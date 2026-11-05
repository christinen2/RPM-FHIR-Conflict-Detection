import random
from .activitydefinition import make_activity_definition, make_random_activity_definition
from .plandefinition import make_plan_definition

OBSERVATION = "SYNTHETIC_EXAMPLE"

def no_conflict_dataset(
    plan_count: int,
    activities_per_plan: int,
) -> dict:
    """
    Multiple PlanDefinitions with identical compatible thresholds.

    Expected conflicts: 0.
    """
    plans = []
    activities = []

    for plan_index in range(plan_count):
        plan_activities = []
        # observation_code = f"OBSERVATION_PLAN_{plan_index}"

        for activity_index in range(activities_per_plan):
            activity_id = (
                f"PLAN-{plan_index}-ACTIVITY-{activity_index}"
            )

            activity = make_activity_definition(
                activity_id=activity_id,
                observation_code=OBSERVATION,
                # observation_code=observation_code,
                comparator=">=",
                urgent_value=100,
                asap_gap=80,
            )

            activities.append(activity)
            plan_activities.append(activity)

        plans.append(
            make_plan_definition(
                plan_id=f"PLAN-{plan_index}",
                activity_ids=[
                    activity["id"]
                    for activity in plan_activities
                ],
            )
        )

    return _make_bundle(
        plans=plans,
        activities=activities,
    )


def dense_conflict_dataset(
    plan_count: int,
    activities_per_plan: int,
) -> dict:
    """
    Produce many PlanDefinitions whose thresholds oppose each other.

    Even numbered plans:
        urgent >= 120
        asap   >= 180

    Odd numbered plans:
        urgent < 100
        asap   < 80

    All activities target the same observation.

    This creates a high-conflict workload between plans.
    """
    plans = []
    activities = []

    for plan_index in range(plan_count):

        if plan_index % 2 == 0:
            comparator = ">="
            urgent_value = 120
            asap_gap = 60
        else:
            comparator = "<"
            urgent_value = 100
            asap_gap = 20

        plan_activities = []

        for activity_index in range(activities_per_plan):
            activity_id = (
                f"PLAN-{plan_index}-ACTIVITY-{activity_index}"
            )

            activity = make_activity_definition(
                activity_id=activity_id,
                observation_code=OBSERVATION,
                comparator=comparator,
                urgent_value=urgent_value,
                asap_gap=asap_gap,
            )

            activities.append(activity)
            plan_activities.append(activity)

        plans.append(
            make_plan_definition(
                plan_id=f"PLAN-{plan_index}",
                activity_ids=[
                    activity["id"]
                    for activity in plan_activities
                ],
            )
        )

    return _make_bundle(
        plans=plans,
        activities=activities,
    )


def same_observation_dataset(
    plan_count: int,
    activities_per_plan: int,
    seed: int = 42,
) -> dict:
    """
    Random thresholds, but every ActivityDefinition in every
    PlanDefinition targets the same ObservationDefinition.

    This is useful as a stress test because nearly everything
    is potentially comparable.
    """
    rng = random.Random(seed)

    plans = []
    activities = []

    for plan_index in range(plan_count):
        plan_activities = []

        for activity_index in range(activities_per_plan):
            activity_id = (
                f"PLAN-{plan_index}-ACTIVITY-{activity_index}"
            )

            activity = make_random_activity_definition(
                activity_id=activity_id,
                observation_code=OBSERVATION,
                rng=rng,
            )

            activities.append(activity)
            plan_activities.append(activity)

        plans.append(
            make_plan_definition(
                plan_id=f"PLAN-{plan_index}",
                activity_ids=[
                    activity["id"]
                    for activity in plan_activities
                ],
            )
        )

    return _make_bundle(
        plans=plans,
        activities=activities,
    )


def random_dataset(
    plan_count: int,
    activities_per_plan: int,
    observation_count: int = 10,
    seed: int = 42,
) -> dict:
    """
    More realistic mixed workload.

    - multiple PlanDefinitions
    - multiple ActivityDefinitions per plan
    - thresholds are randomly generated
    - activities are distributed across observations
    """
    assert observation_count > 0

    rng = random.Random(seed)

    plans = []
    activities = []

    global_activity_index = 0

    for plan_index in range(plan_count):
        plan_activities = []

        for activity_index in range(activities_per_plan):
            activity_id = (
                f"PLAN-{plan_index}-ACTIVITY-{activity_index}"
            )

            observation_code = (
                f"OBS-{global_activity_index % observation_count}"
            )

            activity = make_random_activity_definition(
                activity_id=activity_id,
                observation_code=observation_code,
                rng=rng,
            )

            activities.append(activity)
            plan_activities.append(activity)

            global_activity_index += 1

        plans.append(
            make_plan_definition(
                plan_id=f"PLAN-{plan_index}",
                activity_ids=[
                    activity["id"]
                    for activity in plan_activities
                ],
            )
        )

    return _make_bundle(
        plans=plans,
        activities=activities,
    )


def _make_bundle(
    plans: list[dict],
    activities: list[dict],
) -> dict:
    """
    Build one FHIR transaction Bundle containing all
    PlanDefinitions and ActivityDefinitions.
    """

    entries = []

    for plan in plans:
        entries.append(
            _make_bundle_entry(plan)
        )

    for activity in activities:
        entries.append(
            _make_bundle_entry(activity)
        )

    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": entries,
    }


def _make_bundle_entry(
    resource: dict,
) -> dict:
    resource_type = resource["resourceType"]
    resource_id = resource["id"]

    return {
        "fullUrl": (
            f"DINGO/{resource_type}/{resource_id}"
        ),
        "request": {
            "method": "PUT",
            "url": (
                f"{resource_type}/{resource_id}"
            ),
        },
        "resource": resource,
    }