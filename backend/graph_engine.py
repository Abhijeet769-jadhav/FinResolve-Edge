import networkx as nx
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from models import FinancialEvent

class FinancialGraphEngine:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.node_metadata: Dict[str, Dict[str, Any]] = {}
        self.edge_metadata: Dict[str, Dict[str, Any]] = {}

    def add_event(self, event: FinancialEvent, risk_level: str = "NORMAL"):
        """Ingests a financial event and adds nodes and relationships to the graph."""
        timestamp = event.timestamp
        acc_id = event.account_id
        dev_id = event.device_id
        ip_addr = event.ip
        loc_name = event.location
        evt_id = event.event_id

        # 1. Location node
        self._ensure_node(loc_name, "LOCATION", {"name": loc_name, "risk": "NORMAL"})

        # 2. Device node
        self._ensure_node(dev_id, "DEVICE", {
            "name": dev_id,
            "risk": risk_level if risk_level != "NORMAL" else "NORMAL",
            "location": loc_name
        })
        self._add_edge(dev_id, loc_name, "LOCATED_IN", {"timestamp": timestamp})

        # 3. IP node
        self._ensure_node(ip_addr, "IP", {"name": ip_addr, "risk": "NORMAL"})

        # 4. Account node
        self._ensure_node(acc_id, "ACCOUNT", {
            "name": acc_id,
            "risk": risk_level if risk_level != "NORMAL" else "NORMAL"
        })
        self._add_edge(acc_id, dev_id, "USES", {"timestamp": timestamp})
        self._add_edge(acc_id, ip_addr, "ACCESSED_FROM", {"timestamp": timestamp})

        # 5. Transaction or action event node if amount or recipient/merchant involved
        if event.amount > 0 or event.recipient_id or event.merchant_id:
            txn_node_id = evt_id
            self._ensure_node(txn_node_id, "TRANSACTION", {
                "name": evt_id,
                "amount": event.amount,
                "event_type": event.type.value if hasattr(event.type, "value") else str(event.type),
                "risk": risk_level
            })
            self._add_edge(acc_id, txn_node_id, "MAKES", {"amount": event.amount, "timestamp": timestamp})

            if event.recipient_id:
                rec_id = event.recipient_id
                self._ensure_node(rec_id, "RECIPIENT", {
                    "name": rec_id,
                    "risk": risk_level if risk_level != "NORMAL" else "NORMAL"
                })
                self._add_edge(txn_node_id, rec_id, "SENT_TO", {"amount": event.amount, "timestamp": timestamp})

            if event.merchant_id:
                mer_id = event.merchant_id
                self._ensure_node(mer_id, "MERCHANT", {
                    "name": mer_id,
                    "risk": "NORMAL"
                })
                self._add_edge(txn_node_id, mer_id, "PAID_TO", {"amount": event.amount, "timestamp": timestamp})

        # Keep graph bounded to avoid memory/SVG rendering bloat
        if self.graph.number_of_nodes() > 90:
            self._prune_old_nodes()

    def _prune_old_nodes(self):
        """Prunes oldest benign transactions and isolated nodes to keep memory negligible."""
        txn_nodes = [
            n for n in self.graph.nodes() 
            if self.graph.nodes[n].get("type") == "TRANSACTION" and self.graph.nodes[n].get("risk") == "NORMAL"
        ]
        # Remove up to 20 oldest normal transactions
        for n in txn_nodes[:20]:
            self.graph.remove_node(n)
            self.node_metadata.pop(n, None)

    def _ensure_node(self, node_id: str, node_type: str, attrs: Dict[str, Any]):
        cleaned_attrs = dict(attrs)
        cleaned_attrs.pop("type", None)
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, type=node_type, **cleaned_attrs)
            self.node_metadata[node_id] = {
                "id": node_id,
                "type": node_type,
                "first_seen": datetime.utcnow().isoformat(),
                "is_blocked": False,
                **cleaned_attrs
            }
        else:
            # Upgrade risk if new risk is higher
            current_risk = self.node_metadata[node_id].get("risk", "NORMAL")
            new_risk = attrs.get("risk", "NORMAL")
            risk_ranks = {"NORMAL": 0, "ELEVATED": 1, "HIGH": 2, "CRITICAL": 3, "CONTAINED": -1}
            if risk_ranks.get(new_risk, 0) > risk_ranks.get(current_risk, 0):
                self.graph.nodes[node_id]["risk"] = new_risk
                self.node_metadata[node_id]["risk"] = new_risk

    def _add_edge(self, u: str, v: str, relation: str, attrs: Dict[str, Any]):
        edge_id = f"{u}->{relation}->{v}"
        self.graph.add_edge(u, v, key=edge_id, relation=relation, **attrs)
        self.edge_metadata[edge_id] = {
            "id": edge_id,
            "source": u,
            "target": v,
            "relation": relation,
            **attrs
        }

    def mark_entity_contained(self, entity_id: str, strategy: str):
        """Marks a device or recipient node as CONTAINED / BLOCKED."""
        if self.graph.has_node(entity_id):
            self.graph.nodes[entity_id]["risk"] = "CONTAINED"
            self.graph.nodes[entity_id]["is_blocked"] = True
            self.graph.nodes[entity_id]["contained_by"] = strategy
            if entity_id in self.node_metadata:
                self.node_metadata[entity_id]["risk"] = "CONTAINED"
                self.node_metadata[entity_id]["is_blocked"] = True
                self.node_metadata[entity_id]["contained_by"] = strategy

    def get_incident_subgraph_nodes(self, entity_ids: List[str]) -> List[str]:
        """Returns all connected entities within 2 hops of the affected incident entities."""
        subgraph_nodes = set()
        for entity in entity_ids:
            if self.graph.has_node(entity):
                subgraph_nodes.add(entity)
                # 1-hop neighbors (predecessors and successors)
                neighbors = set(self.graph.predecessors(entity)) | set(self.graph.successors(entity))
                subgraph_nodes.update(neighbors)
                # 2-hop
                for n in neighbors:
                    subgraph_nodes.update(set(self.graph.predecessors(n)) | set(self.graph.successors(n)))
        return list(subgraph_nodes)

    def _calculate_node_relevance(self, node_id: str, focus_set: set) -> float:
        """Calculates relevance score to display top relationships on frontend."""
        meta = self.node_metadata.get(node_id, {})
        score = 0.0

        # High priority to focus / incident entities
        if node_id in focus_set:
            score += 200.0

        # Risk tier weighting
        risk = meta.get("risk", "NORMAL")
        risk_weights = {
            "CRITICAL": 100.0,
            "HIGH": 65.0,
            "ELEVATED": 35.0,
            "CONTAINED": 45.0,
            "NORMAL": 5.0
        }
        score += risk_weights.get(risk, 5.0)

        # Degree connectivity (hub nodes)
        degree = self.graph.degree(node_id) if self.graph.has_node(node_id) else 0
        score += min(degree * 4.0, 30.0)

        # Transactions with higher monetary exposure
        if meta.get("type") == "TRANSACTION":
            amt = meta.get("amount", 0.0)
            if amt > 50000:
                score += 25.0
            elif amt > 10000:
                score += 15.0

        return score

    def to_react_flow(self, focus_nodes: Optional[List[str]] = None, max_nodes: int = 50, max_edges: int = 80) -> Dict[str, Any]:
        """Converts graph into React Flow compatible nodes and edges with deterministic positioning.
        Strictly limits output to <= 50 visible top-relevant nodes and <= 80 edges.
        """
        focus_set = set(focus_nodes) if focus_nodes else set()
        all_graph_nodes = list(self.graph.nodes())

        if not all_graph_nodes:
            return {"nodes": [], "edges": []}

        # If graph size <= max_nodes, include all
        if len(all_graph_nodes) <= max_nodes:
            selected_nodes = all_graph_nodes
        else:
            # Score and rank every node in backend graph
            scored_nodes = [
                (node_id, self._calculate_node_relevance(node_id, focus_set))
                for node_id in all_graph_nodes
            ]
            # Sort by relevance score descending
            scored_nodes.sort(key=lambda x: x[1], reverse=True)
            selected_nodes = [n[0] for n in scored_nodes[:max_nodes]]

        target_set = set(selected_nodes)
        subgraph = self.graph.subgraph(target_set)

        type_columns = {
            "LOCATION": 50,
            "IP": 200,
            "DEVICE": 360,
            "ACCOUNT": 530,
            "TRANSACTION": 700,
            "RECIPIENT": 870,
            "MERCHANT": 870
        }

        # Group nodes by type and sort deterministically by node_id for rock-solid UI stability
        nodes_by_type = {}
        for node_id in subgraph.nodes():
            meta = self.node_metadata.get(node_id, {})
            node_type = meta.get("type", self.graph.nodes[node_id].get("type", "ACCOUNT"))
            nodes_by_type.setdefault(node_type, []).append(node_id)

        rf_nodes = []
        for ntype, nlist in nodes_by_type.items():
            nlist.sort()  # Deterministic row order prevents React Flow jumpiness
            col_x = type_columns.get(ntype, 500)
            for row_idx, node_id in enumerate(nlist):
                meta = self.node_metadata.get(node_id, {})
                risk = meta.get("risk", self.graph.nodes[node_id].get("risk", "NORMAL"))
                is_blocked = meta.get("is_blocked", False)
                row_y = 60 + (row_idx * 75)

                rf_nodes.append({
                    "id": str(node_id),
                    "type": "financialNode",
                    "position": {"x": col_x, "y": row_y},
                    "data": {
                        "id": str(node_id),
                        "label": str(meta.get("name", node_id)),
                        "nodeType": ntype,
                        "risk": risk,
                        "isBlocked": is_blocked,
                        "details": meta
                    }
                })

        # Process edges with strict animation cap (max 1-2 active threat edges, normal edges static)
        edge_candidates = []
        for u, v, k, data in subgraph.edges(keys=True, data=True):
            relation = data.get("relation", "CONNECTS_TO")
            amount = data.get("amount", 0.0)
            u_meta = self.node_metadata.get(u, {})
            v_meta = self.node_metadata.get(v, {})
            is_critical = u_meta.get("risk") in ["HIGH", "CRITICAL"] or v_meta.get("risk") in ["HIGH", "CRITICAL"]
            is_contained = u_meta.get("risk") == "CONTAINED" or v_meta.get("risk") == "CONTAINED"

            # Sort priority: critical first, then contained, then highest amount
            priority = (2 if is_critical else (1 if is_contained else 0), amount)
            edge_candidates.append((priority, u, v, k, data, is_critical, is_contained, relation, amount))

        # Sort edges by importance and slice to max_edges
        edge_candidates.sort(key=lambda x: x[0], reverse=True)
        selected_edges = edge_candidates[:max_edges]

        rf_edges = []
        animated_count = 0
        for _, u, v, k, data, is_critical, is_contained, relation, amount in selected_edges:
            stroke_color = "#EF4444" if is_critical else ("#10B981" if is_contained else "#475569")
            label = f"₹{amount:,.0f}" if amount > 0 else relation

            # Strictly limit animated edges to at most 2 critical threat edges
            should_animate = False
            if is_critical and not is_contained and animated_count < 2:
                should_animate = True
                animated_count += 1

            rf_edges.append({
                "id": str(k),
                "source": str(u),
                "target": str(v),
                "label": label,
                "animated": should_animate,
                "style": {
                    "stroke": stroke_color,
                    "strokeWidth": 2.0 if is_critical else 1.0,
                    "strokeDasharray": "4 4" if is_contained else None
                },
                "data": {
                    "relation": relation,
                    "amount": amount,
                    "isCritical": is_critical,
                    "isContained": is_contained
                }
            })

        return {"nodes": rf_nodes[:max_nodes], "edges": rf_edges[:max_edges]}

    def clear(self):
        self.graph.clear()
        self.node_metadata.clear()
        self.edge_metadata.clear()

graph_engine = FinancialGraphEngine()
