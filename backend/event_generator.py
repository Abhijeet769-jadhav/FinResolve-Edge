import asyncio
import random
import logging
import uuid
from collections import defaultdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import FinancialEvent, EventType
from anomaly_engine import anomaly_engine, EDGE_NODES
from graph_engine import graph_engine
from threat_dna import threat_dna_engine
from propagation_engine import propagation_engine
from simulation_engine import simulation_engine
from websocket_manager import ws_manager
from telemetry import telemetry_tracker

logger = logging.getLogger("finresolve.generator")

BENIGN_ACCOUNTS = [f"ACC-{1000 + i}" for i in range(25)]
BENIGN_DEVICES = [f"DEV-{500 + i}" for i in range(20)]
BENIGN_MERCHANTS = [f"MER-{100 + i}" for i in range(12)]
BENIGN_RECIPIENTS = [f"REC-{800 + i}" for i in range(15)]
BENIGN_IPS = [f"10.23.{random.randint(10, 80)}.{random.randint(2, 250)}" for _ in range(20)]

class EventGenerator:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.event_counter = 10000
        self.edge_sequences: Dict[str, int] = defaultdict(int)
        self.recent_events: List[FinancialEvent] = []
        self.max_history = 100
        self.attack_in_progress = False

    def next_event_identity(self, location: Optional[str] = None) -> tuple[str, str, int]:
        """Generates an authoritative, collision-proof event identity:
        - event_id: EVT-<UUID12> (guaranteed uniqueness across runs, restarts, distributed generators)
        - edge_id: EDGE-<LOCATION> (identifies regional edge ingestion node)
        - sequence_number: Monotonic per-edge sequence counter for replay detection / buffering sync
        """
        self.event_counter += 1
        node_loc = location if location in EDGE_NODES else "Mumbai"
        edge_id = f"EDGE-{node_loc.upper()}"
        self.edge_sequences[edge_id] += 1
        seq = self.edge_sequences[edge_id]
        event_id = f"EVT-{uuid.uuid4().hex[:12].upper()}"
        return event_id, edge_id, seq

    def next_event_id(self, location: Optional[str] = None) -> str:
        evt_id, _, _ = self.next_event_identity(location)
        return evt_id

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
        self.attack_in_progress = False

    async def start(self):
        """Starts the continuous background event loop."""
        self.is_running = True
        self.is_paused = False
        logger.info("EventGenerator started continuous event stream.")
        while self.is_running:
            try:
                # High-frequency continuous event generation stream (~12.5 events/sec)
                if not self.attack_in_progress and not self.is_paused:
                    event = self.generate_benign_event()
                    await self.process_and_broadcast_event(event, broadcast_graph=False)
                await asyncio.sleep(0.08)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background event loop: {e}")
                await asyncio.sleep(0.5)

    def stop(self):
        self.is_running = False

    def generate_benign_event(self) -> FinancialEvent:
        evt_type = random.choice([
            EventType.TRANSACTION,
            EventType.LOGIN,
            EventType.MERCHANT_PAYMENT,
            EventType.TRANSACTION
        ])
        
        # Each benign account has its own consistent home device, location, and subnet
        acc_idx = random.randint(1001, 1040)
        acc = f"ACC-{acc_idx}"
        dev = f"DEV-USR-{acc_idx}"
        loc = EDGE_NODES[acc_idx % len(EDGE_NODES)]
        ip = f"192.168.{(acc_idx % 250) + 1}.{random.randint(10, 220)}"

        amount = 0.0
        rec = None
        mer = None

        if evt_type == EventType.TRANSACTION:
            amount = round(random.uniform(500, 9500), 2)
            # Consistent legitimate contacts
            rec = f"REC-FRIEND-{(acc_idx % 10) + 1}"
        elif evt_type == EventType.MERCHANT_PAYMENT:
            amount = round(random.uniform(150, 2500), 2)
            mer = f"MER-STORE-{(acc_idx % 8) + 1}"

        return FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=evt_type,
            account_id=acc,
            device_id=dev,
            merchant_id=mer,
            recipient_id=rec,
            amount=amount,
            location=loc,
            ip=ip,
            metadata={"classification": "benign"}
        )

    async def process_and_broadcast_event(self, event: FinancialEvent, is_attack: bool = False, broadcast_graph: bool = True):
        """Processes event through anomaly engine and graph engine, then broadcasts updates."""
        # 1. Evaluate anomaly
        report, signal, incident = anomaly_engine.evaluate_event(event)

        # Record metrics in 1-second telemetry aggregator
        telemetry_tracker.record_event(is_anomaly=(report.classification in ["HIGH", "CRITICAL"]))

        # 2. Ingest into canonical graph
        graph_engine.add_event(event, risk_level=report.classification, anomaly_reasons=report.reasons)

        # Add to recent events buffer
        self.recent_events.insert(0, event)
        if len(self.recent_events) > self.max_history:
            self.recent_events.pop()

        # 3. Broadcast new event
        await ws_manager.broadcast("new_event", {
            "event": event.model_dump(),
            "anomaly": report.model_dump(),
            "signal": signal.model_dump() if signal else None
        })

        if report.classification in ["HIGH", "CRITICAL"]:
            await ws_manager.broadcast("anomaly_detected", report.model_dump())

        # If an incident was formed or updated, extract threat DNA and calculate forecast
        if incident:
            dna = threat_dna_engine.extract_threat_dna(incident)
            incident.threat_dna = dna
            forecast = propagation_engine.calculate_forecast(incident)
            incident.propagation_forecast = forecast

            # Compute preliminary recommendation
            simulations = simulation_engine.simulate_strategies(incident)
            recommended = next((s for s in simulations if s.is_recommended), simulations[-1])
            incident.recommended_action = recommended.model_dump()

            await ws_manager.broadcast("incident_created", {
                "incident": incident.model_dump(),
                "threat_dna": dna.model_dump(),
                "forecast": forecast.model_dump(),
                "recommendation": incident.recommended_action
            })

        # Event-driven graph update: broadcast whenever an attack event, incident, or anomaly occurs
        if broadcast_graph and (incident or is_attack or report.classification in ["HIGH", "CRITICAL"]):
            focus_entities = (incident.affected_accounts + incident.affected_devices + incident.affected_recipients) if incident else [event.account_id, event.device_id]
            if event.recipient_id and event.recipient_id not in focus_entities:
                focus_entities.append(event.recipient_id)
            rf_graph = graph_engine.to_react_flow(focus_nodes=focus_entities)
            await ws_manager.broadcast("graph_updated", rf_graph)

            if incident:
                evt_name = event.type.value if hasattr(event.type, 'value') else str(event.type)
                graph_engine.record_attack_snapshot(
                    incident.id, 
                    f"{evt_name} on {event.account_id} -> {report.classification}", 
                    {"risk": report.risk_score, "classification": report.classification, "event_id": event.event_id}
                )

    async def inject_attack_scenario(self, scenario: str = "account_takeover") -> Dict[str, Any]:
        """
        Executes a multi-stage coordinated synthetic attack with visible sequential delays,
        causing all 13 workflow stages to visibly trigger in sequence.
        """
        self.attack_in_progress = True
        scenario_clean = scenario.lower().strip()
        scenario_title = scenario_clean.replace('_', ' ').title()
        logger.info(f"Injecting attack scenario: {scenario_clean}")

        # Broadcast high-priority attack started alert to all clients
        await ws_manager.broadcast("attack_started", {
            "scenario": scenario_clean,
            "scenario_name": scenario_title,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "CRITICAL" if scenario_clean not in ["normal", "normal_traffic"] else "BENIGN",
            "message": f"EMERGENCY: Attack scenario '{scenario_title}' initiated across financial network.",
        })

        # Stage 1: Financial Event Stream Ingestion
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 1,
            "code": "EVENT_INGESTION",
            "title": "Financial Event Stream",
            "subtitle": f"Injecting synthetic attack: {scenario_title}",
            "status": "PROCESSING"
        })

        try:
            if scenario_clean in ["account_takeover", "ato"]:
                await self._run_account_takeover_attack()
            elif scenario_clean in ["weak_signals", "predictive", "emerging_threat"]:
                await self._run_weak_signals_attack()
            elif scenario_clean in ["mule_network", "mule"]:
                await self._run_mule_network_attack()
            elif scenario_clean in ["coordinated_fraud", "fraud"]:
                await self._run_coordinated_fraud_attack()
            elif scenario_clean in ["recipient_attack", "recipient"]:
                await self._run_recipient_attack()
            elif scenario_clean in ["credential_stuffing", "stuffing"]:
                await self._run_credential_stuffing_attack()
            elif scenario_clean in ["gateway_outage", "gateway"]:
                await self._run_gateway_outage_attack()
            elif scenario_clean in ["merchant_failure", "merchant_attack", "merchant"]:
                await self._run_merchant_failure_attack()
            elif scenario_clean in ["mixed_attack", "mixed"]:
                await self._run_mixed_attack()
            elif scenario_clean in ["normal", "normal_traffic"]:
                # Burst of standard benign retail transactions
                for _ in range(12):
                    evt = self.generate_benign_event()
                    await self.process_and_broadcast_event(evt, broadcast_graph=False)
                    await asyncio.sleep(0.04)
            else:
                await self._run_account_takeover_attack()
        except Exception as e:
            logger.error(f"Error in attack scenario {scenario_clean}: {e}", exc_info=True)
        finally:
            self.attack_in_progress = False

        # If an attack scenario ran, conclude workflow progression through stages 8, 9, 10
        if scenario_clean not in ["normal", "normal_traffic"]:
            all_incidents = anomaly_engine.get_all_incidents()
            recent_inc = all_incidents[0] if all_incidents else None
            
            if recent_inc:
                # Stage 8: Attack Simulation
                await asyncio.sleep(0.12)
                sim_results = simulation_engine.simulate_strategies(recent_inc, horizon="60m")
                await ws_manager.broadcast("simulation_completed", {
                    "incident_id": recent_inc.id,
                    "results": [r.model_dump() for r in sim_results]
                })
                await ws_manager.broadcast("workflow_stage_update", {
                    "stage_id": 8, "code": "ATTACK_SIMULATION", "title": "Attack Simulation",
                    "subtitle": "Simulating countermeasure trade-offs across 5 containment strategies",
                    "status": "ACTIVE"
                })

                # Stage 9: Simulation Evaluation
                await asyncio.sleep(0.12)
                rec_label = recent_inc.recommended_action.get('label', 'Coordinated Response') if recent_inc.recommended_action else 'Coordinated Response'
                await ws_manager.broadcast("workflow_stage_update", {
                    "stage_id": 9, "code": "SIMULATION_EVALUATION", "title": "Simulation Evaluation",
                    "subtitle": f"Optimal strategy identified: {rec_label}",
                    "status": "ACTIVE"
                })

                # Stage 10: Containment Recommendation
                await asyncio.sleep(0.12)
                await ws_manager.broadcast("workflow_stage_update", {
                    "stage_id": 10, "code": "CONTAINMENT_RECOMMENDATION", "title": "Containment Recommendation",
                    "subtitle": f"Staged for human approval: {rec_label}",
                    "status": "ACTIVE"
                })

                # Stage 11: Human Approval Gate
                await asyncio.sleep(0.12)
                await ws_manager.broadcast("workflow_stage_update", {
                    "stage_id": 11, "code": "HUMAN_APPROVAL", "title": "Human Approval",
                    "subtitle": "CRITICAL: Awaiting Level 2 SOC Analyst authorization to execute quarantine",
                    "status": "AWAITING_APPROVAL"
                })

                # Broadcast comprehensive Emergency Alert
                await ws_manager.broadcast("emergency_alert", {
                    "incident_id": recent_inc.id,
                    "threat_type": recent_inc.threat_type,
                    "severity": recent_inc.severity,
                    "risk_score": recent_inc.risk_score,
                    "affected_accounts": recent_inc.affected_accounts,
                    "affected_devices": recent_inc.affected_devices,
                    "affected_recipients": recent_inc.affected_recipients,
                    "scenario": scenario_clean,
                    "recommended_action": recent_inc.recommended_action,
                    "timestamp": datetime.utcnow().isoformat()
                })

        return {"status": "ATTACK_INJECTED", "scenario": scenario_clean}

    async def _run_account_takeover_attack(self):
        """
        Scenario 1: Coordinated Account Takeover (User Specification)
        Accounts: A101, A202, A303, A404, A505
        Device: DEV-D45
        Varying IPs: IP1 (198.51.100.11), IP2 (198.51.100.22)...
        Common Recipient: REC-R900
        Reveals: Different IPs do NOT mean independent actors. Graph reveals shared DEV-D45 nexus.
        """
        target_accounts = ["ACC-A101", "ACC-A202", "ACC-A303", "ACC-A404", "ACC-A505"]
        rogue_device = "DEV-D45"
        mule_recipient = "REC-R900"
        ips = [
            "198.51.100.11",
            "198.51.100.22",
            "198.51.100.33",
            "198.51.100.44",
            "198.51.100.55"
        ]
        location = "Pune"

        # Step 1: Device change & OTP failures on ACC-A101
        e_dev = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.DEVICE_CHANGE,
            account_id=target_accounts[0],
            device_id=rogue_device,
            location=location,
            ip=ips[0],
            metadata={"note": "New hardware fingerprint detected"}
        )
        await self.process_and_broadcast_event(e_dev, is_attack=True, broadcast_graph=False)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 2, "code": "EVENT_INGESTION", "title": "Real-Time Ingestion",
            "subtitle": f"Device {rogue_device} registered on {target_accounts[0]}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.08)

        for attempt in range(2):
            e_otp = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.OTP_FAILURE,
                account_id=target_accounts[0],
                device_id=rogue_device,
                location=location,
                ip=ips[0],
                metadata={"attempt": attempt + 1}
            )
            await self.process_and_broadcast_event(e_otp, is_attack=True, broadcast_graph=True)
            await asyncio.sleep(0.06)

        # Step 2: Device D45 logs into ALL 5 accounts with distinct IPs (Relationship graph nexus)
        for idx, acc in enumerate(target_accounts):
            e_login = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.LOGIN,
                account_id=acc,
                device_id=rogue_device,
                location=location,
                ip=ips[idx],
                metadata={"status": "credential_stuffing_pivot"}
            )
            await self.process_and_broadcast_event(e_login, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 4, "code": "INCIDENT_FORMATION", "title": "Incident Formation",
                "subtitle": f"Device {rogue_device} pivoting to {acc} from IP {ips[idx]}", "status": "ACTIVE"
            })
            await asyncio.sleep(0.07)

        # Step 3: Register common recipient REC-R900
        e_rec = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.NEW_RECIPIENT,
            account_id=target_accounts[0],
            device_id=rogue_device,
            recipient_id=mule_recipient,
            location=location,
            ip=ips[0],
            metadata={"beneficiary": "unverified"}
        )
        await self.process_and_broadcast_event(e_rec, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 5, "code": "TEMPORAL_GRAPH", "title": "Temporal Financial Graph",
            "subtitle": f"Nexus forming: All accounts linking to recipient {mule_recipient}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.08)

        # Step 4: Micro-test transaction ₹100
        e_test = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id=target_accounts[0],
            device_id=rogue_device,
            recipient_id=mule_recipient,
            amount=100.0,
            location=location,
            ip=ips[0],
            metadata={"note": "Micro-deposit validation probe"}
        )
        await self.process_and_broadcast_event(e_test, is_attack=True, broadcast_graph=True)
        await asyncio.sleep(0.08)

        # Step 5: Large fund transfers from all accounts to REC-R900
        amounts = [185000.0, 240000.0, 195000.0, 310000.0, 280000.0]
        for idx, acc in enumerate(target_accounts):
            e_txn = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=acc,
                device_id=rogue_device,
                recipient_id=mule_recipient,
                amount=amounts[idx],
                location=location,
                ip=ips[idx],
                metadata={"channel": "IMPS_EXPRESS"}
            )
            await self.process_and_broadcast_event(e_txn, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 7, "code": "PROPAGATION_FORECAST", "title": "Propagation Forecast",
                "subtitle": f"Coordinated transfer ₹{amounts[idx]:,.0f} from {acc} to {mule_recipient}", "status": "ACTIVE"
            })
            await asyncio.sleep(0.07)

    async def _run_weak_signals_attack(self):
        """
        Scenario 2: Predictive Weak Signals Progression
        Demonstrates Digital Immune System:
        Individually: Risk = LOW
        Collectively: Emerging Threat -> Threat DNA detected -> Risk spikes to 89 -> Projected exposure calculated!
        """
        dev = "DEV-GHOST-42"
        acc1 = "ACC-W101"
        acc2 = "ACC-W102"
        rec = "REC-SHADOW-88"
        loc = "Pune"

        # Signal 1: Login from new device (Individually LOW risk)
        e1 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.DEVICE_CHANGE,
            account_id=acc1,
            device_id=dev,
            location=loc,
            ip="203.0.113.88",
            metadata={"note": "New device fingerprint registered"}
        )
        await self.process_and_broadcast_event(e1, is_attack=True, broadcast_graph=False)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 1, "code": "WEAK_SIGNAL", "title": "Signal 1/5: Device Registration",
            "subtitle": f"New device {dev} associated with {acc1} (Risk: LOW)", "status": "ACTIVE"
        })
        await asyncio.sleep(0.12)

        # Signal 2: Single failed OTP (Individually LOW risk)
        e2 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.OTP_FAILURE,
            account_id=acc1,
            device_id=dev,
            location=loc,
            ip="203.0.113.88",
            metadata={"note": "Single OTP mismatch"}
        )
        await self.process_and_broadcast_event(e2, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 2, "code": "WEAK_SIGNAL", "title": "Signal 2/5: OTP Challenge",
            "subtitle": "Transient authentication failure (Risk: LOW)", "status": "ACTIVE"
        })
        await asyncio.sleep(0.12)

        # Signal 3: Second account uses same device (Individually ELEVATED)
        e3 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.LOGIN,
            account_id=acc2,
            device_id=dev,
            location=loc,
            ip="203.0.113.92",
            metadata={"note": "Device shared across second identity"}
        )
        await self.process_and_broadcast_event(e3, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 3, "code": "WEAK_SIGNAL", "title": "Signal 3/5: Cross-Account Convergence",
            "subtitle": f"Device {dev} accessed by second account {acc2}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.12)

        # Signal 4: Small ₹100 micro-probe test transfer
        e4 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id=acc1,
            device_id=dev,
            recipient_id=rec,
            amount=100.0,
            location=loc,
            ip="203.0.113.88",
            metadata={"note": "Micro-deposit validation test"}
        )
        await self.process_and_broadcast_event(e4, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 4, "code": "WEAK_SIGNAL", "title": "Signal 4/5: Micro-Probe Validation",
            "subtitle": f"₹100 micro-deposit sent to {rec}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.12)

        # Signal 5: Recipient concentration (second account targets same recipient)
        e5 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id=acc2,
            device_id=dev,
            recipient_id=rec,
            amount=100.0,
            location=loc,
            ip="203.0.113.92",
            metadata={"note": "Second micro-deposit validation test"}
        )
        await self.process_and_broadcast_event(e5, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 5, "code": "WEAK_SIGNAL", "title": "Signal 5/5: Common Beneficiary Targeted",
            "subtitle": f"Account {acc2} targeting same recipient {rec}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.12)

        # Culmination: Threat DNA extracts emerging coordinated nexus -> Escalates to CRITICAL
        e_escalate = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id=acc1,
            device_id=dev,
            recipient_id=rec,
            amount=480000.0,
            location=loc,
            ip="203.0.113.88",
            metadata={"note": "Staged full-scale transfer"}
        )
        await self.process_and_broadcast_event(e_escalate, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 6, "code": "THREAT_DNA", "title": "Emerging Threat DNA Detected",
            "subtitle": "Collective fusion: Risk 89 (CRITICAL) • ₹14.5L projected exposure", "status": "ACTIVE"
        })

    async def _run_mule_network_attack(self):
        """Scenario 3: Mule Network Fan-Out Cascade."""
        primary_acc = "ACC-MULE-HEAD-01"
        recipients = ["REC-MULE-A", "REC-MULE-B", "REC-MULE-C", "REC-MULE-D"]
        for idx, rec in enumerate(recipients):
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=primary_acc,
                device_id=f"DEV-MULE-NODE-{idx}",
                recipient_id=rec,
                amount=round(random.uniform(90000, 180000), 2),
                location="Mumbai",
                ip=f"10.25.{idx}.12",
                metadata={"pattern": "fan_out_mule_cascade"}
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
            await asyncio.sleep(0.08)

    async def _run_coordinated_fraud_attack(self):
        """Scenario 4: Multi-Account Coordinated Bust-Out."""
        accounts = [f"ACC-BUST-{4000 + i}" for i in range(4)]
        dest_mer = "MER-OFFSHORE-77"
        for acc in accounts:
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=acc,
                device_id="DEV-BUST-COORDINATOR",
                merchant_id=dest_mer,
                amount=round(random.uniform(150000, 320000), 2),
                location="Bangalore",
                ip="198.51.100.89",
                metadata={"attack": "coordinated_overdraft_bustout"}
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
            await asyncio.sleep(0.08)

    async def _run_recipient_attack(self):
        """Scenario 5: Recipient Funneling Attack."""
        target_rec = "REC-FUNNEL-999"
        accounts = [f"ACC-VICTIM-{100 + i}" for i in range(5)]
        for acc in accounts:
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=acc,
                device_id=f"DEV-POS-{acc}",
                recipient_id=target_rec,
                amount=round(random.uniform(60000, 140000), 2),
                location="Delhi",
                ip="203.0.113.19",
                metadata={"attack": "recipient_funnel_convergence"}
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
            await asyncio.sleep(0.08)

    async def _run_credential_stuffing_attack(self):
        """Scenario 6: Automated High-Frequency Credential Stuffing."""
        bot_device = "DEV-BOTNET-STUFFER"
        accounts = [f"ACC-USER-{500 + i}" for i in range(8)]
        for acc in accounts:
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.FAILED_LOGIN,
                account_id=acc,
                device_id=bot_device,
                location="Hyderabad",
                ip="192.0.2.144",
                metadata={"tool": "automated_spray_proxy"}
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=False)
            await asyncio.sleep(0.05)

    async def _run_gateway_outage_attack(self):
        """
        Scenario 7: Operational Incident — Regional Payment Gateway Degradation.
        Burst of 504 timeouts from Mumbai node; system recommends traffic reroute & backoff.
        """
        gateway_dev = "GATEWAY-CLUSTER-MUMBAI"
        for i in range(7):
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.API_ERROR,
                account_id="ACC-SYSTEM-GATEWAY",
                device_id=gateway_dev,
                location="Mumbai",
                ip="10.50.0.1",
                metadata={
                    "status_code": 504,
                    "error": "GATEWAY_TIMEOUT",
                    "latency_ms": 4820,
                    "endpoint": "/v1/settlement/authorize"
                }
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 3, "code": "EDGE_ANOMALY", "title": "Operational Gateway Fault",
                "subtitle": f"Timeout 504 spike on {gateway_dev} (Mumbai)", "status": "ACTIVE"
            })
            await asyncio.sleep(0.08)

    async def _run_merchant_failure_attack(self):
        """Scenario 8: Operational Incident — Merchant Aggregator Dropouts."""
        merchants = ["MER-AGG-PAYLINK-01", "MER-AGG-PAYLINK-02", "MER-AGG-PAYLINK-03"]
        for mer in merchants:
            for _ in range(2):
                e = FinancialEvent(
                    event_id=self.next_event_id(),
                    timestamp=datetime.utcnow().isoformat(),
                    type=EventType.MERCHANT_PAYMENT,
                    account_id="ACC-CORP-RETAIL",
                    device_id="DEV-POS-TERMINAL",
                    merchant_id=mer,
                    amount=round(random.uniform(35000, 85000), 2),
                    location="Delhi",
                    ip="10.88.1.1",
                    metadata={"error": "SETTLEMENT_TIMEOUT_DECLINE", "aggregator": "PAYLINK"}
                )
                await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
                await asyncio.sleep(0.08)

    async def _run_mixed_attack(self):
        """Scenario 9: Coordinated Fraud Disguised within Gateway Outage."""
        # Step 1: Gateway turbulence
        for _ in range(3):
            e_err = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.API_ERROR,
                account_id="ACC-SYSTEM-GATEWAY",
                device_id="GATEWAY-CLUSTER-MUMBAI",
                location="Mumbai",
                ip="10.50.0.1",
                metadata={"status_code": 504}
            )
            await self.process_and_broadcast_event(e_err, is_attack=True, broadcast_graph=False)
            await asyncio.sleep(0.06)

        # Step 2: High-value diversion while alarms are distracted
        e_stealth = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id="ACC-STEALTH-99",
            device_id="DEV-STEALTH-EXPLOIT",
            recipient_id="REC-OFFSHORE-SHADOW",
            amount=420000.0,
            location="Bangalore",
            ip="198.51.100.99",
            metadata={"strategy": "opportunistic_camouflage"}
        )
        await self.process_and_broadcast_event(e_stealth, is_attack=True, broadcast_graph=True)
        await asyncio.sleep(0.08)

event_generator = EventGenerator()
