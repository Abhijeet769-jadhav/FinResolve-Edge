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

        if scenario == "account_takeover":
            await self._run_account_takeover_attack()
        elif scenario == "mule_network":
            await self._run_mule_network_attack()
        elif scenario == "merchant_attack":
            await self._run_merchant_attack()
        else:
            await self._run_account_takeover_attack()

        self.attack_in_progress = False
        return {"status": "ATTACK_INJECTED", "scenario": scenario}

    async def _run_account_takeover_attack(self):
        """
        Scenario 1: Coordinated Account Takeover
        Pattern: New Device -> Multiple Accounts -> Failed OTP -> Successful Login -> New Recipient -> Small Test Txn -> Large Transfer
        """
        rogue_device = f"DEV-ROGUE-{random.randint(900, 999)}"
        rogue_ip = f"198.51.100.{random.randint(10, 90)}"
        primary_location = "Pune"
        target_accounts = [f"ACC-{2000 + i}" for i in range(5)]
        mule_recipient = f"REC-MULE-{random.randint(900, 999)}"

        # Stage 1 & 2: First account probe from rogue device
        e1 = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.DEVICE_CHANGE,
            account_id=target_accounts[0],
            device_id=rogue_device,
            location=primary_location,
            ip=rogue_ip,
            metadata={"note": "New hardware fingerprint detected"}
        )
        await self.process_and_broadcast_event(e1, is_attack=True, broadcast_graph=False)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 2, "code": "EVENT_INGESTION", "title": "Real-Time Ingestion",
            "subtitle": f"Rogue device {rogue_device} registered", "status": "ACTIVE"
        })
        await asyncio.sleep(0.1)

        # Stage 3: OTP Failures (authentication attacks)
        for i in range(3):
            e_otp = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.OTP_FAILURE,
                account_id=target_accounts[0],
                device_id=rogue_device,
                location=primary_location,
                ip=rogue_ip,
                metadata={"attempt": i + 1}
            )
            await self.process_and_broadcast_event(e_otp, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 3, "code": "EDGE_ANOMALY", "title": "Edge Anomaly Detection",
                "subtitle": f"Edge[{primary_location}] flags OTP challenge failures", "status": "ACTIVE"
            })
            await asyncio.sleep(0.08)

        # Stage 4: Multi-account logins from single device
        for acc in target_accounts[1:4]:
            e_login = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.LOGIN,
                account_id=acc,
                device_id=rogue_device,
                location=primary_location,
                ip=rogue_ip,
                metadata={"status": "suspicious_credential_stuffing"}
            )
            await self.process_and_broadcast_event(e_login, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 4, "code": "INCIDENT_FORMATION", "title": "Incident Formation",
                "subtitle": f"Device {rogue_device} pivoting to multiple accounts", "status": "ACTIVE"
            })
            await asyncio.sleep(0.08)

        # Stage 5: Temporal Graph Expansion & New Recipient registration
        e_rec = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.NEW_RECIPIENT,
            account_id=target_accounts[0],
            device_id=rogue_device,
            recipient_id=mule_recipient,
            location=primary_location,
            ip=rogue_ip,
            metadata={"beneficiary": "unverified"}
        )
        await self.process_and_broadcast_event(e_rec, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 5, "code": "TEMPORAL_GRAPH", "title": "Temporal Financial Graph",
            "subtitle": f"Graph expands: Linked to recipient {mule_recipient}", "status": "ACTIVE"
        })
        await asyncio.sleep(0.1)

        # Stage 6: Threat DNA extraction with micro-test transaction
        e_test = FinancialEvent(
            event_id=self.next_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            type=EventType.TRANSACTION,
            account_id=target_accounts[0],
            device_id=rogue_device,
            recipient_id=mule_recipient,
            amount=100.0,
            location=primary_location,
            ip=rogue_ip,
            metadata={"note": "Micro-deposit validation test"}
        )
        await self.process_and_broadcast_event(e_test, is_attack=True, broadcast_graph=True)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 6, "code": "THREAT_DNA", "title": "Threat DNA Extraction",
            "subtitle": "Fingerprint: High velocity ATO pattern extracted", "status": "ACTIVE"
        })
        await asyncio.sleep(0.1)

        # Stage 7: Large Transfer + Escalation triggering Threat Propagation Forecast
        for acc in target_accounts[:3]:
            e_large = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=acc,
                device_id=rogue_device,
                recipient_id=mule_recipient,
                amount=round(random.uniform(180000, 420000), 2),
                location=primary_location,
                ip=rogue_ip,
                metadata={"channel": "IMPS_EXPRESS"}
            )
            await self.process_and_broadcast_event(e_large, is_attack=True, broadcast_graph=True)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": 7, "code": "PROPAGATION_FORECAST", "title": "Propagation Forecast",
                "subtitle": "NetworkX dynamic blast radius calculated across 15m/30m/60m", "status": "ACTIVE"
            })
            await asyncio.sleep(0.08)

        # Stage 8, 9, 10: Attack Simulation, Strategy Comparison, Recommended Action
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 8, "code": "ATTACK_SIMULATION", "title": "Attack Simulation",
            "subtitle": "Evaluating 5 containment strategies against live graph", "status": "ACTIVE"
        })
        await asyncio.sleep(0.1)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 9, "code": "INTERVENTION_COMPARISON", "title": "Intervention Comparison",
            "subtitle": "Trade-off analysis: Exposure reduction vs. customer friction", "status": "ACTIVE"
        })
        await asyncio.sleep(0.1)
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 10, "code": "RECOMMENDED_ACTION", "title": "Recommended Containment",
            "subtitle": "Recommend: Isolate Device & Step-Up Authentication", "status": "ACTIVE"
        })

    async def _run_mule_network_attack(self):
        """
        Scenario 2: Mule Network Expansion
        Pattern: Many Accounts -> Common Recipient -> Rapid Transactions -> Money Concentration
        """
        mule_recipient = f"REC-CONCENTRATOR-{random.randint(900, 999)}"
        mule_accounts = [f"ACC-MULE-{3000 + i}" for i in range(6)]
        cities = ["Mumbai", "Delhi", "Pune", "Bangalore"]

        for idx, acc in enumerate(mule_accounts):
            dev = f"DEV-NODE-{idx + 1}"
            loc = cities[idx % len(cities)]
            amt = round(random.uniform(95000, 240000), 2)
            e = FinancialEvent(
                event_id=self.next_event_id(),
                timestamp=datetime.utcnow().isoformat(),
                type=EventType.TRANSACTION,
                account_id=acc,
                device_id=dev,
                recipient_id=mule_recipient,
                amount=amt,
                location=loc,
                ip=f"10.24.{idx}.{random.randint(10, 90)}",
                metadata={"pattern": "fan_in_funnel"}
            )
            await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
            await asyncio.sleep(0.08)

    async def _run_merchant_attack(self):
        """
        Scenario 3: Merchant/Payment Attack
        Pattern: Multiple Merchants -> Payment Failures -> Retry Explosion -> Regional Degradation
        """
        attacker_acc = f"ACC-EXPLOIT-{random.randint(4000, 4999)}"
        attacker_dev = f"DEV-AUTO-{random.randint(800, 899)}"
        target_merchants = [f"MER-GATEWAY-{10 + i}" for i in range(4)]

        for mer in target_merchants:
            for _ in range(2):
                e = FinancialEvent(
                    event_id=self.next_event_id(),
                    timestamp=datetime.utcnow().isoformat(),
                    type=EventType.MERCHANT_PAYMENT,
                    account_id=attacker_acc,
                    device_id=attacker_dev,
                    merchant_id=mer,
                    amount=round(random.uniform(45000, 99000), 2),
                    location="Delhi",
                    ip="203.0.113.42",
                    metadata={"gateway_status": "CARD_VELOCITY_LIMIT"}
                )
                await self.process_and_broadcast_event(e, is_attack=True, broadcast_graph=True)
                await asyncio.sleep(0.08)

event_generator = EventGenerator()
