from enum import Enum
from typing import List, Any, Dict, Tuple
from .constants import PRIORITY_RANK, FALLBACK_RANK
from z3 import Solver, Real, And, Not, unsat, sat
from collections import defaultdict

class ConflictType(Enum):
    NO_CONFLICT = "No Conflict"
    STRICTNESS_FAIL = "Strictness Flag=True -> Fail"
    STRICTNESS_PASS = "Strictness Flag=False -> Pass"
    DIFFERENT_DEFINITION = "Different Definition"
    NO_ACCEPTABLE_RANGE = "No Acceptable Range"
    DEFAULT = "Default"
    WRONG_ORDER = "Wrong Status Order"


THRESHOLD_EXTRACTION_QUERY = """
    PREFIX : <http://prototype/data/>
    PREFIX tmr: <http://tmr#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?act ?actLabel ?obs ?priority ?low ?high ?lowerInclusive ?higherInclusive
    WHERE {
        GRAPH ?g {
            ?act a :ActivityDefinition ;
                rdfs:label ?actLabel ;
                :requiresObservation ?obs ;
                :threshold ?threshold .

            ?threshold a tmr:ThresholdInterval ;
                    :priority ?priority ;
                    :lowerBound ?low ;
                    :upperBound ?high ;
                    :lowerInclusive ?lowerInclusive ;
                    :higherInclusive ?higherInclusive .

            VALUES ?priority { "urgent" "asap" }
        }
    }
"""


def extract_thresholds(graph):
    return list(
        graph.query(THRESHOLD_EXTRACTION_QUERY)
    )


def find_conflicts_z3(by_observation: Dict[str, Any], strict_mode: bool = False) -> List[Dict[str, Any]]:
    conflicts = []

    for obs_uri, activities in by_observation.items():
        if len(activities) < 2:
            continue

        obs_name = obs_uri.split('/')[-1]

        threshold_items = []
        for act_uri, data in activities.items():
            for priority, interval in data["thresholds"].items():
                low = interval["low"]
                high = interval["high"]

                hi_inclusive = interval["hi_inclusive"]
                lo_inclusive = interval["lo_inclusive"]

                if low > high:
                    # TODO: possibly add throw err here?
                    continue

                threshold_items.append({
                    "activity_uri": act_uri,
                    "activity_label": data.get("label", act_uri),
                    "priority": priority,
                    "low": low,
                    "high": high,
                    "lo_inclusive": lo_inclusive,
                    "hi_inclusive": hi_inclusive
                })

        threshold_items.sort(key=lambda item: item["low"])

        candidate_pairs: set[Tuple[str, str]] = set()

        active = []

        for current in threshold_items:
            current_low = current["low"]

            active = [
                previous for previous in active
                if (
                    previous["high"] > current_low
                    or (
                        previous["high"] == current_low
                        and previous["hi_inclusive"]
                        and current["lo_inclusive"]
                    )
                )
            ]

            for previous in active:
                if (
                    previous["activity_uri"]
                    == current["activity_uri"]
                ):
                    continue

                act1_uri = previous["activity_uri"]
                act2_uri = current["activity_uri"]

                pair = tuple(sorted((act1_uri, act2_uri)))
                candidate_pairs.add(pair)

            active.append(current)

        for act1_uri, act2_uri in sorted(candidate_pairs):
            data1 = activities[act1_uri]
            data2 = activities[act2_uri]

            detected_conflicts = compare_activities_z3(
                obs_name=obs_name,
                act1_label=data1.get("label", act1_uri),
                thresholds1=data1["thresholds"],
                act2_label=data2.get("label", act2_uri),
                thresholds2=data2["thresholds"],
                strict_mode=strict_mode
            )

            conflicts.extend(detected_conflicts)

        if has_no_acceptable_range(threshold_items):
            conflicts.append({
                "activity1": "Multiple activities",
                "activity2": "Multiple activities",
                "priority1": "urgent",
                "priority2": "urgent",
                "bounds1": [],
                "bounds2": [],
                "overlap": [],
                "type": ConflictType.NO_ACCEPTABLE_RANGE.value,
                "detail": (
                    "The combined urgent thresholds cover the entire "
                    "measurement range, leaving no acceptable values."
                ),
                "observation": obs_name,
            })

    return conflicts


def has_no_acceptable_range(threshold_items):
    obs_var = Real("measurement")
    solver = Solver()

    if not threshold_items:
        return False

    for interval in threshold_items:
        conditions = interval_constraints(obs_var, interval)
        solver.add(Not(And(*conditions)))

    return solver.check() == unsat


def interval_constraints(obs_var, interval):
    conditions = []

    low = interval["low"]
    high = interval["high"]

    if low != float("-inf"):
        if interval["lo_inclusive"]:
            conditions.append(obs_var >= low)
        else:
            conditions.append(obs_var > low)

    if high != float("inf"):
        if interval["hi_inclusive"]:
            conditions.append(obs_var <= high)
        else:
            conditions.append(obs_var < high)

    return conditions


def compare_activities_z3(
    obs_name: str,
    act1_label: str,
    thresholds1: dict,
    act2_label: str,
    thresholds2: dict,
    strict_mode: bool = False,
) -> list[dict]:

    conflicts = []

    solver = Solver()
    obs_var = Real(f"measurement_{obs_name}")

    for p1, interval1 in thresholds1.items():
        for p2, interval2 in thresholds2.items():

            low1, high1 = interval1["low"], interval1["high"]
            low2, high2 = interval2["low"], interval2["high"]


            cond1 = interval_constraints(obs_var, interval1)
            cond2 = interval_constraints(obs_var, interval2)

            solver.push()
            solver.add(*(cond1 + cond2))
            is_sat = solver.check() == sat
            solver.pop()

            if not is_sat:
                continue

            overlap_start = max(low1, low2)
            overlap_end = min(high1, high2)

            if low1 > low2:
                overlap_low_inclusive = interval1["lo_inclusive"]
            elif low2 > low1:
                overlap_low_inclusive = interval2["lo_inclusive"]
            else:
                overlap_low_inclusive = (
                    interval1["lo_inclusive"]
                    and interval2["lo_inclusive"]
                )

            if high1 < high2:
                overlap_high_inclusive = interval1["hi_inclusive"]
            elif high2 < high1:
                overlap_high_inclusive = interval2["hi_inclusive"]
            else:
                overlap_high_inclusive = (
                    interval1["hi_inclusive"]
                    and interval2["hi_inclusive"]
                )


            rank1 = PRIORITY_RANK.get(p1.lower(), FALLBACK_RANK)
            rank2 = PRIORITY_RANK.get(p2.lower(), FALLBACK_RANK)

            conflict_type = None
            detail = None


            if rank1 == rank2:
                if (
                    low1 != low2
                    or high1 != high2
                    or interval1["lo_inclusive"]
                    != interval2["lo_inclusive"]
                    or interval1["hi_inclusive"]
                    != interval2["hi_inclusive"]
                ):
                    conflict_type = "DIFFERENT_DEFINITION"
                    detail = (
                        f"Mismatched bounds or inclusivity "
                        f"for identical priority '{p1}'"
                    )
            else:
                if rank1 < rank2:
                    higher_interval = interval1
                    lower_interval = interval2
                    higher_priority = p1
                    lower_priority = p2
                else:
                    higher_interval = interval2
                    lower_interval = interval1
                    higher_priority = p2
                    lower_priority = p1

                higher_low = higher_interval["low"]
                lower_low = lower_interval["low"]
                is_staged = higher_low >= lower_low

                if is_staged:
                    conflict_type = ConflictType.STRICTNESS_PASS
                    detail = (
                        f"Higher-priority '{higher_priority}' threshold "
                        f"is at least as restrictive as '{lower_priority}'"
                    )
                else:
                    conflict_type = (
                        ConflictType.STRICTNESS_FAIL.value if strict_mode
                        else ConflictType.NO_CONFLICT.value
                    )
                    detail = (
                        f"Higher-priority '{higher_priority}' threshold "
                        f"is not stricter than '{lower_priority}'"
                    )


            if conflict_type != ConflictType.NO_CONFLICT.value:
                conflicts.append({
                    "activity1": act1_label,
                    "activity2": act2_label,
                    "priority1": p1,
                    "priority2": p2,
                    "bounds1": [low1, high1],
                    "bounds2": [low2, high2],
                    "overlap": [overlap_start, overlap_end],
                    "overlap_low_inclusive": overlap_low_inclusive,
                    "overlap_high_inclusive": overlap_high_inclusive,
                    "type": conflict_type,
                    "detail": detail,
                    "observation": obs_name,
                })

        return conflicts


def group_thresholds(rows):
    by_observation = defaultdict(dict)

    for row in rows:
        observation = str(row.obs)
        activity = str(row.act)
        priority = str(row.priority)
        hi_inclusive = bool(row.higherInclusive.toPython())
        lo_inclusive = bool(row.lowerInclusive.toPython())

        if activity not in by_observation[observation]:
            by_observation[observation][activity] = {
                "label": str(row.actLabel),
                "thresholds": {},
            }

        by_observation[observation][activity]["thresholds"][
            priority
        ] = {
            "low": float(row.low),
            "high": float(row.high),
            "lo_inclusive": lo_inclusive,
            "hi_inclusive": hi_inclusive,
        }

    return by_observation
