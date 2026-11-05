#!/usr/bin/env python3

import json
from typing import Dict, Any
from rdflib import Dataset, Literal, Namespace, RDF, RDFS, XSD, BNode

# NOTE =========================================================================
# TODO: could do an assert for status since they should(?) all be active

# NOTE: lots of assumptions that all the resources have all the expected fields. Will not handle errors gracefully atm

# NOTE: assumption: use context consistently uses the same operator for each context

# TODO: making the output more human readable, need to say what conflcit it is instead of true/false
# TODO: single threshold conflict can cause 4 separate detected issues, need to combine to one

# TODO: figure out what to do with the 'group' resource
# TODO: observation definition currently not using unit or permittedData, activityDefinition not using timingTiming

# GLOBAL VAR ===================================================================
EX = Namespace("http://prototype/data")
TMR = Namespace("http://tmr")



# RESOURCE CLASSES ===============================================================
class Interval:
    def __init__(self, lo, hi, lo_inclusive, hi_inclusive, priority):
        self.lo = lo
        self.hi = hi
        self.lo_inclusive = lo_inclusive
        self.hi_inclusive = hi_inclusive
        self.priority = priority
    
    def to_rdf(self, graph):
        interval_node = BNode()
        graph.add((interval_node, RDF.type, TMR.ThresholdInterval))
        graph.add((interval_node, EX.lowerBound, Literal(self.lo, datatype=XSD.double)))
        graph.add((interval_node, EX.upperBound, Literal(self.hi, datatype=XSD.double)))
        graph.add((interval_node, EX.lowerInclusive, Literal(self.lo_inclusive, datatype=XSD.boolean)))
        graph.add((interval_node, EX.higherInclusive, Literal(self.hi_inclusive, datatype=XSD.boolean)))
        graph.add((interval_node, EX.priority, Literal(self.priority)))
        return interval_node

    # debug functions
    def __str__(self) -> str:
        left_bracket = "[" if self.lo_inclusive else "("
        right_bracket = "]" if self.hi_inclusive else ")"
        return (
            f"Interval{left_bracket}{self.lo}, {self.hi}{right_bracket} "
            f"priority='{self.priority}'"
        )

    def __repr__(self) -> str:
        return (
            f"Interval(lo={self.lo}, hi={self.hi}, "
            f"lo_inclusive={self.lo_inclusive}, hi_inclusive={self.hi_inclusive}, "
            f"priority='{self.priority}')"
        )
        

class Action:
    def __init__(self, title, act_def, timing):
        self.title = title
        self.act_def = act_def
        self.timing = timing

    def to_rdf(self, graph):
        action_node = EX[f"Action_{self.title}"]
        graph.add((action_node, RDF.type, EX.Action))
        graph.add((action_node, RDFS.label, Literal(self.title)))

        if self.act_def:
            ad_node = self.act_def.to_rdf(graph)
            graph.add((action_node, EX.activityDefinition, ad_node))
        
        if self.timing:
            repeat_data = self.timing.get("repeat", {})
            timing_node = BNode()
            graph.add((action_node, EX.hasTiming, timing_node))
            graph.add((timing_node, RDF.type, EX.Timing))
            
            # assumes it has everything
            frequency = repeat_data.get("frequency")
            period = repeat_data.get("period")
            period_unit = repeat_data.get("periodUnit")

            graph.add((timing_node, EX.frequency, Literal(frequency, datatype=XSD.integer)))
            graph.add((timing_node, EX.period, Literal(period, datatype=XSD.decimal)))
            graph.add((timing_node, EX.periodUnit, Literal(period_unit, Literal(period_unit))))
        
        return action_node
    
    # debug
    def __str__(self) -> str:
        act_def_str = str(self.act_def) if self.act_def else "None"
        timing_str = f"Timing({self.timing})" if self.timing else "None"
        return f"Action(title='{self.title}', activity_def='{act_def_str}', timing={timing_str})"

    def __repr__(self) -> str:
        return f"Action(title={self.title!r}, act_def={self.act_def!r}, timing={self.timing!r})"


class PlanDefinition:
    def __init__(self, id, title, status, actions):
        self.id = id
        self.title = title
        self.staus = status
        self.action_refs = actions
        self.actions = []

    def add_activity_def(self, ads):
        for action_ref in self.action_refs:
            act_def = next((y for y in ads if y.url == action_ref.get("definitionCanonical")), None)
            title = action_ref.get("title")
            timing = action_ref.get("timingTiming")
            action_obj = Action(title, act_def, timing)
            self.actions.append(action_obj)

    def to_rdf(self, dataset):
        graph_uri = EX[f"graph_{self.id}"]
        graph = dataset.graph(graph_uri)

        pd_node = EX[f"self.id"]
        graph.add(
            (
                pd_node, RDF.type, EX.Guideline
            )
        )

        graph.add((pd_node, RDFS.label, Literal(self.title)))
        graph.add((pd_node, EX.status, Literal(self.staus)))

        for action in self.actions:
            action_node = action.to_rdf(graph)
            graph.add((pd_node, EX.hasAction, action_node))

        return graph
    
    # debug
    def __str__(self) -> str:
        actions_formatted = "\n  ".join(
            str(action) for action in self.actions
        )
        return (
            f"PlanDefinition ID: '{self.id}'\n"
            f"Title: '{self.title}'\n"
            f"Status: '{self.staus}'\n"
            f"Actions ({len(self.actions)}):\n  {actions_formatted if actions_formatted else 'None'}"
        )

    def __repr__(self) -> str:
        return f"PlanDefinition(id={self.id!r}, title={self.title!r}, status={self.staus!r}, actions={self.actions!r})"


class ActivityDefinition:
    def __init__(self, id, url, status, title, date, usage, obs_req, thresholds):
        self.id = id
        self.url = url
        self.status = status
        self.title = title
        self.date = date
        self.usage = usage
        self.obs_req_ref = obs_req                                  # example: "ObservationDefinition/MDC-DEV-SPEC-PROFILE-SCALE"
        self.thresholds = thresholds
        self.obs_req = None
    
    def add_observation_def(self, ods):
        for od in ods:
            if self.obs_req_ref == f"ObservationDefinition/{od.id}":
                self.obs_req = od
                return

    def to_rdf(self, graph):
        ad_node = EX[f"ActivityDefinition_{self.id}"]
        graph.add((ad_node, RDF.type, EX.ActivityDefinition))
        graph.add((ad_node, RDFS.label, Literal(self.title)))

        if self.obs_req:
            obs_node = self.obs_req.to_rdf(graph)
            graph.add((ad_node, EX.requiresObservation, obs_node))

        for interval in self.thresholds:
            interval_node = interval.to_rdf(graph)
            graph.add((ad_node, EX.threshold, interval_node))
        
        return ad_node
    
    # debug
    def __str__(self) -> str:
        intervals_str = "\n  ".join(str(t) for t in self.thresholds)
        obs_str = self.obs_req.id if self.obs_req else self.obs_req_ref
        return (
            f"ActivityDefinition ID: '{self.id}'\n"
            f"Title: '{self.title}'\n"
            f"Observation Req: {obs_str}\n"
            f"Thresholds ({len(self.thresholds)}):\n  {intervals_str if intervals_str else 'None'}"
        )

    def __repr__(self) -> str:
        return f"ActivityDefinition(id={self.id!r}, title={self.title!r}, status={self.status!r}, thresholds={self.thresholds!r})"
    


class ObservationDefinition:
    def __init__(self, id, code, permitted_data, unit):
        self.id = id
        self.code = code
        self.permitted_data = permitted_data # TODO: what is this
        self.unit = unit        # TODO: find example
    
    def to_rdf(self, graph):
        od_node = EX[f"ActivityDefinition_{self.id}"]
        graph.add((od_node, RDF.type, EX.ObservationDefinition))
        graph.add((od_node, RDFS.label, Literal(self.id)))

        # TODO: permitted data and unit
        return od_node

    # debug
    def __str__(self) -> str:
        return f"ObservationDefinition(id='{self.id}', code='{self.code}', data_type='{self.permitted_data}', unit='{self.unit}')"

    def __repr__(self) -> str:
        return f"ObservationDefinition(id={self.id!r}, code={self.code!r}, permitted_data={self.permitted_data!r}, unit={self.unit!r})"
    
# TRANSLATION CLASSES ===============================================================


class FHIRToTmrPathATranslator:
    def __init__(self):
        pass

    def process_plan_definition(self, resource):

        id = resource.get("id");
        status = resource.get("status")
        title = resource.get("title")
        actions = resource.get("action")
    
        # actions is a list of objects. Some objects contain a timingTiming. All action objects
        # contains definition cannoical and title
        # To parse later... (parse int he actual class)
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
        # NOTE ignoring effective period

        # getting thresholds
        # ASSUMPTION: context list uses the same comparator for each entry (to prevent creating dead zone)
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

            if comparator == "<" or comparator == "<=":
                hi_bound = current_val
                lo_bound = float('-inf') if i == 0 else ranges[i - 1]["value"]

                processed_intervals.append(Interval(lo_bound, hi_bound, lo_inclusive, not lo_inclusive, priority))
            else:
                lo_bound = current_val
                hi_bound = float('inf') if i >= (num_milestones - 1)  else ranges[i + 1]["value"]

                processed_intervals.append(Interval(lo_bound, hi_bound, lo_inclusive, not lo_inclusive, priority))
        
        return ActivityDefinition(id, url, status, title, date, usage, obs_req, processed_intervals)


    def process_observation_defintiion(self, resource):
        id = resource.get("id");
        code = resource.get("code", {}).get("code")
        permitted_data = resource.get("permittedDataType") # NOTE: from sample, it's either quantity or sample data - need to check

        # qualitative details is optional
        qualitative_details = resource.get("qualitativeDetails") # contains the unit only it seems
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
                    # ignore groups for now
                
        # link the observation defintions to the activity definitions
        for ad in activity_definitions:
            ad.add_observation_def(observation_definitions)
        
        # link activity definitions to plan definitions
        for pd in plan_definitions:
            pd.add_activity_def(activity_definitions)

        # DEBUG
        # print(pd)

        ds = Dataset()
        ds.bind("", EX)
        ds.bind("tmr", TMR)
        ds.bind("rdfs", RDFS)
        ds.bind("xsd", XSD)

        for pd in plan_definitions:
            pd.to_rdf(ds);

        return ds.serialize(format="trig")


def look_for_conflicts(ds):
    # sparql = """
    # PREFIX : <http://prototype/data>
    # PREFIX tmr: <http://tmr>
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    # SELECT ?conditionLabel ?priority ?lowerBound ?lowerInclusive ?upperBound ?higherInclusive
    # WHERE {
    # GRAPH ?g {
    #     ?actDef a :ActivityDefinition ;
    #             rdfs:label ?conditionLabel ;
    #             :threshold ?interval .

    #     # Filter specifically for Hypertension and Hypotension
    #     FILTER(?conditionLabel IN ("Hypertension", "Hypotension"))

    #     ?interval a tmr:ThresholdInterval ;
    #             :lowerBound ?lowerBound ;
    #             :lowerInclusive ?lowerInclusive ;
    #             :upperBound ?upperBound ;
    #             :higherInclusive ?higherInclusive ;
    #             :priority ?priority .
    # }
    # }
    # ORDER BY ?conditionLabel ?lowerBound
    # """


    sparql = """
 
    PREFIX : <http://prototype/data>
PREFIX tmr: <http://tmr>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?act1Label ?priority1 ?low1 ?high1 ?act2Label ?priority2 ?low2 ?high2
WHERE {
  GRAPH ?g {
    # Match Activity 1
    ?act1 a :ActivityDefinition ;
          rdfs:label ?act1Label ;
          :requiresObservation ?obs ;
          :threshold ?t1 .

    ?t1 a tmr:ThresholdInterval ;
        :priority ?priority1 ;
        :lowerBound ?rawLow1 ;
        :upperBound ?rawHigh1 ;
        :lowerInclusive ?incLow1 ;
        :higherInclusive ?incHigh1 .

    # Match Activity 2
    ?act2 a :ActivityDefinition ;
          rdfs:label ?act2Label ;
          :requiresObservation ?obs ;
          :threshold ?t2 .

    ?t2 a tmr:ThresholdInterval ;
        :priority ?priority2 ;
        :lowerBound ?rawLow2 ;
        :upperBound ?rawHigh2 ;
        :lowerInclusive ?incLow2 ;
        :higherInclusive ?incHigh2 .

    FILTER (?act1 != ?act2)
    FILTER (STR(?act1) < STR(?act2))

    # Convert literal representations safely
    BIND(IF(STR(?rawLow1) = "-INF", -1.0e308, xsd:double(STR(?rawLow1))) AS ?low1)
    BIND(IF(STR(?rawHigh1) = "INF", 1.0e308, xsd:double(STR(?rawHigh1))) AS ?high1)
    
    BIND(IF(STR(?rawLow2) = "-INF", -1.0e308, xsd:double(STR(?rawLow2))) AS ?low2)
    BIND(IF(STR(?rawHigh2) = "INF", 1.0e308, xsd:double(STR(?rawHigh2))) AS ?high2)

    # Interval Intersection
    FILTER (?low1 < ?high2 && ?low2 < ?high1)
  }
}
    """


    sparql = """
PREFIX : <http://prototype/data>
PREFIX tmr: <http://tmr>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?plan1Label ?act1Label ?p1 ?low1 ?high1 ?plan2Label ?act2Label ?p2 ?low2 ?high2
WHERE {
  # --- Action 1 Branch ---
  {
    GRAPH ?g1 {
      ?gnode1 a :Guideline ; rdfs:label ?plan1Label ; :hasAction ?action1 .
      ?action1 :activityDefinition ?act1 .
      ?act1 rdfs:label ?act1Label ; :threshold ?t1 .
      ?t1 a tmr:ThresholdInterval ; :priority ?p1 ; :lowerBound ?rawLow1 ; :upperBound ?rawHigh1 .
    }
  } UNION {
    ?gnode1 a :Guideline ; rdfs:label ?plan1Label ; :hasAction ?action1 .
    ?action1 :activityDefinition ?act1 .
    ?act1 rdfs:label ?act1Label ; :threshold ?t1 .
    ?t1 a tmr:ThresholdInterval ; :priority ?p1 ; :lowerBound ?rawLow1 ; :upperBound ?rawHigh1 .
  }

  # --- Action 2 Branch ---
  {
    GRAPH ?g2 {
      ?gnode2 a :Guideline ; rdfs:label ?plan2Label ; :hasAction ?action2 .
      ?action2 :activityDefinition ?act2 .
      ?act2 rdfs:label ?act2Label ; :threshold ?t2 .
      ?t2 a tmr:ThresholdInterval ; :priority ?p2 ; :lowerBound ?rawLow2 ; :upperBound ?rawHigh2 .
    }
  } UNION {
    ?gnode2 a :Guideline ; rdfs:label ?plan2Label ; :hasAction ?action2 .
    ?action2 :activityDefinition ?act2 .
    ?act2 rdfs:label ?act2Label ; :threshold ?t2 .
    ?t2 a tmr:ThresholdInterval ; :priority ?p2 ; :lowerBound ?rawLow2 ; :upperBound ?rawHigh2 .
  }

  # --- DISAMBIGUATE BY ACTION OR GUIDELINE LABEL ---
  # Ensures we don't compare Action1 to Action1, while allowing cross-plan or multi-graph matching
  FILTER (STR(?action1) < STR(?action2))

  # --- NUMERIC & INF PARSING ---
  BIND(IF(isNumeric(?rawLow1), xsd:double(?rawLow1), xsd:double(STR(?rawLow1))) AS ?low1)
  BIND(
    IF(CONTAINS(STR(?rawHigh1), "INF"), 1.0e308,
      IF(isNumeric(?rawHigh1), xsd:double(?rawHigh1), xsd:double(STR(?rawHigh1)))
    ) AS ?high1
  )

  BIND(IF(isNumeric(?rawLow2), xsd:double(?rawLow2), xsd:double(STR(?rawLow2))) AS ?low2)
  BIND(
    IF(CONTAINS(STR(?rawHigh2), "INF"), 1.0e308,
      IF(isNumeric(?rawHigh2), xsd:double(?rawHigh2), xsd:double(STR(?rawHigh2)))
    ) AS ?high2
  )

  # --- INTERVAL OVERLAP FORMULA ---
  FILTER (?low1 < ?high2 && ?low2 < ?high1)
}
    """

    return ds.query(sparql)


def has_no_conflicts(fhir_bundle_json):
    translator = FHIRToTmrPathATranslator()
    trig_output = translator.translate_bundle(fhir_bundle_json)
    ds = Dataset()
    ds.parse(data=trig_output, format="trig")
    conflicts = look_for_conflicts(ds)
    print(conflicts)
    return len(conflicts) == 0


# For manual testing purposes
if __name__ == "__main__":
    input_file = "../testing/fhir/mult_plan_threshold_conflict.json"
    input_file = "../testing/fhir/mult_plan_no_conflict_shared_obs_def.json"
    # input_file = '../FHIR_examples/FHIR_definition_items.json'
    output_file = "../TMR_examples/output2.trig"

    with open(input_file) as f:
        data = json.load(f)

        translator = FHIRToTmrPathATranslator()

        trig_output = translator.translate_bundle(data)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(trig_output)


        ds = Dataset()
        ds.parse(output_file, format="trig")
        conflicts = look_for_conflicts(ds)
        print(trig_output)

        print("Conflicts found:")
        for row in conflicts:
            print(row)
        
