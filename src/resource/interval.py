from rdflib import Literal, RDF, XSD
from ..constants import EX, TMR

class Interval:
    def __init__(self, lo, hi, lo_inclusive, hi_inclusive, priority, ad_id):
        self.lo = lo
        self.hi = hi
        self.lo_inclusive = lo_inclusive
        self.hi_inclusive = hi_inclusive
        self.priority = priority
        self.ad_id = ad_id
    
    def to_rdf(self, graph):
        interval_node = EX[f"Interval_{self.priority}-{self.ad_id}"]

        def format_double(val):
            if val == float("-inf"):
                return "-INF"
            elif val == float("inf"):
                return "INF"
            return float(val)
    
        graph.add((interval_node, RDF.type, TMR.ThresholdInterval))
        graph.add((interval_node, EX.lowerBound, Literal(format_double(self.lo), datatype=XSD.double)))
        graph.add((interval_node, EX.upperBound, Literal(format_double(self.hi), datatype=XSD.double)))
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