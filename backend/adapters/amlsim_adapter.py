import csv
import io
import time
import random
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import FinancialEvent, EventType

class AMLSimAdapter:
    """
    Adapter for IBM AMLSim (Anti-Money Laundering Simulation) datasets.
    Provides strict schema isolation: translates AMLSim synthetic transaction models
    (fan-in, fan-out, cycle, scatter-gather) into standard FinResolve FinancialEvent schemas
    without leaking external domain attributes into core anomaly/graph logic.
    """

    TYPE_MAPPING = {
        "TRANSFER": EventType.TRANSACTION,
        "PAYMENT": EventType.MERCHANT_PAYMENT,
        "CASH_OUT": EventType.TRANSACTION,
        "DEBIT": EventType.TRANSACTION,
        "CASH_IN": EventType.TRANSACTION
    }

    def convert_record(self, record: Dict[str, Any]) -> FinancialEvent:
        """
        Converts a single AMLSim record dictionary to FinResolve FinancialEvent.
        Expected AMLSim fields:
        step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
        nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud
        """
        raw_type = str(record.get("type", "TRANSFER")).upper()
        event_type = self.TYPE_MAPPING.get(raw_type, EventType.TRANSACTION)
        
        account_id = str(record.get("nameOrig", f"AML-ORIG-{random.randint(1000, 9999)}"))
        recipient_id = str(record.get("nameDest", f"AML-DEST-{random.randint(1000, 9999)}"))
        amount = float(record.get("amount", 0.0))
        is_fraud = int(record.get("isFraud", 0)) == 1

        # Synthesize device and location for FinResolve telemetry
        device_seed = abs(hash(account_id)) % 900 + 100
        device_id = record.get("device_id", f"DEV-AML-{device_seed}")
        location = record.get("location", "IN-MUM")
        ip = record.get("ip", f"10.50.{(device_seed % 250) + 1}.{random.randint(10, 240)}")

        step = record.get("step", 1)
        event_id = f"AML-{step}-{uuid.uuid4().hex[:8]}"

        return FinancialEvent(
            event_id=event_id,
            timestamp=datetime.utcnow().isoformat(),
            type=event_type,
            account_id=account_id,
            device_id=device_id,
            recipient_id=recipient_id,
            merchant_id=recipient_id if event_type == EventType.MERCHANT_PAYMENT else None,
            amount=amount,
            location=location,
            ip=ip,
            metadata={
                "source_dataset": "IBM_AMLSim",
                "amlsim_type": raw_type,
                "is_fraud_ground_truth": is_fraud,
                "old_balance_orig": float(record.get("oldbalanceOrg", 0.0)),
                "new_balance_orig": float(record.get("newbalanceOrig", 0.0)),
                "pattern_topology": record.get("pattern", "FAN_IN")
            }
        )

    def parse_csv(self, csv_text: str) -> List[FinancialEvent]:
        """Parses AMLSim CSV stream/text and yields FinResolve FinancialEvents."""
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        events = []
        for row in reader:
            events.append(self.convert_record(row))
        return events

    def generate_synthetic_stream(self, pattern: str = "fan_in", count: int = 25) -> List[FinancialEvent]:
        """
        Generates a high-fidelity synthetic AMLSim sequence demonstrating known money laundering topologies:
        - 'fan_in': Multiple feeder accounts channeling illicit funds to a central aggregator mule.
        - 'cycle': Circular flow (A -> B -> C -> D -> A) to disguise origin.
        - 'scatter_gather': Dispersal to 5 intermediary nodes, rapidly reconsolidated into high-risk sink.
        """
        events = []
        base_step = random.randint(100, 900)

        if pattern == "fan_in":
            # 8-15 distinct origin accounts sending bursts to target mule MULE_CENTRAL_88
            target_mule = f"MULE-REC-{random.randint(800, 899)}"
            for i in range(count):
                orig_acc = f"AML-SRC-{1000 + (i % 8)}"
                amt = round(random.uniform(45000.0, 98000.0), 2)
                rec = {
                    "step": base_step + i,
                    "type": "TRANSFER",
                    "amount": amt,
                    "nameOrig": orig_acc,
                    "oldbalanceOrg": amt + random.uniform(1000, 5000),
                    "newbalanceOrig": random.uniform(500, 1500),
                    "nameDest": target_mule,
                    "oldbalanceDest": random.uniform(20000, 80000),
                    "newbalanceDest": random.uniform(100000, 300000),
                    "isFraud": 1,
                    "pattern": "FAN_IN_AGGREGATOR"
                }
                events.append(self.convert_record(rec))

        elif pattern == "cycle":
            # Ring: A -> B -> C -> D -> A
            ring_nodes = [f"AML-RING-{n}" for n in ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON"]]
            ring_len = len(ring_nodes)
            amt = round(random.uniform(75000.0, 150000.0), 2)
            for i in range(count):
                src = ring_nodes[i % ring_len]
                dest = ring_nodes[(i + 1) % ring_len]
                rec = {
                    "step": base_step + i,
                    "type": "TRANSFER",
                    "amount": amt - (i * 250), # small structuring deduction
                    "nameOrig": src,
                    "oldbalanceOrg": amt * 1.5,
                    "newbalanceOrig": amt * 0.5,
                    "nameDest": dest,
                    "oldbalanceDest": amt * 0.2,
                    "newbalanceDest": amt * 1.2,
                    "isFraud": 1,
                    "pattern": "CIRCULAR_LAYERING"
                }
                events.append(self.convert_record(rec))

        elif pattern == "scatter_gather":
            # 1 Funder -> 4 Mules -> 1 Final Sink
            funder = "AML-FUNDER-01"
            intermediates = [f"AML-HOP-{k}" for k in range(1, 5)]
            final_sink = "AML-OFFSHORE-SINK"

            # Phase 1: Disperse (Scatter)
            for k, intermediate in enumerate(intermediates):
                amt = 85000.0
                rec = {
                    "step": base_step,
                    "type": "TRANSFER",
                    "amount": amt,
                    "nameOrig": funder,
                    "nameDest": intermediate,
                    "isFraud": 1,
                    "pattern": "SCATTER_DISPERSAL"
                }
                events.append(self.convert_record(rec))

            # Phase 2: Reconsolidate (Gather)
            for k, intermediate in enumerate(intermediates):
                amt = 84200.0
                rec = {
                    "step": base_step + 1,
                    "type": "TRANSFER",
                    "amount": amt,
                    "nameOrig": intermediate,
                    "nameDest": final_sink,
                    "isFraud": 1,
                    "pattern": "GATHER_CONSOLIDATION"
                }
                events.append(self.convert_record(rec))

        else: # Normal commercial flow
            for i in range(count):
                amt = round(random.uniform(500.0, 8500.0), 2)
                rec = {
                    "step": base_step + i,
                    "type": random.choice(["PAYMENT", "TRANSFER"]),
                    "amount": amt,
                    "nameOrig": f"AML-USER-{random.randint(100, 999)}",
                    "nameDest": f"AML-MERC-{random.randint(50, 99)}",
                    "isFraud": 0,
                    "pattern": "LEGITIMATE_COMMERCE"
                }
                events.append(self.convert_record(rec))

        return events

amlsim_adapter = AMLSimAdapter()
