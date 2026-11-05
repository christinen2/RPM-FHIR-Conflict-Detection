#!/usr/bin/env python3

import datetime
import json
from rdflib import Dataset, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
import re

TEMPORAL = Namespace("http://anonymous.org/vocab/temporalVocab/")
VOCAB = Namespace("http://anonymous.org/vocav/")
DATA = Namespace("http://anonymous.org/data/")
NANOPUB = Namespace("http://www.nanopub.org/nschema#")
PROV = Namespace("http://www.w3.org/ns/prov#")


class FHIRResourceParser:
    """Base parser ensuring robust structure validation."""
    def __init__(self, resource: dict):
        self.resource = resource or {}
        self.validate()

    def validate(self):
        if "resourceType" not in self.resource:
            raise ValueError("Missing resourceType in FHIR resource.")
            
    @staticmethod
    def clean_token(text: str) -> str:
        """Normalizes IDs/titles into CamelCase safe for URIs."""
        if not text:
            return "Unknown"
        words = re.split(r'[^a-zA-Z0-9]+', text)
        return "".join(word.capitalize() for word in words if word)


class PlanDefinitionParser(FHIRResourceParser):
    """Parses KIOLA PlanDefinition resources defining guidelines and action rules."""
    
    def validate(self):
        super().validate()
        if self.resource.get("resourceType") != "PlanDefinition":
            raise ValueError("Expected PlanDefinition resource.")

    def get_guideline_details(self) -> dict:
        guideline_id = self.resource.get("id", "Guideline")
        return {
            "id": guideline_id,
            "title": self.resource.get("title", guideline_id),
            "token": self.clean_token(guideline_id),
            "url": self.resource.get("url", f"PlanDefinition/{guideline_id}")
        }

    def get_actions(self) -> list:
        """Returns action metadata blocks."""
        return self.resource.get("action", [])


class ActivityDefinitionParser(FHIRResourceParser):
    """Parses KIOLA ActivityDefinition resources specifying clinical state logic."""
    
    def validate(self):
        super().validate()
        if self.resource.get("resourceType") != "ActivityDefinition":
            raise ValueError("Expected ActivityDefinition resource.")

    def get_activity_details(self) -> dict:
        activity_id = self.resource.get("id", "Activity")
        return {
            "id": activity_id,
            "title": self.resource.get("title", activity_id),
            "token": self.clean_token(activity_id),
            "url": self.resource.get("url", f"ActivityDefinition/{activity_id}")
        }

    def extract_characteristic(self) -> str:
        """Dynamically extracts the clinical target characteristic."""
        use_contexts = self.resource.get("useContext", [])
        if use_contexts:
            ctx = use_contexts[0]
            
            # Check valueCodeableConcept displays (e.g. SNOMED/LOINC displays)
            val_concept = ctx.get("valueCodeableConcept", {})
            for coding in val_concept.get("coding", []):
                if coding.get("display"):
                    return coding["display"]
            if val_concept.get("text"):
                return val_concept["text"]

            # Ignore priority-based system codings, look for descriptive displays
            ctx_code = ctx.get("code", {})
            for coding in ctx_code.get("coding", []):
                if coding.get("display") and "priority" not in coding.get("system", "").lower():
                    return coding["display"]

        # Check main activity code block
        observation_code = self.resource.get("code", {})
        for coding in observation_code.get("coding", []):
            if coding.get("display"):
                return coding["display"]
        if observation_code.get("text"):
            return observation_code["text"]
        
        # Fallback to cleaning raw identifiers
        raw_title = self.resource.get("title") or self.resource.get("id") or "Unknown"
        title_upper = raw_title.upper()
        if "BP" in title_upper or "HYPERTENSION" in title_upper:
            return "Blood Pressure"
        elif "HR" in title_upper or "BRADYCARDIA" in title_upper:
            return "Heart Rate"
        elif "WEIGHT" in title_upper:
            return "Body Weight"
        elif "SPO2" in title_upper:
            return "Oxygen Saturation"
            
        return raw_title

    def get_use_contexts(self) -> list:
        return self.resource.get("useContext", [])


# ==========================================
# Main KIOLA FHIR to TMR Converter
# ==========================================

class KIOLAFHIR2TMRConverter:
    def __init__(self):
        pass

    def convert(self, bundle_entries: list) -> Dataset:
        """
        Parses KIOLA FHIR resource entries and outputs a TMR TriG Dataset.
        """
        ds = Dataset()
        ds.bind("", TEMPORAL)
        ds.bind("VOCAB", VOCAB)
        ds.bind("data", DATA)
        ds.bind("nanopub", NANOPUB)
        ds.bind("prov", PROV)
        ds.bind("owl", OWL)
        ds.bind("xsd", XSD)

        resources_by_url = {}
        parsed_plan_defs = []

        # Indexing step: wrap resources dynamically into parser classes
        for entry in bundle_entries:
            resource = entry.get("resource", {})
            res_type = resource.get("resourceType")
            res_id = resource.get("id")

            if not res_id or not res_type: 
                continue

            # Create references using resource identifiers
            resources_by_url[f"DINGO/{res_type}/{res_id}"] = resource
            resources_by_url[f"{res_type}/{res_id}"] = resource

            if res_type == "PlanDefinition":
                try:
                    parsed_plan_defs.append(PlanDefinitionParser(resource))
                except ValueError:
                    continue

        if not parsed_plan_defs:
            raise ValueError("No valid PlanDefinition resources found in bundle.")
        
        for plan_parser in parsed_plan_defs:
            g_info = plan_parser.get_guideline_details()
            guideline_uri = TEMPORAL[f"CIG-{g_info['token']}"]

            # Guideline Declaration
            ds.add((guideline_uri, RDF.type, VOCAB.ClinicalGuideline))
            ds.add((guideline_uri, RDFS.label, Literal(g_info['title'], lang="en")))

            for action in plan_parser.get_actions():
                canonical_ref = action.get("definitionCanonical")
                action_title = action.get("title", "Action Alert")
                
                if not canonical_ref or "ActivityDefinition" not in canonical_ref:
                    continue
                    
                raw_activity = resources_by_url.get(canonical_ref)
                if not raw_activity:
                    continue
                
                # Wrap the ActivityDefinition inside its specialized parser
                activity_parser = ActivityDefinitionParser(raw_activity)
                act_info = activity_parser.get_activity_details()
                
                # --- GENERALIZED GRAPH URIs ---
                head_graph_uri = DATA[f"Rec-{g_info['token']}-{act_info['token']}_head"]
                assertion_graph_uri = DATA[f"Rec-{g_info['token']}-{act_info['token']}_assertion"]
                provenance_graph_uri = DATA[f"Rec-{g_info['token']}-{act_info['token']}_provenance"]
                pubinfo_graph_uri = DATA[f"Rec-{g_info['token']}-{act_info['token']}_pubinfo"]
                
                rec_uri = DATA[f"Rec-{g_info['token']}-{act_info['token']}"]
                cb_uri = DATA[f"CB-{g_info['token']}-{act_info['token']}"]
                act_type_uri = TEMPORAL[f"ActMonitor-{g_info['token']}-{act_info['token']}"]
                trans_type_uri = TEMPORAL[f"TrTransitionTo-{g_info['token']}-{act_info['token']}"]

                # 1. Global Declarations
                ds.add((act_type_uri, RDF.type, VOCAB.CareActionType))
                ds.add((act_type_uri, RDF.type, OWL.NamedIndividual))
                ds.add((act_type_uri, RDFS.label, Literal(f"Monitor {act_info['title']} Threshold Alert", lang="en")))

                # 2. Nanopub Head Graph
                head_graph = ds.graph(head_graph_uri)
                head_graph.add((head_graph_uri, RDF.type, NANOPUB.Nanopublication))
                head_graph.add((head_graph_uri, NANOPUB.hasAssertion, assertion_graph_uri))
                head_graph.add((head_graph_uri, NANOPUB.hasProvenance, provenance_graph_uri))
                head_graph.add((head_graph_uri, NANOPUB.hasPublicationInfo, pubinfo_graph_uri))

                # 3. Nanopub Assertion Graph (TMR logic)
                assertion_graph = ds.graph(assertion_graph_uri)
                assertion_graph.add((rec_uri, RDF.type, VOCAB.ClinicalRecommendation))
                assertion_graph.add((rec_uri, RDFS.label, Literal(action_title, lang="en")))
                assertion_graph.add((rec_uri, VOCAB.strength, Literal("should")))
                assertion_graph.add((rec_uri, VOCAB.partOf, guideline_uri))
                assertion_graph.add((rec_uri, VOCAB.aboutExecutionOf, act_type_uri))
                assertion_graph.add((rec_uri, VOCAB.basedOn, cb_uri))
                
                assertion_graph.add((cb_uri, RDF.type, VOCAB.CausationBelief))
                assertion_graph.add((cb_uri, VOCAB.strength, Literal("L1")))
                assertion_graph.add((cb_uri, VOCAB.frequency, Literal("always")))
                assertion_graph.add((act_type_uri, VOCAB.causes, trans_type_uri))
                
                assertion_graph.add((trans_type_uri, RDF.type, VOCAB.TransitionType))
                assertion_graph.add((trans_type_uri, RDF.type, OWL.NamedIndividual))

                # Handle Dynamic Characteristic & Logical Situations
                characteristic = activity_parser.extract_characteristic()
                use_contexts = activity_parser.get_use_contexts()
                
                # Case A: Qualitative baselines (no contexts defined)
                if not use_contexts:
                    sit_bnode = assertion_graph.resource(BNode())
                    sit_bnode.add(RDF.type, VOCAB.SituationType)
                    sit_bnode.add(RDFS.label, Literal(f"Patient in {act_info['title']} State", lang="en"))
                    sit_bnode.add(VOCAB.stateOf, Literal("urgent", datatype=XSD.string))
                    sit_bnode.add(VOCAB.refersToCharacteristic, Literal(characteristic))
                    
                    sit_bnode.add(VOCAB.hasLogicalOperator, Literal("=="))
                    sit_bnode.add(VOCAB.hasValue, Literal("Active"))
                    assertion_graph.add((trans_type_uri, VOCAB.hasExpectedSituation, sit_bnode.identifier))
                
                # Case B: Context thresholds mapped
                else:

                    thresholds = []
                    for ctx in use_contexts:
                        priority_state = ctx.get("code", {}).get("code", "urgent")
                        val_qty = ctx.get("valueQuantity", {})
                        if val_qty:
                            thresholds.append({
                                "val": float(val_qty.get("value")),
                                "op": val_qty.get("comparator", ">="),
                                "unit": val_qty.get("unit", ""),
                                "priority": priority_state
                            })

                    # Sort ascending by value so we can see the next tier
                    thresholds.sort(key=lambda x: x["val"])

                    for i, thresh in enumerate(thresholds):
                        sit_bnode = assertion_graph.resource(BNode())
                        sit_bnode.add(RDF.type, VOCAB.SituationType)
                        sit_bnode.add(VOCAB.refersToCharacteristic, Literal(characteristic))
                        sit_bnode.add(VOCAB.stateOf, Literal(thresh["priority"], datatype=XSD.string))
                        
                        # Check if there is a next highest threshold of the same operator type to create a range
                        if thresh["op"] in [">", ">="] and (i + 1) < len(thresholds):
                            next_thresh = thresholds[i + 1]
                            
                            # Define as a bounded range
                            sit_bnode.add(RDFS.label, Literal(f"Patient in range {thresh['val']} to {next_thresh['val']} {thresh['unit']}", lang="en"))
                            
                            # Lower bound component
                            low_node = BNode()
                            assertion_graph.add((low_node, VOCAB.hasLogicalOperator, Literal(thresh["op"])))
                            assertion_graph.add((low_node, VOCAB.hasValue, Literal(thresh["val"])))
                            sit_bnode.add(VOCAB.hasLowerConstraint, low_node)
                            
                            # Upper bound component (exclusive)
                            high_node = BNode()
                            assertion_graph.add((high_node, VOCAB.hasLogicalOperator, Literal("<")))
                            assertion_graph.add((high_node, VOCAB.hasValue, Literal(next_thresh["val"])))
                            sit_bnode.add(VOCAB.hasUpperConstraint, high_node)
                        
                        else:
                            # Highest tier or unbounded single constraint (e.g., >= 179)
                            sit_bnode.add(RDFS.label, Literal(f"Patient state {thresh['op']}{thresh['val']} {thresh['unit']}", lang="en"))
                            sit_bnode.add(VOCAB.hasLogicalOperator, Literal(thresh["op"]))
                            sit_bnode.add(VOCAB.hasValue, Literal(thresh["val"]))
                            
                        if thresh["unit"]:
                            sit_bnode.add(VOCAB.hasUnit, Literal(thresh["unit"]))
                            
                        assertion_graph.add((trans_type_uri, VOCAB.hasExpectedSituation, sit_bnode.identifier))

                # 4. Nanopub Provenance Graph
                provenance_graph = ds.graph(provenance_graph_uri)
                plan_def_url = URIRef(g_info['url'])
                activity_url = URIRef(act_info['url'])
            
                provenance_graph.add((assertion_graph_uri, PROV.wasDerivedFrom, plan_def_url))
                provenance_graph.add((cb_uri, PROV.wasDerivedFrom, activity_url))

                # 5. Nanopub Publication Info Graph
                pubinfo_graph = ds.graph(pubinfo_graph_uri)
                current_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                
                pubinfo_graph.add((head_graph_uri, PROV.generatedAtTime, Literal(current_timestamp, datatype=XSD.dateTime)))
                pubinfo_graph.add((head_graph_uri, PROV.wasAttributedTo, DATA.FHIRTransformationPipeline))

        return ds


if __name__ == '__main__':
    file_name = '../../FHIR_examples/FHIR_definition_items.json'

    with open(file_name) as f:
        data = json.load(f)
        # assumption is that json payload is a FHIR Bundle type
        # so need to extract the individual resources out.
        resources = data.get('entry')

        convertor = KIOLAFHIR2TMRConverter()
        tmr_dataset = convertor.convert(resources)
        output_trig_string = tmr_dataset.serialize(format="trig", inline=True)
        print(output_trig_string)