from rdflib import Literal, RDF, RDFS
from ..constants import EX

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
    