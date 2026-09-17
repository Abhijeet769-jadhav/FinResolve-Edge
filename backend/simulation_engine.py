import math
from typing import List, Dict, Any, Optional
from models import SimulationResult, Incident
from propagation_engine import propagation_engine

class AttackSimulationEngine:
    def simulate_strategies(self, incident: Incident, horizon: str = "60m") -> List[SimulationResult]:
        """
        Dynamically simulates outcomes across 5 intervention strategies based on the incident's
        propagation forecast and graph topology, calculating containment scores and picking the optimal recommendation.
        """
        # Obtain current unmitigated baseline forecast
        forecast = propagation_engine.calculate_forecast(incident)
        
        # Pick target horizon
        target_h = next((h for h in forecast.horizons if h.label == horizon), forecast.horizons[-1])
        base_accounts = target_h.affected_accounts
        base_txns = target_h.transactions_at_risk
        base_exposure = target_h.estimated_exposure

        current_acc = len(incident.affected_accounts) or 1
        current_txn = len(incident.event_ids) or 1
        current_exposure = forecast.horizons[0].estimated_exposure

        # Dynamic simulation model parameters based on threat type
        is_operational = getattr(incident, 'is_operational', False) or any(k in incident.threat_type for k in ["Gateway", "Aggregator", "Degradation", "Outage", "Merchant Failure"])
        is_ato = "Takeover" in incident.threat_type
        is_mule = "Mule" in incident.threat_type
        is_merchant = "Merchant" in incident.threat_type

        # Strategy 1: NO_ACTION
        strat_no_action = SimulationResult(
            strategy="NO_ACTION",
            label="No Intervention (Passive Monitoring)",
            description="Allow current traffic patterns without containment. Cascading timeouts and failures accumulate unchecked." if is_operational else "Allow current traffic patterns without containment. Baseline exposure accumulates exponentially.",
            estimated_affected_accounts=base_accounts,
            estimated_transactions_at_risk=base_txns,
            estimated_financial_exposure=base_exposure,
            propagation="CRITICAL" if base_accounts >= 8 else "HIGH",
            customer_friction="LOW",
            containment_score=0.0
        )

        if is_operational:
            # Operational Playbook Strategies
            strat_reroute = SimulationResult(
                strategy="REROUTE_TRAFFIC",
                label="Reroute Payment Traffic (Secondary Ingress)",
                description="Immediately reroute transaction flow from degraded gateway to healthy backup settlement pipelines.",
                estimated_affected_accounts=math.ceil(base_accounts * 0.25),
                estimated_transactions_at_risk=math.ceil(base_txns * 0.20),
                estimated_financial_exposure=round(base_exposure * 0.18, 2),
                propagation="LOW",
                customer_friction="LOW",
                containment_score=89.5
            )

            strat_circuit = SimulationResult(
                strategy="CIRCUIT_BREAKER",
                label="Engage Adaptive Circuit Breaker",
                description="Temporarily rate-limit non-essential traffic and isolate failing aggregator endpoints to halt cascade.",
                estimated_affected_accounts=math.ceil(base_accounts * 0.35),
                estimated_transactions_at_risk=math.ceil(base_txns * 0.30),
                estimated_financial_exposure=round(base_exposure * 0.25, 2),
                propagation="LOW",
                customer_friction="MEDIUM",
                containment_score=84.0
            )

            strat_noc = SimulationResult(
                strategy="ALERT_OPERATIONS",
                label="Escalate to NOC & Health Check Probe",
                description="Dispatch urgent P1 alert to Site Reliability Engineering with automated health probe telemetry.",
                estimated_affected_accounts=math.ceil(base_accounts * 0.50),
                estimated_transactions_at_risk=math.ceil(base_txns * 0.45),
                estimated_financial_exposure=round(base_exposure * 0.40, 2),
                propagation="MEDIUM",
                customer_friction="LOW",
                containment_score=68.0
            )

            strat_combined_op = SimulationResult(
                strategy="COMBINED",
                label="Coordinated Resilience (Reroute + Breaker + NOC)",
                description="Multi-layered operational response: Instant secondary reroute, edge circuit breaker, and automated NOC alert.",
                estimated_affected_accounts=current_acc,
                estimated_transactions_at_risk=current_txn + 1,
                estimated_financial_exposure=round(current_exposure + 2000, 2),
                propagation="LOW",
                customer_friction="LOW",
                containment_score=98.2
            )

            all_strategies = [
                strat_no_action,
                strat_reroute,
                strat_circuit,
                strat_noc,
                strat_combined_op
            ]
            best_strat = max(all_strategies, key=lambda s: s.containment_score)
            best_strat.is_recommended = True
            exp_red = round(((base_exposure - best_strat.estimated_financial_exposure) / max(base_exposure, 1)) * 100, 1)
            best_strat.recommendation_reason = (
                f"Mitigates {exp_red}% of downtime exposure (protecting ₹{base_exposure - best_strat.estimated_financial_exposure:,.0f}), "
                f"restores service availability while maintaining minimal customer friction."
            )
            return all_strategies

        # Strategy 2: BLOCK_DEVICE
        # Highly effective for ATO with single device, less effective if mule or distributed
        if is_ato:
            acc_b = current_acc + 1
            txn_b = current_txn + 3
            exp_b = round(current_exposure + 35000, 2)
            prop_b = "LOW"
            fric_b = "LOW"
            contain_b = 88.0
        elif is_mule:
            acc_b = math.ceil(base_accounts * 0.65)
            txn_b = math.ceil(base_txns * 0.60)
            exp_b = round(base_exposure * 0.62, 2)
            prop_b = "MEDIUM"
            fric_b = "LOW"
            contain_b = 52.0
        else: # Merchant attack
            acc_b = math.ceil(base_accounts * 0.45)
            txn_b = math.ceil(base_txns * 0.40)
            exp_b = round(base_exposure * 0.45, 2)
            prop_b = "MEDIUM"
            fric_b = "MEDIUM"
            contain_b = 68.0

        strat_block_device = SimulationResult(
            strategy="BLOCK_DEVICE",
            label="Isolate Suspicious Device",
            description="Block incoming telemetry and authorization attempts from identified rogue hardware fingerprint.",
            estimated_affected_accounts=acc_b,
            estimated_transactions_at_risk=txn_b,
            estimated_financial_exposure=exp_b,
            propagation=prop_b,
            customer_friction=fric_b,
            containment_score=contain_b
        )

        # Strategy 3: HOLD_RECIPIENT
        # Extremely effective for Mule networks, moderate for ATO
        if is_mule:
            acc_c = current_acc + 1
            txn_c = current_txn + 2
            exp_c = round(current_exposure + 15000, 2)
            prop_c = "LOW"
            fric_c = "LOW"
            contain_c = 93.0
        elif is_ato:
            acc_c = math.ceil(base_accounts * 0.55)
            txn_c = math.ceil(base_txns * 0.50)
            exp_c = round(base_exposure * 0.48, 2)
            prop_c = "MEDIUM"
            fric_c = "MEDIUM"
            contain_c = 64.0
        else:
            acc_c = math.ceil(base_accounts * 0.70)
            txn_c = math.ceil(base_txns * 0.65)
            exp_c = round(base_exposure * 0.68, 2)
            prop_c = "HIGH"
            fric_c = "LOW"
            contain_c = 44.0

        strat_hold_recipient = SimulationResult(
            strategy="HOLD_RECIPIENT",
            label="Freeze Mule Recipient Account",
            description="Temporarily freeze beneficiary credit settlement and place outbound transfers on hold.",
            estimated_affected_accounts=acc_c,
            estimated_transactions_at_risk=txn_c,
            estimated_financial_exposure=exp_c,
            propagation=prop_c,
            customer_friction=fric_c,
            containment_score=contain_c
        )

        # Strategy 4: STEP_UP_AUTH
        # Adds verification layer across cluster; moderate containment, higher friction
        acc_d = math.ceil(base_accounts * 0.35)
        txn_d = math.ceil(base_txns * 0.30)
        exp_d = round(base_exposure * 0.32, 2)
        prop_d = "LOW"
        fric_d = "HIGH"
        contain_d = 76.0

        strat_step_up = SimulationResult(
            strategy="STEP_UP_AUTH",
            label="Cluster-Wide Step-Up Authentication",
            description="Force biometric / hardware-token re-authentication for all linked accounts in blast radius.",
            estimated_affected_accounts=acc_d,
            estimated_transactions_at_risk=txn_d,
            estimated_financial_exposure=exp_d,
            propagation=prop_d,
            customer_friction=fric_d,
            containment_score=contain_d
        )

        # Strategy 5: COMBINED (Dynamic combination based on scenario)
        if is_ato:
            combo_name = "Device Isolation + Step-Up Auth"
            acc_e = current_acc
            txn_e = current_txn + 1
            exp_e = round(current_exposure + 5000, 2)
            prop_e = "LOW"
            fric_e = "MEDIUM"
            contain_e = 96.5
        elif is_mule:
            combo_name = "Hold Recipient + Gateway Rate Limit"
            acc_e = current_acc
            txn_e = current_txn + 1
            exp_e = round(current_exposure + 3000, 2)
            prop_e = "LOW"
            fric_e = "LOW"
            contain_e = 97.8
        else:
            combo_name = "Merchant Terminal Hold + Step-Up Auth"
            acc_e = current_acc + 1
            txn_e = current_txn + 2
            exp_e = round(current_exposure + 12000, 2)
            prop_e = "LOW"
            fric_e = "MEDIUM"
            contain_e = 94.0

        strat_combined = SimulationResult(
            strategy="COMBINED",
            label=f"Coordinated Response ({combo_name})",
            description=f"Multi-layered defense combining entity isolation and adaptive friction checks.",
            estimated_affected_accounts=acc_e,
            estimated_transactions_at_risk=txn_e,
            estimated_financial_exposure=exp_e,
            propagation=prop_e,
            customer_friction=fric_e,
            containment_score=contain_e
        )

        all_strategies = [
            strat_no_action,
            strat_block_device,
            strat_hold_recipient,
            strat_step_up,
            strat_combined
        ]

        # Dynamically determine the best recommendation based on score and trade-offs
        # Filter strategies with highest containment score
        best_strat = max(all_strategies, key=lambda s: s.containment_score)
        best_strat.is_recommended = True

        exposure_reduction_pct = round(((base_exposure - best_strat.estimated_financial_exposure) / max(base_exposure, 1)) * 100, 1)
        account_protection_pct = round(((base_accounts - best_strat.estimated_affected_accounts) / max(base_accounts, 1)) * 100, 1)

        best_strat.recommendation_reason = (
            f"Reduces financial exposure by {exposure_reduction_pct}% (saving ₹{base_exposure - best_strat.estimated_financial_exposure:,.0f}), "
            f"prevents {account_protection_pct}% of account propagation, while keeping customer friction at '{best_strat.customer_friction}'."
        )

        return all_strategies

simulation_engine = AttackSimulationEngine()
