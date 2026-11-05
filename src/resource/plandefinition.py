from rdflib import Literal, RDF, RDFS
from ..constants import EX
from .action import Action

class PlanDefinition:
    def __init__(self, id, title, status, actions):
        self.id = id
        self.title = title
        self.status = status
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

        pd_node = EX[f"{self.id}"]
        graph.add(
            (
                pd_node, RDF.type, EX.PlanDefinition
            )
        )

        graph.add((pd_node, RDFS.label, Literal(self.title)))
        graph.add((pd_node, EX.status, Literal(self.status)))

        for action in self.actions:
            action_node = action.to_rdf(graph)
            graph.add((pd_node, EX.hasAction, action_node))

        return graph


    def combine_plan_defs(pds):
        ids = []
        titles = []
        status = True
        action_refs = []

        for pd in pds:
            ids.append(pd.id)
            titles.append(pd.title)
            status = status and pd.status == "active"
            action_refs.extend(pd.action_refs)

        combined_id = "_".join(ids)
        combined_title = "_".join(titles)

        return PlanDefinition(combined_id, combined_title, status, list(action_refs))


    # debug
    def __str__(self) -> str:
        actions_formatted = "\n  ".join(
            str(action) for action in self.actions
        )
        return (
            f"PlanDefinition ID: '{self.id}'\n"
            f"Title: '{self.title}'\n"
            f"Status: '{self.status}'\n"
            f"Actions ({len(self.actions)}):\n  {actions_formatted if actions_formatted else 'None'}"
        )

    def __repr__(self) -> str:
        return f"PlanDefinition(id={self.id!r}, title={self.title!r}, status={self.status!r}, actions={self.actions!r})"

