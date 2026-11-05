from enum import Enum
from rdflib import Dataset
from typing import List, Any, Dict, Tuple
from itertools import combinations
# from .constants import PRIORITY_RANK, FALLBACK_RANK
from z3 import Solver, Real, And, Not, unsat, sat

# TODO: better messages
class ConflictType(Enum):
    NO_CONFLICT = "No Conflict"
    STRICTNESS_FAIL = "Strictness Flag=True -> Fail"
    STRICTNESS_PASS = "Strictness Flag=False -> Pass"
    DIFFERENT_DEFINITION = "Different ranges"
    NO_ACCEPTABLE_RANGE = "No Acceptable Range"
    DEFAULT = "default"
    WRONG_ORDER = "status order wrong"



def extract_candidate_overlaps(ds: Dataset) -> List[Any]:
    s2 = '''
PREFIX : <http://prototype/data/>
PREFIX tmr: <http://tmr#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT
    ?act1Label ?priority1 ?low1 ?high1
    ?act2Label ?priority2 ?low2 ?high2
    ?overlapStart ?overlapEnd
WHERE {
    GRAPH ?g {

        VALUES ?priority1 { "urgent" "asap" }
        VALUES ?priority2 { "urgent" "asap" }

        ?act1 a :ActivityDefinition ;
              rdfs:label ?act1Label ;
              :requiresObservation ?obs ;
              :threshold ?t1 .

        ?t1 a tmr:ThresholdInterval ;
            :priority ?priority1 ;
            :lowerBound ?low1 ;
            :upperBound ?high1 .

        ?act2 a :ActivityDefinition ;
              rdfs:label ?act2Label ;
              :requiresObservation ?obs ;
              :threshold ?t2 .

        ?act2 :threshold ?t2 .

        ?t2 a tmr:ThresholdInterval ;
            :priority ?priority2 ;
            :lowerBound ?low2 ;
            :upperBound ?high2 .

        FILTER (?act1 != ?act2)
        FILTER (STR(?act1) < STR(?act2))

        FILTER (
            ?low1 < ?high2 &&
            ?high1 > ?low2
        )

        BIND(
            IF(?low1 > ?low2, ?low1, ?low2)
            AS ?overlapStart
        )

        BIND(
            IF(?high1 < ?high2, ?high1, ?high2)
            AS ?overlapEnd
        )
    }
}
'''

    return ds.query(s2)

def get_conflict_report(overlaps: list, strict_mode) -> int:
    reports = []
    for row in overlaps:
        classification = classify_threshold_conflict(row, strict_mode)

        if classification["type"] == ConflictType.NO_CONFLICT:
            continue
        elif classification["type"] == ConflictType.STRICTNESS_PASS and not strict_mode:
            continue

        reports.append({
            "activity_1": str(row.act1Label),
            "activity_2": str(row.act2Label),
            "priority_1": str(row.priority1),
            "priority_2": str(row.priority2),
            "range_1": f"[{float(row.low1)}, {float(row.high1)}]",
            "range_2": f"[{float(row.low2)}, {float(row.high2)}]",
            "conflict_type": classification["type"].value,
            "description": classification["detail"]
        })

    return reports


def classify_threshold_conflict(row: Any, strict_mode: bool = True) -> Dict[str, Any]:
    """
    Classifies an overlapping candidate pair into one of the 5 defined conflict types.
    """
    low1, high1 = float(row.low1), float(row.high1)
    low2, high2 = float(row.low2), float(row.high2)
    p1 = str(row.priority1).lower()
    p2 = str(row.priority2).lower()
    
    # priority hierarchy (NOTE: assumption made here!!! - only urgent/asap)
    priority_rank = {"urgent": 1, "asap": 2}
    rank1 = priority_rank.get(p1, 1)
    rank2 = priority_rank.get(p2, 1)

    overlap_start = max(low1, low2)
    overlap_end = min(high1, high2)


    is_low_starting = min(low1, low2) <= 20.0
    is_unbounded_high = max(high1, high2) >= 1.0e300

    ranges_touch_or_overlap = max(low1, low2) <= min(high1, high2)

    if is_low_starting and is_unbounded_high and ranges_touch_or_overlap:
            return {
                "type": ConflictType.NO_ACCEPTABLE_RANGE,
                "detail": (
                    f"Entire threshold spectrum from {min(low1, low2)} to +INF is "
                    f"saturated by high-urgency triggers ('{p1}' / '{p2}')."
                )
            }


    # -------------------------------------------------------------
    # RULE 2: No Conflict (Complementary / Adjoining Ranges)
    # Upper bound of one meets lower bound of another cleanly
    # -------------------------------------------------------------
    if high1 <= low2 or high2 <= low1:
        return {
            "type": ConflictType.NO_CONFLICT,
            "detail": f"Ranges touch or meet at boundary {high1} without an overlapping internal region."
        }


    if rank1 != rank2:
        # Check if higher cutoff has higher priority (Staged Escalation)
        is_staged = (low1 < low2 and rank1 < rank2) or (low2 < low1 and rank2 < rank1)
        if is_staged:
            if strict_mode:
                return {
                    "type": ConflictType.STRICTNESS_FAIL,
                    "detail": f"Priority discrepancy above {overlap_start}: Act1 specifies '{p1}' while Act2 specifies '{p2}'."
                }
            else:
                higher_p = p2 if rank2 > rank1 else p1
                return {
                    "type": ConflictType.STRICTNESS_PASS,
                    "detail": f"Non-strict mode: '{higher_p}' supersedes lower priority above {overlap_start}."
                }


        is_high_spectrum = max(high1, high2) >= 1.0e300
        
        if is_high_spectrum:
            if low1 <= low2:
                milder_act, milder_p, milder_rank = row.act1Label, p1, rank1
                severe_act, severe_p, severe_rank = row.act2Label, p2, rank2
                milder_val, severe_val = low1, low2
            else:
                milder_act, milder_p, milder_rank = row.act2Label, p2, rank2
                severe_act, severe_p, severe_rank = row.act1Label, p1, rank1
                milder_val, severe_val = low2, low1

         
        else:
            if high1 >= high2:
                milder_act, milder_p, milder_rank = row.act1Label, p1, rank1
                severe_act, severe_p, severe_rank = row.act2Label, p2, rank2
                milder_val, severe_val = high1, high2
            else:
                milder_act, milder_p, milder_rank = row.act2Label, p2, rank2
                severe_act, severe_p, severe_rank = row.act1Label, p1, rank1
                milder_val, severe_val = high2, high1

        if milder_rank > severe_rank and milder_val != severe_val:
            return {
                "type": ConflictType.WRONG_ORDER,
                "detail": (
                    f"Inverted priority order: Higher urgency '{milder_p}' ({milder_act}) "
                    f"triggers at milder threshold ({milder_val}) than lower urgency '{severe_p}' "
                    f"({severe_act}) at {severe_val}."
                )
            }


    
    if p1 == p2 and (low1 != low2 or high1 != high2):
        return {
            "type": ConflictType.DIFFERENT_DEFINITION,
            "detail": f"Mismatched threshold definition for priority '{p1}': Act1 starts at {low1}, Act2 starts at {low2}."
        }

    return {
        "type": ConflictType.NO_CONFLICT,
        "detail": "fallback"
    }



def find_conflicts(by_observation):
    conflicts = []

    for observation, activities in by_observation.items():
        if len(activities) < 2:
            continue

        for (act1, data1), (act2, data2) in combinations(
            activities.items(),
            2,
        ):
            conflicts.extend(
                compare_activities(
                    observation,
                    act1,
                    data1,
                    act2,
                    data2,
                )
            )

    return conflicts


def compare_activities(
    observation,
    act1,
    data1,
    act2,
    data2,
    strict_mode=False,
):
    conflicts = []

    thresholds1 = data1["thresholds"]
    thresholds2 = data2["thresholds"]

    for p1, interval1 in thresholds1.items():
        for p2, interval2 in thresholds2.items():

            low1 = interval1["low"]
            high1 = interval1["high"]

            low2 = interval2["low"]
            high2 = interval2["high"]

            # No overlap
            if not (low1 < high2 and high1 > low2):
                continue

            overlap_start = max(low1, low2)
            overlap_end = min(high1, high2)

            rank1 = PRIORITY_RANK[p1]
            rank2 = PRIORITY_RANK[p2]

            if rank1 == rank2:
                continue

            is_staged = (
                (low1 < low2 and rank1 < rank2)
                or
                (low2 < low1 and rank2 < rank1)
            )

            if is_staged:
                if strict_mode:
                    conflict_type = ConflictType.STRICTNESS_FAIL
                    detail = (
                        f"Priority discrepancy above {overlap_start}: "
                        f"Act1 specifies '{p1}' while Act2 specifies '{p2}'."
                    )
                else:
                    higher_p = p2 if rank2 > rank1 else p1

                    conflict_type = ConflictType.STRICTNESS_PASS
                    detail = (
                        f"Non-strict mode: '{higher_p}' supersedes "
                        f"lower priority above {overlap_start}."
                    )

            else:
                conflict_type = ConflictType.DIFFERENT_DEFINITION
                detail = (
                    f"Conflicting priorities over "
                    f"{overlap_start}-{overlap_end}: "
                    f"Act1 specifies '{p1}' while "
                    f"Act2 specifies '{p2}'."
                )

            conflicts.append(
                {
                    "type": conflict_type,
                    "observation": observation,

                    "activity1": act1,
                    "activity1_label": data1["label"],
                    "priority1": p1,
                    "low1": low1,
                    "high1": high1,

                    "activity2": act2,
                    "activity2_label": data2["label"],
                    "priority2": p2,
                    "low2": low2,
                    "high2": high2,

                    "overlap_start": overlap_start,
                    "overlap_end": overlap_end,

                    "detail": detail,
                }
            )

    return conflicts
