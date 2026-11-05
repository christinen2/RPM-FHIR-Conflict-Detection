import random

COMPARATORS = [">", ">=", "<", "<="]


def make_activity_definition(
    activity_id: str,
    observation_code: str,
    comparator: str,
    urgent_value: float,
    asap_gap: float,
    unit: str = "mmHg",
) -> dict:
    """
    Build one valid synthetic ActivityDefinition.

    ASAP is derived from urgent so that the ordering is always valid:

        > / >= : ASAP is above urgent
        < / <= : ASAP is below urgent
    """
    assert comparator in {">", ">=", "<", "<="}
    assert asap_gap >= 0

    if comparator in {">", ">="}:
        asap_value = urgent_value + asap_gap
    else:
        asap_value = urgent_value - asap_gap

    return {
        "resourceType": "ActivityDefinition",
        "id": activity_id,
        "url": f"DINGO/ActivityDefinition/{activity_id}",
        "meta": {
            "profile": [
                "DINGO/StructureDefinition/"
                "activity-definition-threshold-default|1.0.0"
            ]
        },
        "name": activity_id,
        "title": f"Synthetic threshold {activity_id}",
        "status": "active",
        "usage": "threshold-default",
        "intent": "plan",
        "useContext": [
            _make_context(
                priority="urgent",
                comparator=comparator,
                value=urgent_value,
                unit=unit,
            ),
            _make_context(
                priority="asap",
                comparator=comparator,
                value=asap_value,
                unit=unit,
            ),
        ],
        "observationRequirement": [
            {
                "reference": (
                    f"ObservationDefinition/{observation_code}"
                )
            }
        ],
    }


def _make_context(
    priority: str,
    comparator: str,
    value: float,
    unit: str,
) -> dict:
    return {
        "code": {
            "system": "http://hl7.org/fhir/request-priority",
            "code": priority,
        },
        "valueQuantity": {
            "value": value,
            "comparator": comparator,
            "unit": unit,
        },
    }

def make_random_activity_definition(
    activity_id: str,
    observation_code: str,
    rng: random.Random,
) -> dict:
    comparator = rng.choice(COMPARATORS)

    return make_activity_definition(
        activity_id=activity_id,
        observation_code=observation_code,
        comparator=comparator,
        urgent_value=rng.randint(60, 200),
        asap_gap=rng.randint(10, 80),
    )