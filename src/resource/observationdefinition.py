from rdflib import Literal, RDF, RDFS
from ..constants import EX


class ObservationDefinition:
    def __init__(self, id, code, permitted_data, unit):
        self.id = id
        self.code = code
        self.permitted_data = permitted_data
        self.unit = unit
    
    def to_rdf(self, graph):
        od_node = EX[f"ObservationDefinition_{self.id}"]
        graph.add((od_node, RDF.type, EX.ObservationDefinition))
        graph.add((od_node, RDFS.label, Literal(self.id)))

        return od_node

    # debug
    def __str__(self) -> str:
        return f"ObservationDefinition(id='{self.id}', code='{self.code}', data_type='{self.permitted_data}', unit='{self.unit}')"

    def __repr__(self) -> str:
        return f"ObservationDefinition(id={self.id!r}, code={self.code!r}, permitted_data={self.permitted_data!r}, unit={self.unit!r})"
    