def make_plan_definition(
    plan_id: str,
    activity_ids: list[str],
) -> dict:
    actions = []

    for i, activity_id in enumerate(activity_ids):
        actions.append(
            {
                "id": f"action-{i}",
                "title": f"Synthetic-action-{i}",
                "definitionCanonical": (
                    f"DINGO/ActivityDefinition/{activity_id}"
                ),
            }
        )

    return {
        "resourceType": "PlanDefinition",
        "id": plan_id,
        "url": f"DINGO/PlanDefinition/{plan_id}",
        "name": plan_id,
        "title": f"Synthetic-plan {plan_id}",
        "status": "active",
        "action": actions,
    }