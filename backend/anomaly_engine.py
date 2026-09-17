import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from models import (
    FinancialEvent, AnomalyReport, AnomalyFactor, EdgeNodeSignal,
    Incident, ThreatDNA
)
from graph_engine import graph_engine

EDGE_NODES = ["Pune", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]

class AnomalyAndIncidentEngine:
    def __init__(self):
        # In-memory tracking structures for rule scoring
        self.device_accounts = defaultdict(set)
        self.device_recent_events = defaultdict(list)
        self.account_recent_events = defaultdict(list)
        self.account_otp_failures = defaultdict(int)
        self.account_locations = defaultdict(set)
        self.account_recipients = defaultdict(set)

        # Global Edge Benchmark Funnel Counters (User Architectural Directive)
        self.edge_counters = {
            "events_received": 0,
            "events_filtered": 0,
            "events_forwarded": 0,
            "events_processed": 0,
            "signals_correlated": 0,
            "incidents_formed": 0,
            "critical_incidents": 0
        }

        # Edge node status tracking & offline simulation buffer
        self.edge_node_stats = {
            node: {
                "status": "ONLINE",  # ONLINE, OFFLINE, BUFFERING, RECONNECTED, SYNCING
                "events_received": 0,
                "events_filtered": 0,
                "events_forwarded": 0,
                "signals_processed": 0,
                "anomalies_detected": 0,
                "buffered_count": 0,
                "local_buffer": [],
                "last_active": datetime.utcnow().isoformat(),
                "latency_ms": 12 + (hash(node) % 8)
            }
            for node in EDGE_NODES
        }

        # Incidents repository
        self.incidents: Dict[str, Incident] = {}
        self.active_incident_counter = 1000

        # Anomaly reports history
        self.anomaly_reports: List[AnomalyReport] = []

    def disconnect_edge_node(self, node_name: str) -> Dict[str, Any]:
        """Simulates edge node disconnection from central network."""
        if node_name in self.edge_node_stats:
            self.edge_node_stats[node_name]["status"] = "OFFLINE"
            return {"node": node_name, "status": "OFFLINE", "message": f"{node_name} disconnected. Local detection active in buffer mode."}
        return {"error": "Node not found"}

    def reconnect_and_sync_edge_node(self, node_name: str) -> Dict[str, Any]:
        """Simulates edge node reconnection and batch synchronization."""
        if node_name in self.edge_node_stats:
            stats = self.edge_node_stats[node_name]
            buffered_count = len(stats.get("local_buffer", []))
            stats["status"] = "SYNCING"
            # Flush buffered events into forwarded count
            stats["events_forwarded"] += buffered_count
            self.edge_counters["events_forwarded"] += buffered_count
            stats["local_buffer"] = []
            stats["buffered_count"] = 0
            stats["status"] = "ONLINE"
            return {
                "node": node_name,
                "status": "ONLINE",
                "synced_events": buffered_count,
                "message": f"Successfully synchronized {buffered_count} buffered events from {node_name} to central engine."
            }
        return {"error": "Node not found"}

    def evaluate_event(self, event: FinancialEvent) -> Tuple[AnomalyReport, Optional[EdgeNodeSignal], Optional[Incident]]:
        """
        Evaluates a single financial event:
        1. Calculates explainable risk score.
        2. Generates edge node cryptographic signal (ML-DSA-65 / SHA-384).
        3. Aggregates into an incident if risk warrants.
        """
        acc = event.account_id
        dev = event.device_id
        loc = event.location
        ts = event.timestamp
        evt_type = event.type.value if hasattr(event.type, "value") else str(event.type)

        # Update global benchmark counters (User Architectural Directive)
        self.edge_counters["events_received"] += 1
        self.edge_counters["events_processed"] += 1

        is_offline = False
        if loc in self.edge_node_stats:
            self.edge_node_stats[loc]["events_received"] += 1
            self.edge_node_stats[loc]["last_active"] = ts
            is_offline = (self.edge_node_stats[loc]["status"] == "OFFLINE")

        # Update local tracking with strict bounds to prevent memory accumulation
        self.device_accounts[dev].add(acc)
        self.device_recent_events[dev].append(ts)
        if len(self.device_recent_events[dev]) > 10:
            self.device_recent_events[dev].pop(0)

        self.account_recent_events[acc].append(ts)
        if len(self.account_recent_events[acc]) > 10:
            self.account_recent_events[acc].pop(0)

        self.account_locations[acc].add(loc)

        if evt_type == "OTP_FAILURE":
            self.account_otp_failures[acc] += 1
        elif evt_type == "LOGIN":
            pass

        if event.recipient_id:
            self.account_recipients[acc].add(event.recipient_id)

        # --- Rule Evaluation ---
        factors: List[AnomalyFactor] = []
        reasons: List[str] = []
        raw_score = 0.0

        # Rule 1: Multiple accounts from one device (+25)
        linked_acc_count = len(self.device_accounts[dev])
        if linked_acc_count >= 4:
            contrib = 25.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="SHARED_DEVICE_HIGH", score_contribution=contrib, description=f"Device {dev} linked to {linked_acc_count} accounts"))
            reasons.append(f"Device connected to {linked_acc_count} accounts")
        elif linked_acc_count >= 2:
            contrib = 15.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="SHARED_DEVICE_MODERATE", score_contribution=contrib, description=f"Device {dev} linked to {linked_acc_count} accounts"))
            reasons.append(f"Device connected to {linked_acc_count} accounts")

        # Rule 2: Unusual transaction amount (+20)
        if event.amount >= 250000:
            contrib = 20.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="HIGH_VALUE_TRANSACTION", score_contribution=contrib, description=f"Transaction ₹{event.amount:,.0f} exceeds safe threshold"))
            reasons.append(f"Unusual high-value transaction of ₹{event.amount:,.0f}")
        elif event.amount >= 80000:
            contrib = 10.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="ELEVATED_TRANSACTION", score_contribution=contrib, description=f"Transaction ₹{event.amount:,.0f} above normal distribution"))
            reasons.append(f"Elevated transaction amount ₹{event.amount:,.0f}")

        # Rule 3: Multiple OTP failures (+15)
        otp_fails = self.account_otp_failures[acc]
        if otp_fails >= 3:
            contrib = 15.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="MULTIPLE_OTP_FAILURES", score_contribution=contrib, description=f"{otp_fails} consecutive authentication failures"))
            reasons.append(f"{otp_fails} consecutive OTP failures on account")
        elif otp_fails >= 1:
            contrib = 8.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="OTP_FAILURE_DETECTED", score_contribution=contrib, description="Recent OTP failure detected"))
            reasons.append("Recent OTP challenge failure detected")

        # Rule 4: New recipient (+15)
        if evt_type == "NEW_RECIPIENT" or (event.recipient_id and len(self.account_recipients[acc]) == 1):
            contrib = 15.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="NEW_RECIPIENT_ADDED", score_contribution=contrib, description=f"New recipient {event.recipient_id or 'REC'} registered"))
            reasons.append("New recipient created shortly before high-value action")

        # Rule 5: Rapid transaction frequency / velocity (+15)
        recent_acc_evts = len(self.account_recent_events[acc])
        recent_dev_evts = len(self.device_recent_events[dev])
        if recent_acc_evts >= 4 or recent_dev_evts >= 6:
            contrib = 15.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="HIGH_TRANSACTION_VELOCITY", score_contribution=contrib, description=f"Velocity spike: {recent_dev_evts} events from device"))
            reasons.append(f"Transaction velocity increased {min(recent_dev_evts * 45, 380)}%")

        # Rule 6: Multiple locations in short time (+10)
        loc_count = len(self.account_locations[acc])
        if loc_count >= 2:
            contrib = 10.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="GEO_VELOCITY_ANOMALY", score_contribution=contrib, description=f"Account accessed across {loc_count} distinct regions"))
            reasons.append(f"Multiple locations accessed ({', '.join(self.account_locations[acc])})")

        # Rule 7: Operational API / Gateway Error (+45)
        if evt_type == "API_ERROR":
            contrib = 45.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="REGIONAL_GATEWAY_TIMEOUT", score_contribution=contrib, description=f"Gateway timeout error 504 on node {loc}"))
            reasons.append(f"Regional Gateway 504 degradation timeout on {loc}")

        # Rule 8: Recipient Concentration Cluster (+25)
        if event.recipient_id:
            rec_accounts = [a for a, recs in self.account_recipients.items() if event.recipient_id in recs]
            if len(rec_accounts) >= 3:
                contrib = 25.0
                raw_score += contrib
                factors.append(AnomalyFactor(rule="RECIPIENT_CONCENTRATION_CLUSTER", score_contribution=contrib, description=f"Recipient {event.recipient_id} targeted by {len(rec_accounts)} distinct accounts"))
                reasons.append(f"High-density recipient funneling ({len(rec_accounts)} accounts)")

        # Rule 9: Micro-deposit probe testing (+15)
        if 0 < event.amount <= 250 and (evt_type == "TRANSACTION") and (linked_acc_count >= 2 or event.recipient_id):
            contrib = 15.0
            raw_score += contrib
            factors.append(AnomalyFactor(rule="MICRO_DEPOSIT_VALIDATION_PROBE", score_contribution=contrib, description=f"Small probe amount ₹{event.amount:.0f} testing account access"))
            reasons.append("Micro-deposit probe transfer detected")

        # Normalize score to 0 - 100
        risk_score = min(100.0, round(raw_score, 1))

        # Classification
        if risk_score >= 81:
            classification = "CRITICAL"
        elif risk_score >= 61:
            classification = "HIGH"
        elif risk_score >= 31:
            classification = "ELEVATED"
        else:
            classification = "NORMAL"

        # Track edge filtering funnel: Normal events filtered locally; suspicious forwarded
        if classification == "NORMAL":
            self.edge_counters["events_filtered"] += 1
            if loc in self.edge_node_stats:
                self.edge_node_stats[loc]["events_filtered"] += 1
        else:
            if is_offline:
                if loc in self.edge_node_stats:
                    self.edge_node_stats[loc]["buffered_count"] += 1
                    self.edge_node_stats[loc]["local_buffer"].append({
                        "event_id": event.event_id,
                        "risk_score": risk_score,
                        "classification": classification,
                        "timestamp": ts
                    })
                    if len(self.edge_node_stats[loc]["local_buffer"]) > 500:
                        self.edge_node_stats[loc]["local_buffer"].pop(0)
            else:
                self.edge_counters["events_forwarded"] += 1
                if loc in self.edge_node_stats:
                    self.edge_node_stats[loc]["events_forwarded"] += 1

        report = AnomalyReport(
            event_id=event.event_id,
            account_id=acc,
            device_id=dev,
            risk_score=risk_score,
            classification=classification,
            reasons=reasons if reasons else ["Standard transaction and access baseline."],
            factors=factors,
            timestamp=ts
        )
        self.anomaly_reports.append(report)
        if len(self.anomaly_reports) > 50:
            self.anomaly_reports.pop(0)

        # Cryptographic edge signal abstraction
        signal = None
        if risk_score >= 40 and not is_offline:
            if loc in self.edge_node_stats:
                self.edge_node_stats[loc]["anomalies_detected"] += 1
                self.edge_node_stats[loc]["signals_processed"] += 1

            self.edge_counters["signals_correlated"] += 1

            # Deterministic SHA-384 hash of the metadata
            payload_data = f"{loc}:{dev}:{acc}:{risk_score}:{ts}"
            payload_hash = hashlib.sha384(payload_data.encode("utf-8")).hexdigest()

            signal = EdgeNodeSignal(
                signal_id=f"SIG-{abs(hash(payload_data)) % 100000:05d}",
                edge_node=loc,
                signal_type="COORDINATED_THREAT_PATTERN" if risk_score >= 70 else "LOCAL_EDGE_ANOMALY",
                risk_score=round(risk_score / 100.0, 2),
                affected_entities=linked_acc_count + (1 if event.recipient_id else 0),
                timestamp=ts,
                payload_hash=payload_hash,
                signature_status="VERIFIED",
                algorithm="ML-DSA-65 (Demonstrational Abstraction)",
                raw_preview=f"Edge[{loc}] detected {classification} anomaly score {risk_score} on {dev}."
            )

        # Incident Formation Logic
        incident = None
        if risk_score >= 60 and not is_offline:
            incident = self._correlate_or_create_incident(event, report, signal)

        return report, signal, incident

        return report, signal, incident

    def _correlate_or_create_incident(
        self,
        event: FinancialEvent,
        report: AnomalyReport,
        signal: Optional[EdgeNodeSignal]
    ) -> Incident:
        """Finds an existing active incident matching this device/account/recipient cluster, or forms a new one."""
        acc = event.account_id
        dev = event.device_id
        rec = event.recipient_id
        mer = event.merchant_id
        loc = event.location
        evt_type = event.type.value if hasattr(event.type, 'value') else str(event.type)

        # Check for matching active incident
        target_incident: Optional[Incident] = None
        for inc in self.incidents.values():
            if inc.status == "ACTIVE":
                # Check entity overlap
                if (dev in inc.affected_devices or 
                    acc in inc.affected_accounts or 
                    (rec and rec in inc.affected_recipients) or
                    (mer and mer in inc.affected_merchants)):
                    target_incident = inc
                    break

        timeline_entry = {
            "timestamp": event.timestamp,
            "event_id": event.event_id,
            "summary": f"{event.type.value if hasattr(event.type, 'value') else event.type} on {acc}",
            "detail": f"Risk {report.risk_score}: {', '.join(report.reasons[:2])}"
        }

        if target_incident:
            # Update existing incident
            if acc not in target_incident.affected_accounts:
                target_incident.affected_accounts.append(acc)
            if dev not in target_incident.affected_devices:
                target_incident.affected_devices.append(dev)
            if rec and rec not in target_incident.affected_recipients:
                target_incident.affected_recipients.append(rec)
            if mer and mer not in target_incident.affected_merchants:
                target_incident.affected_merchants.append(mer)
            if loc not in target_incident.regions:
                target_incident.regions.append(loc)

            target_incident.event_ids.append(event.event_id)
            if len(target_incident.event_ids) > 40:
                target_incident.event_ids.pop(0)

            target_incident.last_updated = event.timestamp
            target_incident.risk_score = max(target_incident.risk_score, report.risk_score)
            target_incident.timeline.append(timeline_entry)
            if len(target_incident.timeline) > 25:
                target_incident.timeline.pop(0)
            target_incident.confidence = min(98.0, target_incident.confidence + 3.0)

            # Determine severity
            if target_incident.risk_score >= 81 or len(target_incident.affected_accounts) >= 4:
                target_incident.severity = "CRITICAL"
            elif target_incident.risk_score >= 61:
                target_incident.severity = "HIGH"

            return target_incident
        else:
            # Form a new incident
            self.active_incident_counter += 1
            inc_id = f"INC-{self.active_incident_counter}"

            # Classify threat type (Security vs. Operational vs. Predictive Emerging)
            if evt_type == "API_ERROR":
                threat_type = "Regional Payment Gateway Degradation"
            elif "MER" in str(mer or "") or "PAYLINK" in str(mer or ""):
                threat_type = "Merchant Aggregator Failure / Decline Spike"
            elif "GHOST" in dev or "SHADOW" in str(rec or ""):
                threat_type = "Emerging Coordinated Nexus (Weak Signals Accumulator)"
            elif rec and len(self.device_accounts[dev]) > 1:
                threat_type = "Coordinated Account Takeover (Nexus Detected)"
            elif rec:
                threat_type = "Mule Network Expansion"
            elif mer:
                threat_type = "Distributed Merchant Payment Attack"
            else:
                threat_type = "Coordinated Account Takeover"

            new_incident = Incident(
                id=inc_id,
                threat_type=threat_type,
                severity=report.classification,
                confidence=82.0,
                risk_score=report.risk_score,
                first_detected=event.timestamp,
                last_updated=event.timestamp,
                affected_accounts=[acc],
                affected_devices=[dev],
                affected_recipients=[rec] if rec else [],
                affected_merchants=[mer] if mer else [],
                regions=[loc],
                current_stage="INCIDENT_FORMED",
                status="ACTIVE",
                event_ids=[event.event_id],
                timeline=[timeline_entry]
            )
            self.incidents[inc_id] = new_incident
            self.edge_counters["incidents_formed"] += 1
            if new_incident.severity == "CRITICAL":
                self.edge_counters["critical_incidents"] += 1

            return new_incident

    def get_incident(self, inc_id: str) -> Optional[Incident]:
        return self.incidents.get(inc_id)

    def get_all_incidents(self) -> List[Incident]:
        # Return sorted by last_updated descending
        return sorted(list(self.incidents.values()), key=lambda x: x.last_updated, reverse=True)

    def get_system_status_data(self) -> Dict[str, Any]:
        return {
            "edge_nodes": self.edge_node_stats,
            "edge_counters": self.edge_counters,
            "services": {
                "Event Stream": "ONLINE",
                "Graph Engine": "ONLINE",
                "Anomaly Engine": "ONLINE",
                "Threat DNA Engine": "ONLINE",
                "Forecast Engine": "ONLINE",
                "Simulation Engine": "READY",
                "Response Engine": "READY"
            },
            "pqc_verification": {
                "algorithm": "ML-DSA-65 (Post-Quantum Signature Scheme Abstraction)",
                "hash_standard": "SHA-384",
                "status": "OPERATIONAL / VERIFIED",
                "note": "Demonstrational cryptographic verification layer"
            }
        }

anomaly_engine = AnomalyAndIncidentEngine()
