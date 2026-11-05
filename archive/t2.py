# from typing import Dict, Any
# from rdflib import Dataset, RDFS, XSD
# from .conflict import extract_candidate_overlaps, get_conflict_report, extract_thresholds, find_conflicts_z3
# from .constants import EX, TMR
# from .resource.interval import Interval
# from .resource.plandefinition import PlanDefinition
# from .resource.activitydefinition import ActivityDefinition
# from .resource.observationdefinition import ObservationDefinition
# from collections import defaultdict

# def has_no_conflicts(fhir_bundle_json, strict_mode = True):
#     translator = FHIRToTmrPathATranslator()
#     trig_output = translator.translate_bundle(fhir_bundle_json)
#     ds = Dataset()
#     ds.parse(data=trig_output, format="trig")

#     overlaps = extract_candidate_overlaps(ds);
#     report = get_conflict_report(overlaps, strict_mode);

#     return len(report) == 0


# def has_no_conflicts(fhir_bundle_json, strict_mode = True):
#     translator = FHIRToTmrPathATranslator()
#     trig_output = translator.translate_bundle(fhir_bundle_json)
#     ds = Dataset()
#     ds.parse(data=trig_output, format="trig")

#     overlaps = extract_candidate_overlaps(ds);
#     report = get_conflict_report(overlaps, strict_mode);

#     return len(report) == 0