from rdflib import Literal, RDF, RDFS, XSD, BNode
from ..constants import EX


class Action:
    def __init__(self, title, act_def, timing):
        self.title = title
        self.act_def = act_def
        self.timing = timing

    def to_rdf(self, graph):
        id = self.act_def.id if self.act_def else self.title
        action_node = EX[f"Action_{id}"]
        
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
