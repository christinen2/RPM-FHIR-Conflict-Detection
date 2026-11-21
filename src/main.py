#!/usr/bin/env python3

from .api import FHIRToTmrPathATranslator, group_thresholds
from rdflib import Dataset
import json
from .conflict import extract_thresholds, find_conflicts_z3


# For manual testing purposes
if __name__ == "__main__":
    input_file = "./tests/fhir/single_plan_no_shared_obs.json"




    # input_file = "./demo/pres_plans/unrelated.json"
    output_file = "./demo/pres_plans/unrelated.trig"


    with open(input_file) as f:
        data = json.load(f)

        translator = FHIRToTmrPathATranslator()

        trig_output = translator.translate_bundle(data)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(trig_output)


        ds = Dataset()
        ds.parse(output_file, format="trig")


        
        overlaps = extract_thresholds(ds)
        by_obs = group_thresholds(overlaps)
        conflicts = find_conflicts_z3(by_obs, True)

        

        print(conflicts)
        
        print(len(conflicts))
        if not conflicts:
            print("no conflicts")