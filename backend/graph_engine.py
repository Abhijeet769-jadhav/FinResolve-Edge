import networkx as nx
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from models import FinancialEvent

class FinancialGraphEngine:
    """
    Canonical Financial Graph Engine: Single source of truth for the entire platform.
    Every event across Phase 1 to 5 mutates this canonical graph state.
    Projections for React Flow extract the cohesive 1-hop and 2-hop threat subgraph.
    """
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.node_metadata: Dict[str, Dict[str, Any]] = {}
        self.edge_metadata: Dict[str, Dict[str, Any]] = {}
        self.mutation_log: List[Dict[str, Any]] = []
        self.attack_snapshots: Dict[str, List[Dict[str, Any]]] = {}
        self._init_base_topology()

    def _init_base_topology(self):
        """Initializes canonical edge nodes, regional gateways, and baseline healthy financial relationships."""
        regional_nodes = ["Mumbai", "Pune", "Delhi", "Bangalore", "Hyderabad"]
        now = datetime.utcnow().isoformat()
        for loc in regional_nodes:
            edge_id = f"EDGE-{loc.upper()}"
            gw_id = f"GATEWAY-{loc.upper()}"
            self._ensure_node(loc, "LOCATION", {"name": loc, "risk": 10.0, "state": "NORMAL"})
            self._ensure_node(edge_id, "EDGE_NODE", {"name": edge_id, "risk": 12.0, "state": "NORMAL", "location": loc})
            self._ensure_node(gw_id, "GATEWAY", {"name": gw_id, "risk": 10.0, "state": "NORMAL", "location": loc})
            self._add_edge(edge_id, gw_id, "ROUTES_TO", {"timestamp": now})

        # Baseline verified customer accounts, devices, and legitimate retail transaction flows
        baseline_flows = [
            ("ACC-1001", "DEV-USR-1001", "Mumbai", "EDGE-MUMBAI", "REC-FRIEND-1", 3450.0),
            ("ACC-1002", "DEV-USR-1002", "Delhi", "EDGE-DELHI", "REC-FRIEND-2", 1850.0),
            ("ACC-1003", "DEV-USR-1003", "Pune", "EDGE-PUNE", "MER-STORE-1", 450.0)
        ]
        for acc, dev, loc, edge, peer, amt in baseline_flows:
            self._ensure_node(acc, "ACCOUNT", {"name": acc, "risk": 10.0, "state": "NORMAL"})
            self._ensure_node(dev, "DEVICE", {"name": dev, "risk": 10.0, "state": "NORMAL", "location": loc})
            self._add_edge(acc, dev, "USES", {"timestamp": now})
            self._add_edge(dev, edge, "INGRESSED_AT", {"timestamp": now})
            self._add_edge(dev, loc, "LOCATED_IN", {"timestamp": now})
            if "MER" in peer:
                self._ensure_node(peer, "MERCHANT", {"name": peer, "risk": 10.0, "state": "NORMAL"})
                self._add_edge(acc, peer, "PAID_TO", {"amount": amt, "timestamp": now})
            else:
                self._ensure_node(peer, "RECIPIENT", {"name": peer, "risk": 10.0, "state": "NORMAL"})
                self._add_edge(acc, peer, "TRANSFERS_TO", {"amount": amt, "timestamp": now})

    def record_mutation(self, node_id: str, new_state: str, new_risk: float, reason: str) -> Dict[str, Any]:
        """Records an explicit timestamped transition on the canonical graph."""
        entry = {
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
            "node_id": str(node_id),
            "state": str(new_state),
            "risk": float(new_risk),
            "reason": str(reason)
        }
        self.mutation_log.append(entry)
        if len(self.mutation_log) > 100:
            self.mutation_log.pop(0)
        return entry

    def add_event(self, event: FinancialEvent, risk_level: str = "NORMAL", anomaly_reasons: Optional[List[str]] = None):
        """Ingests a financial event and mutates nodes and relationships in the canonical graph."""
        timestamp = event.timestamp
        acc_id = event.account_id
        dev_id = event.device_id
        ip_addr = event.ip
        loc_name = event.location
        evt_id = event.event_id

        # Determine node state based on risk
        risk_ranks = {
            "NORMAL": (15.0, "NORMAL"),
            "ELEVATED": (45.0, "SUSPICIOUS"),
            "HIGH": (75.0, "ACTIVE_THREAT"),
            "CRITICAL": (95.0, "CRITICAL"),
            "CONTAINED": (0.0, "CONTAINED")
        }
        numeric_risk, default_state = risk_ranks.get(risk_level, (15.0, "NORMAL"))

        # 1. Location & Regional Edge Infrastructure Nodes
        self._ensure_node(loc_name, "LOCATION", {
            "name": loc_name, 
            "risk": 10.0, 
            "state": "NORMAL"
        })
        
        edge_node_id = f"EDGE-{loc_name.upper()}"
        gateway_id = f"GATEWAY-{loc_name.upper()}"
        self._ensure_node(edge_node_id, "EDGE_NODE", {
            "name": edge_node_id,
            "risk": 15.0,
            "state": "NORMAL",
            "location": loc_name
        })
        self._ensure_node(gateway_id, "GATEWAY", {
            "name": gateway_id,
            "risk": 10.0,
            "state": "NORMAL",
            "location": loc_name
        })
        self._add_edge(edge_node_id, gateway_id, "ROUTES_TO", {"timestamp": timestamp})

        # 2. Device node
        reason_desc = (anomaly_reasons[0] if anomaly_reasons else f"Device hardware {dev_id}")
        self._ensure_node(dev_id, "DEVICE", {
            "name": dev_id,
            "risk": numeric_risk,
            "state": default_state,
            "location": loc_name,
            "reason": reason_desc
        })
        self._add_edge(dev_id, loc_name, "LOCATED_IN", {"timestamp": timestamp})
        self._add_edge(dev_id, edge_node_id, "INGRESSED_AT", {"timestamp": timestamp})

        # 3. IP node
        self._ensure_node(ip_addr, "IP", {
            "name": ip_addr, 
            "risk": 15.0 if risk_level == "NORMAL" else 45.0,
            "state": "OBSERVED" if risk_level == "NORMAL" else "SUSPICIOUS"
        })

        # 4. Account node
        self._ensure_node(acc_id, "ACCOUNT", {
            "name": acc_id,
            "risk": numeric_risk,
            "state": default_state,
            "reason": reason_desc
        })
        self._add_edge(acc_id, dev_id, "USES", {"timestamp": timestamp})
        self._add_edge(acc_id, ip_addr, "ACCESSED_FROM", {"timestamp": timestamp})

        # 5. Transaction or Action Event node
        if event.amount > 0 or event.recipient_id or event.merchant_id:
            txn_node_id = evt_id
            self._ensure_node(txn_node_id, "TRANSACTION", {
                "name": evt_id,
                "amount": event.amount,
                "event_type": event.type.value if hasattr(event.type, "value") else str(event.type),
                "risk": numeric_risk,
                "state": default_state
            })
            self._add_edge(acc_id, txn_node_id, "MAKES", {"amount": event.amount, "timestamp": timestamp})

            if event.recipient_id:
                rec_id = event.recipient_id
                self._ensure_node(rec_id, "RECIPIENT", {
                    "name": rec_id,
                    "risk": numeric_risk if numeric_risk > 20 else 15.0,
                    "state": default_state
                })
                self._add_edge(txn_node_id, rec_id, "SENT_TO", {"amount": event.amount, "timestamp": timestamp})
                # Direct nexus relationship for multi-account AML/ATO detection
                self._add_edge(acc_id, rec_id, "TRANSFERS_TO", {"amount": event.amount, "timestamp": timestamp})

            if event.merchant_id:
                mer_id = event.merchant_id
                self._ensure_node(mer_id, "MERCHANT", {
                    "name": mer_id,
                    "risk": 15.0,
                    "state": "NORMAL"
                })
                self._add_edge(txn_node_id, mer_id, "PAID_TO", {"amount": event.amount, "timestamp": timestamp})

        # Manage bounded memory without dropping active threat entities
        if self.graph.number_of_nodes() > 95:
            self._prune_old_nodes()

    def update_edge_resiliency(self, node_name: str, is_disconnected: bool, stats: Optional[Dict[str, Any]] = None):
        """Phase 2: Updates canonical edge node and gateway partition status and failover routing."""
        edge_id = f"EDGE-{node_name.upper()}"
        gateway_id = f"GATEWAY-{node_name.upper()}"
        failover_target = "GATEWAY-PUNE"

        # Ensure nodes exist
        self._ensure_node(edge_id, "EDGE_NODE", {"name": edge_id, "location": node_name})
        self._ensure_node(gateway_id, "GATEWAY", {"name": gateway_id, "location": node_name})
        self._ensure_node(failover_target, "GATEWAY", {"name": failover_target, "location": "Pune"})

        timestamp = datetime.utcnow().isoformat()
        failover_edge_id = f"{edge_id}->FAILOVER_REROUTE->{failover_target}"

        if is_disconnected:
            buf_count = (stats.get("buffered_count", 48) if stats else 48)
            self.node_metadata[edge_id].update({
                "risk": 88.0,
                "state": "PARTITIONED",
                "is_blocked": False,
                "metrics": {
                    "events_buffered": buf_count,
                    "failover": failover_target,
                    "status": "OFFLINE"
                },
                "reason": f"Regional Edge Partition: Local buffer active ({buf_count} events held)"
            })
            self.graph.nodes[edge_id]["risk"] = 88.0
            self.graph.nodes[edge_id]["state"] = "PARTITIONED"

            # Add dynamic failover link
            self._add_edge(edge_id, failover_target, "FAILOVER_REROUTE", {
                "timestamp": timestamp,
                "status": "ACTIVE_FAILOVER"
            })
            self.record_mutation(edge_id, "PARTITIONED", 88.0, f"Link failure on {node_name}. Rerouting to {failover_target}")
        else:
            synced_count = (stats.get("synced_events", 48) if stats else 48)
            self.node_metadata[edge_id].update({
                "risk": 15.0,
                "state": "RESOLVED",
                "is_blocked": False,
                "metrics": {
                    "events_synced": synced_count,
                    "status": "ONLINE"
                },
                "reason": f"Network partition restored: {synced_count} events synchronized"
            })
            self.graph.nodes[edge_id]["risk"] = 15.0
            self.graph.nodes[edge_id]["state"] = "RESOLVED"

            # Remove failover edge if present
            if self.graph.has_edge(edge_id, failover_target, key=failover_edge_id):
                self.graph.remove_edge(edge_id, failover_target, key=failover_edge_id)
                self.edge_metadata.pop(failover_edge_id, None)

            self.record_mutation(edge_id, "RESOLVED", 15.0, f"{node_name} reconnected & synchronized {synced_count} buffered events.")

    def update_pqc_tamper(self, original_amount: float, tampered_amount: float, is_contained: bool = False):
        """Phase 3: Integrates simulated adversarial payload tampering into canonical graph."""
        src_acc = "ACC-A101"
        src_dev = "DEV-D45"
        adv_node = "ADV-QUANTUM-MITM"
        txn_node = "TXN-PQC-TAMPER"
        rec_node = "REC-R900"
        timestamp = datetime.utcnow().isoformat()

        self._ensure_node(src_acc, "ACCOUNT", {"name": src_acc, "risk": 75.0, "state": "ACTIVE_THREAT"})
        self._ensure_node(src_dev, "DEVICE", {"name": src_dev, "risk": 90.0, "state": "CRITICAL"})
        self._ensure_node(rec_node, "RECIPIENT", {"name": rec_node, "risk": 80.0, "state": "SUSPICIOUS"})

        if not is_contained:
            self._ensure_node(adv_node, "ADVERSARY", {
                "name": adv_node,
                "risk": 98.0,
                "state": "TAMPERED",
                "reason": "Simulated adversarial payload tampering (SHA-384 mismatch, ML-DSA-65 signature failure)"
            })
            self._ensure_node(txn_node, "TRANSACTION", {
                "name": txn_node,
                "amount": tampered_amount,
                "risk": 98.0,
                "state": "TAMPERED",
                "details": {
                    "original_amount": original_amount,
                    "tampered_amount": tampered_amount,
                    "cryptography": "ML-DSA-65 Signature Failure"
                }
            })

            # Relationship: D45 -> INTERCEPTED_BY -> ADV-QUANTUM-MITM -> TXN-PQC-TAMPER -> SENT_TO -> REC-R900
            self._add_edge(src_dev, adv_node, "INTERCEPTED_BY", {"timestamp": timestamp})
            self._add_edge(adv_node, txn_node, "FORGED_PAYLOAD", {"amount": tampered_amount, "timestamp": timestamp})
            self._add_edge(txn_node, rec_node, "SENT_TO", {"amount": tampered_amount, "timestamp": timestamp})
            self.record_mutation(adv_node, "TAMPERED", 98.0, f"Payload forged from ₹{original_amount:,.0f} to ₹{tampered_amount:,.0f}")
        else:
            # SOC approval revokes lattice session key
            self.mark_entity_contained(adv_node, "PQC_KEY_REVOCATION")
            self.mark_entity_contained(txn_node, "PQC_KEY_REVOCATION")
            self.record_mutation(adv_node, "ISOLATED", 0.0, "Lattice session key revoked by SOC authorization")

    def update_load_stress(self, tier_eps: int, is_stopped: bool = False):
        """Phase 5: Integrates 10k volumetric botnet stress & edge drop filter into canonical graph."""
        botnet_alpha = "BOTNET-SYNDICATE-ALPHA"
        botnet_beta = "BOTNET-SYNDICATE-BETA"
        edge_ingress = "EDGE-INGRESS-FILTER"
        core_ledger = "CORE-LEDGER-PIPELINE"
        timestamp = datetime.utcnow().isoformat()

        if not is_stopped:
            self._ensure_node(botnet_alpha, "ADVERSARY", {
                "name": botnet_alpha,
                "risk": 92.0,
                "state": "CRITICAL",
                "reason": f"Volumetric attack cluster generating {tier_eps:,} EPS"
            })
            self._ensure_node(botnet_beta, "ADVERSARY", {
                "name": botnet_beta,
                "risk": 90.0,
                "state": "CRITICAL",
                "reason": f"Distributed assault cluster"
            })
            self._ensure_node(edge_ingress, "EDGE_NODE", {
                "name": edge_ingress,
                "risk": 82.0,
                "state": "BUFFERING",
                "metrics": {
                    "filtered_rate": "98.7%",
                    "forwarded_rate": "1.3%",
                    "tier_eps": tier_eps
                },
                "reason": f"High-volume ingress: 98.7% normal events dropped locally"
            })
            self._ensure_node(core_ledger, "CORE_LEDGER", {
                "name": core_ledger,
                "risk": 65.0,
                "state": "ELEVATED",
                "reason": "Core ledger receiving rate-limited suspicious signals"
            })

            # Relationships: BOTNET -> ATTACKS -> EDGE-INGRESS -> 98.7% FILTERED / SUSPICIOUS -> CORE-LEDGER
            self._add_edge(botnet_alpha, edge_ingress, "VOLUMETRIC_FLOOD", {"eps": tier_eps, "timestamp": timestamp})
            self._add_edge(botnet_beta, edge_ingress, "VOLUMETRIC_FLOOD", {"eps": tier_eps, "timestamp": timestamp})
            self._add_edge(edge_ingress, core_ledger, "CORRELATED_SIGNALS", {"filtered": "98.7%", "timestamp": timestamp})
            self.record_mutation(edge_ingress, "BUFFERING", 82.0, f"Ingress load {tier_eps:,} EPS. Edge filter shedding 98.7% normal traffic.")
        else:
            self.mark_entity_contained(botnet_alpha, "RATE_LIMIT_ISOLATION")
            self.mark_entity_contained(botnet_beta, "RATE_LIMIT_ISOLATION")
            if edge_ingress in self.node_metadata:
                self.node_metadata[edge_ingress].update({"risk": 15.0, "state": "NORMAL"})
            if core_ledger in self.node_metadata:
                self.node_metadata[core_ledger].update({"risk": 15.0, "state": "NORMAL"})
            self.record_mutation(botnet_alpha, "ISOLATED", 0.0, "Distributed load syndicate throttled by edge ingress rate limits")

    def _ensure_node(self, node_id: str, node_type: str, attrs: Dict[str, Any]):
        cleaned_attrs = dict(attrs)
        cleaned_attrs.pop("type", None)
        new_risk = float(cleaned_attrs.get("risk", 15.0))
        new_state = cleaned_attrs.get("state", "NORMAL")

        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, type=node_type, **cleaned_attrs)
            self.node_metadata[node_id] = {
                "id": node_id,
                "type": node_type,
                "first_seen": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_blocked": False,
                **cleaned_attrs
            }
            if new_state != "NORMAL":
                self.record_mutation(node_id, new_state, new_risk, cleaned_attrs.get("reason", f"Node created as {new_state}"))
        else:
            # Upgrade risk/state if new risk is higher or special state assigned
            current_risk = float(self.node_metadata[node_id].get("risk", 15.0))
            current_state = self.node_metadata[node_id].get("state", "NORMAL")

            # Prevent benign background events from downgrading contained/mitigated security postures
            if current_state in ["BLOCKED", "STEP_UP", "PROTECTED", "CONTAINED"] and new_state == "NORMAL":
                return

            if new_risk > current_risk or new_state in ["PARTITIONED", "TAMPERED", "ISOLATED", "CONTAINED", "BLOCKED", "STEP_UP", "PROTECTED"]:
                self.graph.nodes[node_id]["risk"] = new_risk
                self.graph.nodes[node_id]["state"] = new_state
                self.node_metadata[node_id]["risk"] = new_risk
                self.node_metadata[node_id]["state"] = new_state
                self.node_metadata[node_id]["updated_at"] = datetime.utcnow().isoformat()
                if "reason" in cleaned_attrs:
                    self.node_metadata[node_id]["reason"] = cleaned_attrs["reason"]
                if "metrics" in cleaned_attrs:
                    self.node_metadata[node_id]["metrics"] = cleaned_attrs["metrics"]

                if new_state != current_state:
                    self.record_mutation(node_id, new_state, new_risk, cleaned_attrs.get("reason", f"Transitioned to {new_state}"))

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

    def mark_entity_contained(self, entity_id: str, strategy: str, state: str = "CONTAINED", risk: float = 0.0, is_blocked: bool = False):
        """Marks a device, adversary, account, or recipient node with post-approval containment posture."""
        if self.graph.has_node(entity_id):
            self.graph.nodes[entity_id]["risk"] = risk
            self.graph.nodes[entity_id]["state"] = state
            self.graph.nodes[entity_id]["is_blocked"] = is_blocked
            self.graph.nodes[entity_id]["contained_by"] = strategy
            if entity_id in self.node_metadata:
                self.node_metadata[entity_id]["risk"] = risk
                self.node_metadata[entity_id]["state"] = state
                self.node_metadata[entity_id]["is_blocked"] = is_blocked
                self.node_metadata[entity_id]["contained_by"] = strategy
                self.node_metadata[entity_id]["updated_at"] = datetime.utcnow().isoformat()
            self.record_mutation(entity_id, state, risk, f"Quarantine policy ({strategy}) applied -> {state}")

    def get_incident_subgraph_nodes(self, entity_ids: List[str], hops: int = 2) -> List[str]:
        """Returns all nodes within N hops of the specified entity nodes in the canonical graph."""
        if not entity_ids:
            return []
        visited = set()
        frontier = set()
        for eid in entity_ids:
            sid = str(eid)
            visited.add(sid)
            if self.graph.has_node(sid):
                frontier.add(sid)

        for _ in range(hops):
            next_frontier = set()
            for curr in frontier:
                if self.graph.has_node(curr):
                    for pred in self.graph.predecessors(curr):
                        if pred not in visited:
                            visited.add(pred)
                            next_frontier.add(pred)
                    for succ in self.graph.successors(curr):
                        if succ not in visited:
                            visited.add(succ)
                            next_frontier.add(succ)
            frontier = next_frontier
            if not frontier:
                break
        return list(visited)

    def _prune_old_nodes(self):
        """Prunes oldest ephemeral transactions so the canonical graph preserves topological connectivity."""
        all_txn_nodes = [
            n for n in self.graph.nodes() 
            if self.graph.nodes[n].get("type") == "TRANSACTION"
        ]
        # Keep only the latest 8 transactions total in memory
        if len(all_txn_nodes) > 8:
            sorted_txns = sorted(
                all_txn_nodes, 
                key=lambda n: self.node_metadata.get(n, {}).get("updated_at", self.node_metadata.get(n, {}).get("first_seen", "")), 
                reverse=False
            )
            to_remove = sorted_txns[:len(all_txn_nodes) - 8]
            for n in to_remove:
                if self.graph.has_node(n):
                    self.graph.remove_node(n)
                    self.node_metadata.pop(n, None)

    def to_react_flow(self, focus_nodes: Optional[List[str]] = None, max_nodes: int = 50, max_edges: int = 80) -> Dict[str, Any]:
        """
        Converts canonical graph into React Flow compatible nodes and edges.
        STRICT GUARANTEES:
        1. Connected Topology: Threat entities are always rendered with their connected 1-hop structural partners.
        2. Permanent Green Baseline: Legitimate retail flow is always present to contrast against threats and confirm healthy operational state.
        3. Multi-Color Posture: Post-approval, BLOCKED (red), STEP_UP (yellow), and PROTECTED (green) nodes and matching dashed edges are prominently visible.
        4. Zero Floating Orphans: Every selected node has connected edges on canvas.
        """
        all_graph_nodes = set(self.graph.nodes())
        if not all_graph_nodes:
            return {"nodes": [], "edges": [], "timeline": []}

        # 1. Guaranteed baseline healthy entities (always included for contrast & legitimate flow)
        baseline_entities = {
            "Mumbai", "EDGE-MUMBAI", "GATEWAY-MUMBAI", "DEV-USR-1001", "ACC-1001", "REC-FRIEND-1",
            "Delhi", "EDGE-DELHI", "GATEWAY-DELHI", "DEV-USR-1002", "ACC-1002", "REC-FRIEND-2",
            "Pune", "EDGE-PUNE", "GATEWAY-PUNE", "DEV-USR-1003", "ACC-1003", "MER-STORE-1"
        }
        selected_set = {n for n in baseline_entities if n in all_graph_nodes}

        # 2. Identify active and recently mitigated threat entities
        threat_nodes = set(focus_nodes) if focus_nodes else set()
        for nid, meta in self.node_metadata.items():
            risk_val = float(meta.get("risk", 0.0))
            st = meta.get("state", "NORMAL")
            if risk_val >= 40.0 or st in ["CRITICAL", "ACTIVE_THREAT", "BLOCKED", "STEP_UP", "PROTECTED", "TAMPERED", "PARTITIONED", "BUFFERING"]:
                threat_nodes.add(nid)

        # Separate structural entities from ephemeral transactions
        structural_threats = {n for n in threat_nodes if self.node_metadata.get(n, {}).get("type") != "TRANSACTION"}
        txn_threats = {n for n in threat_nodes if self.node_metadata.get(n, {}).get("type") == "TRANSACTION"}

        # 3. For each structural threat, bring its 1-hop connected structural chain
        for n in structural_threats:
            if self.graph.has_node(n):
                selected_set.add(n)
                # Expand to direct neighbors (USES, INGRESSED_AT, ROUTES_TO, TRANSFERS_TO, LOCATED_IN)
                for neighbor in list(self.graph.predecessors(n)) + list(self.graph.successors(n)):
                    ntype = self.node_metadata.get(neighbor, {}).get("type")
                    if ntype != "TRANSACTION":
                        selected_set.add(neighbor)
                        # If an edge node is added, ensure its gateway is also present
                        if ntype == "EDGE_NODE":
                            for gw in self.graph.successors(neighbor):
                                if self.node_metadata.get(gw, {}).get("type") == "GATEWAY":
                                    selected_set.add(gw)

        # 4. Include at most 2-3 key transactions whose parent account AND recipient are already selected
        valid_txns = []
        for txn in txn_threats:
            preds = [p for p in self.graph.predecessors(txn) if p in selected_set]
            succs = [s for s in self.graph.successors(txn) if s in selected_set]
            if preds and succs:
                valid_txns.append(txn)
        selected_set.update(valid_txns[:3])

        # 5. Cap at max_nodes while preserving connected structures and baseline guarantee
        guaranteed_baseline = [
            "Mumbai", "EDGE-MUMBAI", "GATEWAY-MUMBAI", "DEV-USR-1001", "ACC-1001", "REC-FRIEND-1",
            "Delhi", "EDGE-DELHI", "GATEWAY-DELHI", "DEV-USR-1002", "ACC-1002", "REC-FRIEND-2",
            "Pune", "EDGE-PUNE", "GATEWAY-PUNE", "DEV-USR-1003", "ACC-1003", "MER-STORE-1"
        ]
        guaranteed_set = {n for n in guaranteed_baseline if n in all_graph_nodes}

        other_selected = [n for n in selected_set if n not in guaranteed_set]
        def other_priority(nid):
            st = self.node_metadata.get(nid, {}).get("state", "NORMAL")
            r = float(self.node_metadata.get(nid, {}).get("risk", 0.0))
            if focus_nodes and nid in focus_nodes:
                return (5, r)
            if st in ["BLOCKED", "STEP_UP", "PROTECTED", "CRITICAL", "ACTIVE_THREAT"]:
                return (4, r)
            return (1, r)

        other_sorted = sorted(other_selected, key=other_priority, reverse=True)
        available_slots = max(0, max_nodes - len(guaranteed_set))
        final_nodes = list(guaranteed_set) + other_sorted[:available_slots]

        target_set = set(final_nodes)
        subgraph = self.graph.subgraph(target_set)

        # 6. Columnar layout coordinates
        type_columns = {
            "LOCATION": 40,
            "EDGE_NODE": 180,
            "IP": 320,
            "DEVICE": 460,
            "ADVERSARY": 460,
            "ACCOUNT": 620,
            "GATEWAY": 760,
            "TRANSACTION": 820,
            "RECIPIENT": 980,
            "MERCHANT": 980,
            "CORE_LEDGER": 980
        }

        nodes_by_type = {}
        for node_id in subgraph.nodes():
            meta = self.node_metadata.get(node_id, {})
            node_type = meta.get("type", self.graph.nodes[node_id].get("type", "ACCOUNT"))
            nodes_by_type.setdefault(node_type, []).append(node_id)

        rf_nodes = []
        for ntype, nlist in nodes_by_type.items():
            # Sort: active threats and contained states first for clean horizontal alignment
            def row_sort_key(nid):
                meta = self.node_metadata.get(nid, {})
                st = meta.get("state", "NORMAL")
                r = float(meta.get("risk", 0.0))
                state_order = {
                    "BLOCKED": 1,
                    "STEP_UP": 2,
                    "PROTECTED": 3,
                    "CRITICAL": 4,
                    "ACTIVE_THREAT": 5,
                    "TAMPERED": 6,
                    "PARTITIONED": 7,
                    "SUSPICIOUS": 8,
                    "NORMAL": 9
                }
                return (state_order.get(st, 10), -r, str(nid))

            nlist.sort(key=row_sort_key)
            col_x = type_columns.get(ntype, 500)
            for row_idx, node_id in enumerate(nlist):
                meta = self.node_metadata.get(node_id, {})
                risk_val = float(meta.get("risk", 15.0))
                state_val = meta.get("state", "NORMAL")
                is_blocked = meta.get("is_blocked", False)
                row_y = 50 + (row_idx * 75)

                rf_nodes.append({
                    "id": str(node_id),
                    "type": "financialNode",
                    "position": {"x": col_x, "y": row_y},
                    "data": {
                        "id": str(node_id),
                        "label": str(meta.get("name", node_id)),
                        "nodeType": ntype,
                        "risk": risk_val,
                        "state": state_val,
                        "isBlocked": is_blocked,
                        "reason": meta.get("reason", ""),
                        "metrics": meta.get("metrics", {}),
                        "details": meta
                    }
                })

        # 7. Extract and style all edges within the subgraph
        edge_candidates = []
        for u, v, k, data in subgraph.edges(keys=True, data=True):
            relation = data.get("relation", "CONNECTS_TO")
            amount = data.get("amount", 0.0)
            u_meta = self.node_metadata.get(u, {})
            v_meta = self.node_metadata.get(v, {})

            u_risk = float(u_meta.get("risk", 0.0))
            v_risk = float(v_meta.get("risk", 0.0))

            u_state = u_meta.get("state", "NORMAL")
            v_state = v_meta.get("state", "NORMAL")
            u_blocked = u_meta.get("is_blocked", False)
            v_blocked = v_meta.get("is_blocked", False)

            # 1. BLOCKED rogue hardware / adversary edge (RED DASHED)
            is_blocked_edge = (
                u_state == "BLOCKED" or v_state == "BLOCKED" or
                u_blocked or v_blocked
            )

            # 2. PROTECTED / Quarantine Barrier / Frozen sink edge (GREEN DASHED)
            # Triggers when pointing to a protected recipient sink or involving contained funds
            is_protected_edge = not is_blocked_edge and (
                v_state in ["PROTECTED", "CONTAINED", "ISOLATED", "RESOLVED"] or
                (u_state in ["PROTECTED", "CONTAINED"] and v_state not in ["BLOCKED", "STEP_UP"])
            )

            # 3. STEP-UP AUTH / Adaptive Friction edge (YELLOW DASHED)
            # Triggers on challenged victim account authentication paths
            is_step_up_edge = not is_blocked_edge and not is_protected_edge and (
                u_state in ["STEP_UP", "CHALLENGED"] or 
                v_state in ["STEP_UP", "CHALLENGED"]
            )

            # 4. Active critical uncontained threat (RED SOLID / ANIMATED)
            is_critical = not is_blocked_edge and not is_step_up_edge and not is_protected_edge and (
                u_risk >= 70.0 or v_risk >= 70.0 or 
                u_state in ["CRITICAL", "ACTIVE_THREAT", "TAMPERED"] or
                v_state in ["CRITICAL", "ACTIVE_THREAT", "TAMPERED"] or
                "FAILOVER" in relation or "TAMPER" in relation or "VOLUMETRIC" in relation
            )

            # 5. Suspicious / Elevated (AMBER SOLID)
            is_suspicious = not is_blocked_edge and not is_step_up_edge and not is_protected_edge and not is_critical and (
                u_risk >= 40.0 or v_risk >= 40.0 or
                u_state in ["SUSPICIOUS", "ELEVATED", "BUFFERING"] or
                v_state in ["SUSPICIOUS", "ELEVATED", "BUFFERING"]
            )

            # 6. Partition / Regional failover (PURPLE DASHED)
            is_partition = (
                u_state == "PARTITIONED" or v_state == "PARTITIONED" or
                "FAILOVER" in relation
            )

            # 7. Healthy / Authorized legitimate flow (GREEN SOLID)
            is_healthy = not is_blocked_edge and not is_step_up_edge and not is_protected_edge and not is_critical and not is_suspicious and not is_partition

            # Priority for display: ensure containment barriers and active threats take top visual precedence
            priority_rank = (4 if is_blocked_edge else (3 if is_step_up_edge else (3 if is_critical else (2 if is_protected_edge else (1 if is_healthy else 0)))))
            priority = (priority_rank, amount)
            edge_candidates.append((
                priority, u, v, k, data, is_blocked_edge, is_step_up_edge, is_protected_edge, is_critical, is_suspicious, is_partition, is_healthy, relation, amount
            ))

        edge_candidates.sort(key=lambda x: x[0], reverse=True)
        selected_edges = edge_candidates[:max_edges]

        rf_edges = []
        animated_count = 0
        for _, u, v, k, data, is_blocked_edge, is_step_up_edge, is_protected_edge, is_critical, is_suspicious, is_partition, is_healthy, relation, amount in selected_edges:
            if is_blocked_edge:
                stroke_color = "#EF4444"  # Red for blocked / quarantined rogue device
                stroke_width = 2.4
                dash_array = "4 4"
                label = "BLOCKED / DENIED" if amount <= 0 else f"₹{amount:,.0f} (BLOCKED)"
            elif is_step_up_edge:
                stroke_color = "#F59E0B"  # Yellow / Amber for Step-Up Auth challenge
                stroke_width = 2.2
                dash_array = "5 5"
                label = "STEP-UP AUTH" if amount <= 0 else f"₹{amount:,.0f} (CHALLENGE)"
            elif is_protected_edge:
                stroke_color = "#10B981"  # Emerald green for protected sink / quarantine barrier
                stroke_width = 2.0
                dash_array = "5 5"
                label = "PROTECTED / HELD" if amount <= 0 else f"₹{amount:,.0f} (HELD)"
            elif is_critical:
                stroke_color = "#EF4444"  # Red for active threat vector
                stroke_width = 2.4
                dash_array = None
                label = f"₹{amount:,.0f}" if amount > 0 else relation
            elif is_partition:
                stroke_color = "#A855F7"  # Purple for network partition / failover
                stroke_width = 2.0
                dash_array = "4 4"
                label = relation
            elif is_suspicious:
                stroke_color = "#F59E0B"  # Amber for elevated
                stroke_width = 1.8
                dash_array = None
                label = f"₹{amount:,.0f}" if amount > 0 else relation
            else:
                # Vibrant Emerald Green for normal, legitimate, authorized financial flow!
                stroke_color = "#10B981"
                stroke_width = 1.6
                dash_array = None
                label = f"₹{amount:,.0f}" if amount > 0 else relation

            should_animate = False
            if is_critical and not is_blocked_edge and not is_protected_edge and animated_count < 4:
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
                    "strokeWidth": stroke_width,
                    "strokeDasharray": dash_array
                },
                "data": {
                    "relation": relation,
                    "amount": amount,
                    "isBlocked": is_blocked_edge,
                    "isStepUp": is_step_up_edge,
                    "isProtected": is_protected_edge,
                    "isCritical": is_critical,
                    "isHealthy": is_healthy,
                    "strokeColor": stroke_color
                }
            })

        return {
            "nodes": rf_nodes[:max_nodes], 
            "edges": rf_edges[:max_edges],
            "timeline": self.mutation_log[-25:]
        }

    def record_attack_snapshot(self, incident_id: str, step_label: str, details: Optional[Dict[str, Any]] = None):
        """Phase 10: Records a timestamped progression snapshot for Replay Attack feature."""
        if incident_id not in self.attack_snapshots:
            self.attack_snapshots[incident_id] = []

        rf_state = self.to_react_flow()
        self.attack_snapshots[incident_id].append({
            "step_index": len(self.attack_snapshots[incident_id]) + 1,
            "timestamp": datetime.utcnow().strftime("%H:%M:%S.%f")[:-3],
            "label": step_label,
            "details": details or {},
            "graph": rf_state
        })

    def get_attack_snapshots(self, incident_id: str) -> List[Dict[str, Any]]:
        """Returns replayable attack timeline snapshots for an incident."""
        return self.attack_snapshots.get(incident_id, [])

    def clear(self):
        self.graph.clear()
        self.node_metadata.clear()
        self.edge_metadata.clear()
        self.mutation_log.clear()
        self.attack_snapshots.clear()
        self._init_base_topology()

graph_engine = FinancialGraphEngine()

