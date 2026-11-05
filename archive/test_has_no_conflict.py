# from src.t2 import has_no_conflicts
# import json
# from pathlib import Path

# '''
# THIS USES THE OLD FUNCTION WHICH USES THE SPARQL QUERY. PERFORMANCE FOR MANY
# ACTIVITES IS NOT THAT GOOD SO USING THE NEW GET_CONFLICTS FUNCTION NOW INSTEAD.
# '''

# current_dir = Path(__file__).parent

# # ONE PLAN DEF TESTS - VALIATES THE PLAN DEF
# def test_no_conflicts_no_shared_obs_def():
#     json_path = current_dir / "fhir" / "single_plan_no_shared_obs.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(has_no_conflicts(data))


# def test_no_conflicts_shared_obs_def():
#     json_path = current_dir / "fhir" / "single_plan_no_conflict_shared_obs.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(has_no_conflicts(data))

# def test_conflicts_threshold_overlap():
#     json_path = current_dir / "fhir" / "single_plan_threshold_overlap.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(not has_no_conflicts(data))

# # MULTIPLE PLAN DEFINITIONS
# def test_multiple_plan_def_no_shared_obs_def():
#     json_path = current_dir / "fhir" / "mult_plan_no_shared_obs_def.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(has_no_conflicts(data))

# def test_multiple_plan_def_shared_obs_def_no_overlap():
#     json_path = current_dir / "fhir" / "mult_plan_no_conflict_shared_obs_def.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(has_no_conflicts(data))

# def test_multiple_plan_def_threshold_overlap():
#     json_path = current_dir / "fhir" / "mult_plan_threshold_conflict.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(not has_no_conflicts(data))

# def test_mutiple_plan_def_no_valid_value():
#     json_path = current_dir / "fhir" / "mult_plan_no_valid.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(has_no_conflicts(data))

# def test_multiple_plan_different_definition():
#     json_path = current_dir / "fhir" / "mult_plan_different_definition.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(not has_no_conflicts(data))

# def test_multiple_plan_wrong_order_status():
#     json_path = current_dir / "fhir" / "mult_plan_wrong_order_status.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(not has_no_conflicts(data))

# def test_multiple_plan_strictness_additive_threshold():
#     json_path = current_dir / "fhir" / "mult_plan_additive_threshold.json"
#     with open(json_path) as f:
#         data = json.load(f)
#         assert(not has_no_conflicts(data, True))
#         assert(has_no_conflicts(data, False))



