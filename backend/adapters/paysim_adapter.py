import csv
import io
import time
import random
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import FinancialEvent, EventType

class PaySimAdapter:
    """
    Adapter for PaySim mobile money transaction datasets.
    Provides strict schema isolation: translates PaySim transaction records
    (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER) into FinResolve FinancialEvent schemas.
    """

    TYPE_MAPPING = {
        "PAYMENT": EventType.MERCHANT_PAYMENT,
        "TRANSFER": EventType.TRANSACTION,
        "CASH_OUT": EventType.TRANSACTION,
        "DEBIT": EventType.TRANSACTION,
        "CASH_IN": EventType.TRANSACTION
    }

    def convert_record(self, record: Dict[str, Any]) -> FinancialEvent:
        """
        Converts a single PaySim record dictionary to FinResolve FinancialEvent.
        Expected fields:
        step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
        nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud
        """
        raw_type = str(record.get("type", "PAYMENT")).upper()
        event_type = self.TYPE_MAPPING.get(raw_type, EventType.TRANSACTION)

        account_id = str(record.get("nameOrig", f"C{random.randint(10000000, 99999999)}"))
        recipient_id = str(record.get("nameDest", f"M{random.randint(10000000, 99999999)}"))
        amount = float(record.get("amount", 0.0))
        is_fraud = int(record.get("isFraud", 0)) == 1

        device_seed = abs(hash(account_id)) % 800 + 100
        device_id = record.get("device_id", f"DEV-PAY-{device_seed}")
        location = record.get("location", "IN-DEL")
        ip = record.get("ip", f"192.0.2.{(device_seed % 250) + 1}")

        step = record.get("step", 1)
        event_id = f"PYS-{step}-{uuid.uuid4().hex[:8]}"

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
                "source_dataset": "PaySim_MobileMoney",
                "paysim_type": raw_type,
                "is_fraud_ground_truth": is_fraud,
                "old_balance_orig": float(record.get("oldbalanceOrg", 0.0)),
                "new_balance_orig": float(record.get("newbalanceOrig", 0.0)),
                "old_balance_dest": float(record.get("oldbalanceDest", 0.0)),
                "new_balance_dest": float(record.get("newbalanceDest", 0.0))
            }
        )

    def parse_csv(self, csv_text: str) -> List[FinancialEvent]:
        """Parses PaySim CSV stream/text and yields FinResolve FinancialEvents."""
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        events = []
        for row in reader:
            events.append(self.convert_record(row))
        return events

    def generate_synthetic_stream(self, pattern: str = "transfer_cashout_drain", count: int = 20) -> List[FinancialEvent]:
        """
        Generates PaySim synthetic sequences:
        - 'transfer_cashout_drain': Classic PaySim fraud vector (Victim account balance transferred, then cashed out via agent).
        - 'rapid_payment_burst': Normal commercial high-volume micro-payments.
        """
        events = []
        base_step = random.randint(50, 400)

        if pattern == "transfer_cashout_drain":
            # For each victim, execute TRANSFER of entirety of funds, followed by CASH_OUT
            for i in range(count // 2):
                victim_id = f"C{random.randint(11111111, 44444444)}"
                mule_id = f"C{random.randint(55555555, 88888888)}"
                cashout_merchant = f"M{random.randint(90000000, 99999999)}"
                drain_amount = round(random.uniform(180000.0, 450000.0), 2)

                # Step 1: Fraudulent Transfer draining victim balance
                transfer_rec = {
                    "step": base_step + i,
                    "type": "TRANSFER",
                    "amount": drain_amount,
                    "nameOrig": victim_id,
                    "oldbalanceOrg": drain_amount,
                    "newbalanceOrig": 0.0,
                    "nameDest": mule_id,
                    "oldbalanceDest": 0.0,
                    "newbalanceDest": drain_amount,
                    "isFraud": 1
                }
                events.append(self.convert_record(transfer_rec))

                # Step 2: Fraudulent Cash-Out liquidation
                cashout_rec = {
                    "step": base_step + i,
                    "type": "CASH_OUT",
                    "amount": drain_amount,
                    "nameOrig": mule_id,
                    "oldbalanceOrg": drain_amount,
                    "newbalanceOrig": 0.0,
                    "nameDest": cashout_merchant,
                    "oldbalanceDest": 50000.0,
                    "newbalanceDest": 50000.0 + drain_amount,
                    "isFraud": 1
                }
                events.append(self.convert_record(cashout_rec))

        else: # Normal payment burst
            for i in range(count):
                amt = round(random.uniform(120.0, 3500.0), 2)
                rec = {
                    "step": base_step + i,
                    "type": "PAYMENT",
                    "amount": amt,
                    "nameOrig": f"C{random.randint(10000000, 99999999)}",
                    "oldbalanceOrg": amt + random.uniform(500, 10000),
                    "newbalanceOrig": random.uniform(500, 10000),
                    "nameDest": f"M{random.randint(10000000, 99999999)}",
                    "oldbalanceDest": 0.0,
                    "newbalanceDest": 0.0,
                    "isFraud": 0
                }
                events.append(self.convert_record(rec))

        return events

paysim_adapter = PaySimAdapter()
