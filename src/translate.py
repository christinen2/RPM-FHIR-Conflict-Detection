from typing import Dict, Any
from rdflib import Dataset, RDFS, XSD
from .constants import EX, TMR
from .resource.interval import Interval
from .resource.plandefinition import PlanDefinition
from .resource.activitydefinition import ActivityDefinition
from .resource.observationdefinition import ObservationDefinition


class FHIRToTmrPathATranslator:
    def process_plan_definition(self, resource):
        id = resource.get("id");
        status = resource.get("status")
        title = resource.get("title")
        actions = resource.get("action")

        return PlanDefinition(id, title, status, actions)
    
    def process_activity_definition(self, resource):
        id = resource.get("id");
        status = resource.get("status");
        url = resource.get("url")
        title = resource.get("title")

        date = resource.get("date")
        usage = resource.get("usage")
        obs_req_list = resource.get("observationRequirement")
        obs_req = None if not obs_req_list else obs_req_list[0].get("reference")

        ranges = []
        thresholds = resource.get("useContext")
        for threshold in thresholds:
            code = threshold.get("code").get("code")
            
            val_qty = threshold.get("valueQuantity")
            comparator = val_qty.get("comparator", ">=")
            value = val_qty.get("value")
            unit = val_qty.get("unit");

            ranges.append({
                "priority": code,
                "comparator": comparator,
                "value": value,
                "unit": unit
            })
        
        ranges.sort(key=lambda x: x["value"])
        processed_intervals = []
        num_milestones = len(ranges)

        for i, milestone in enumerate(ranges):
            current_val = milestone["value"]
            priority = milestone["priority"]
            comparator = milestone["comparator"]
            lo_inclusive = comparator == ">=" or comparator == "<="

            if comparator in ("<", "<="):
                lo_bound = (
                    float("-inf")
                    if i == num_milestones - 1
                    else ranges[i + 1]["value"]
                )
                hi_bound = current_val

                lo_inclusive = (
                    False if i == num_milestones - 1
                    else ranges[i + 1]["comparator"] in (">=", "<=")
                )
                hi_inclusive = comparator == "<="

            else:
                lo_bound = current_val
                hi_bound = (
                    float("inf")
                    if i == num_milestones - 1
                    else ranges[i + 1]["value"]
                )

                lo_inclusive = comparator == ">="
                hi_inclusive = (
                False if i == num_milestones - 1
                else ranges[i + 1]["comparator"] in ("<=", ">")
            )

            processed_intervals.append(
                Interval(
                    lo_bound,
                    hi_bound,
                    lo_inclusive,
                    hi_inclusive,
                    priority,
                    id
                )
            )
        return ActivityDefinition(id, url, status, title, date, usage, obs_req, processed_intervals)


    def process_observation_defintiion(self, resource):
        id = resource.get("id");
        code = resource.get("code", {}).get("code")
        permitted_data = resource.get("permittedDataType")

        qualitative_details = resource.get("qualitativeDetails")
        unit = None
        if qualitative_details:
            unit = qualitative_details.get("coding").get("code");
        
        return ObservationDefinition(id, code, permitted_data, unit)


    def translate_bundle(self, bundle: Dict[str, Any]) -> str:
        entries = bundle.get("entry", [])
        
        plan_definitions = []
        activity_definitions = []
        observation_definitions = []

        for entry in entries:
            resource = entry.get("resource", {})

            match resource.get("resourceType"):
                case "PlanDefinition":
                    plan_definitions.append(self.process_plan_definition(resource))
                case "ActivityDefinition":
                    activity_definitions.append(self.process_activity_definition(resource))
                case "ObservationDefinition":
                    observation_definitions.append(self.process_observation_defintiion(resource))
                case _:
                    pass

        combined_plan_def = PlanDefinition.combine_plan_defs(plan_definitions)

        for ad in activity_definitions:
            ad.add_observation_def(observation_definitions)

        combined_plan_def.add_activity_def(activity_definitions)

        ds = Dataset()
        ds.bind("", EX)
        ds.bind("tmr", TMR)
        ds.bind("rdfs", RDFS)
        ds.bind("xsd", XSD)
        combined_plan_def.to_rdf(ds);

        return ds.serialize(format="trig")
    