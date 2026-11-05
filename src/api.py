from rdflib import Dataset
from .conflict import extract_thresholds, find_conflicts_z3, group_thresholds

from .translate import FHIRToTmrPathATranslator


def get_conflicts(fhir_bundle_json, strict_mode = False):
    translator = FHIRToTmrPathATranslator()
    trig_output = translator.translate_bundle(fhir_bundle_json)
    ds = Dataset()
    ds.parse(data=trig_output, format="trig")

    rows = extract_thresholds(ds)

    by_observation = group_thresholds(rows)

    conflicts = find_conflicts_z3(by_observation, strict_mode=strict_mode)
    return conflicts




def count_resources(bundle):
    entries = bundle.get("entry", [])
            
    plan_definitions = 0
    activity_definitions = 0
    
    for entry in entries:
        resource = entry.get("resource", {})

        match resource.get("resourceType"):
            case "PlanDefinition":
                plan_definitions += 1
            case "ActivityDefinition":
                activity_definitions += 1

    return {
        "plan_defs": plan_definitions,
        "act_defs": activity_definitions
    }