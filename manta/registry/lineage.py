from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import datetime

@dataclass
class LineageNode:
    node_id: str
    node_type: str  # DATASET, FEATURE_VIEW, EXPERIMENT, MODEL, DEPLOYMENT
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class LineageEdge:
    source_id: str
    target_id: str
    relation: str  # PRODUCED_BY, TRAINED_ON, EVALUATED_AGAINST, DEPLOYED_AS

class LineageGraph:
    """Directed Acyclic Graph (DAG) for full provenance and auditability."""
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []

    def add_node(self, node_id: str, node_type: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> LineageNode:
        node = LineageNode(node_id=node_id, node_type=node_type, name=name, attributes=attributes or {})
        self.nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, relation: str) -> None:
        self.edges.append(LineageEdge(source_id=source_id, target_id=target_id, relation=relation))

    def get_upstream_lineage(self, node_id: str) -> List[LineageNode]:
        upstream = []
        queue = [node_id]
        visited = set()
        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            for edge in self.edges:
                if edge.target_id == curr and edge.source_id not in visited:
                    if edge.source_id in self.nodes:
                        upstream.append(self.nodes[edge.source_id])
                        queue.append(edge.source_id)
        return upstream

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.node_id, "type": n.node_type, "name": n.name} for n in self.nodes.values()],
            "edges": [{"source": e.source_id, "target": e.target_id, "relation": e.relation} for e in self.edges]
        }
