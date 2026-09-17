import asyncio
import random
import logging
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
        self.event_counter = 10000
        self.recent_events: List[FinancialEvent] = []
        self.max_history = 100
        self.attack_in_progress = False

    def next_event_id(self) -> str:
        self.event_counter += 1
        return f"EVT-{self.event_counter}"

    async def start(self):
        """Starts the continuous background event loop."""
        self.is_running = True
        logger.info("EventGenerator started.")
        while self.is_running:
            try:
                # High-frequency continuous event generation stream
                if not self.attack_in_progress:
                    event = self.generate_benign_event()
                    await self.process_and_broadcast_event(event, broadcast_graph=True)
                await asyncio.sleep(0.08)
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
        acc = random.choice(BENIGN_ACCOUNTS)
        dev = random.choice(BENIGN_DEVICES)
        loc = random.choice(EDGE_NODES)
        ip = random.choice(BENIGN_IPS)

        amount = 0.0
        rec = None
        mer = None

        if evt_type == EventType.TRANSACTION:
            amount = round(random.uniform(500, 15000), 2)
            rec = random.choice(BENIGN_RECIPIENTS)
        elif evt_type == EventType.MERCHANT_PAYMENT:
            amount = round(random.uniform(150, 4500), 2)
            mer = random.choice(BENIGN_MERCHANTS)

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

        # 2. Ingest into graph
        graph_engine.add_event(event, risk_level=report.classification)

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

            # Broadcast graph update only when requested to avoid DOM/GPU thrashing
            if broadcast_graph:
                rf_graph = graph_engine.to_react_flow(focus_nodes=incident.affected_accounts + incident.affected_devices)
                await ws_manager.broadcast("graph_updated", rf_graph)

    async def inject_attack_scenario(self, scenario: str = "account_takeover") -> Dict[str, Any]:
        """
        Executes a multi-stage coordinated synthetic attack with visible sequential delays,
        causing all 13 workflow stages to visibly trigger in sequence.
        """
        self.attack_in_progress = True
        logger.info(f"Injecting attack scenario: {scenario}")

        # Notify clients attack sequence starting
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 1,
            "code": "EVENT_INGESTION",
            "title": "Financial Event Stream",
            "subtitle": f"Injecting synthetic attack: {scenario.replace('_', ' ').title()}",
            "status": "PROCESSING"
        })

        if scenario in ["account_takeover", "ato"]:
            await self._run_account_takeover_attack()
        elif scenario in ["weak_signals", "predictive", "emerging_threat"]:
            await self._run_weak_signals_attack()
        elif scenario in ["mule_network", "mule"]:
            await self._run_mule_network_attack()
        elif scenario in ["coordinated_fraud", "fraud"]:
            await self._run_coordinated_fraud_attack()
        elif scenario in ["recipient_attack", "recipient"]:
            await self._run_recipient_attack()
        elif scenario in ["credential_stuffing", "stuffing"]:
            await self._run_credential_stuffing_attack()
        elif scenario in ["gateway_outage", "gateway"]:
            await self._run_gateway_outage_attack()
        elif scenario in ["merchant_failure", "merchant_attack", "merchant"]:
            await self._run_merchant_failure_attack()
        elif scenario in ["mixed_attack", "mixed"]:
            await self._run_mixed_attack()
        elif scenario in ["normal", "normal_traffic"]:
            # Burst of standard benign retail transactions
            for _ in range(12):
                evt = self.generate_benign_event()
                await self.process_and_broadcast_event(evt, broadcast_graph=False)
                await asyncio.sleep(0.04)
        else:
            await self._run_account_takeover_attack()

        self.attack_in_progress = False
        return {"status": "ATTACK_INJECTED", "scenario": scenario}

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
