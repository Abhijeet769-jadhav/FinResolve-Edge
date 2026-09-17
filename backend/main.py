import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from models import (
    SimulateRequest, ResponseActionRequest, InjectAttackRequest,
    Incident, ThreatDNA, PropagationForecast, SimulationResult
)
from websocket_manager import ws_manager
from graph_engine import graph_engine
from anomaly_engine import anomaly_engine
from threat_dna import threat_dna_engine
from propagation_engine import propagation_engine
from simulation_engine import simulation_engine
from response_engine import response_engine
from event_generator import event_generator
from telemetry import telemetry_tracker
from pqc_lab import pqc_lab
from adapters import amlsim_adapter, paysim_adapter
from load_test_engine import load_test_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("finresolve.main")

background_task = None
telemetry_task = None

async def telemetry_ticker_loop():
    """Broadcasts 1-second aggregated metrics (events/sec, anomalies/sec, risk, exposure) for static charting."""
    while True:
        try:
            await asyncio.sleep(1.0)
            incidents = anomaly_engine.get_all_incidents()
            active_inc = next((i for i in incidents if i.status == "ACTIVE"), None)
            point = telemetry_tracker.tick(active_incident=active_inc)
            point["edge_counters"] = anomaly_engine.edge_counters
            if load_test_engine.is_running:
                point["load_test"] = load_test_engine.get_status()
            await ws_manager.broadcast("telemetry_tick", point)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.debug(f"Telemetry tick error: {e}")

AUTO_SCENARIOS = [
    "mule_network",
    "weak_signals",
    "coordinated_fraud",
    "recipient_attack",
    "credential_stuffing",
    "account_takeover"
]
_auto_scenario_idx = 0

def get_next_auto_scenario() -> str:
    global _auto_scenario_idx
    scenario = AUTO_SCENARIOS[_auto_scenario_idx % len(AUTO_SCENARIOS)]
    _auto_scenario_idx += 1
    return scenario

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start synthetic event generator background task
    global background_task, telemetry_task
    logger.info("FinResolve Predict backend initializing...")
    background_task = asyncio.create_task(event_generator.start())
    telemetry_task = asyncio.create_task(telemetry_ticker_loop())
    yield
    # Shutdown
    logger.info("FinResolve Predict backend shutting down...")
    event_generator.stop()
    if background_task:
        background_task.cancel()
    if telemetry_task:
        telemetry_task.cancel()

app = FastAPI(
    title="FinResolve Predict API",
    description="Real-Time Financial Threat Detection & Attack Simulation Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FinResolve Predict",
        "version": "1.0.0",
        "pqc_integrity": "ML-DSA-65 (Demonstrational Abstraction Active)"
    }

@app.get("/api/events")
async def get_events(limit: int = 50):
    """Returns recent financial events."""
    events = event_generator.recent_events[:limit]
    return [e.model_dump() for e in events]

@app.get("/api/stream/status")
async def get_stream_status():
    """Returns continuous background event injection stream status."""
    return {
        "is_running": event_generator.is_running,
        "is_paused": getattr(event_generator, 'is_paused', False),
        "attack_in_progress": event_generator.attack_in_progress,
        "total_events": event_generator.event_counter - 10000,
        "target_eps": 12.5
    }

@app.post("/api/stream/resume")
async def resume_stream():
    """Resumes continuous background event generation."""
    event_generator.resume()
    if not event_generator.is_running:
        asyncio.create_task(event_generator.start())
    return {"status": "STREAM_RESUMED", "is_running": True, "is_paused": False}

@app.post("/api/stream/pause")
async def pause_stream():
    """Pauses continuous background event generation."""
    event_generator.pause()
    return {"status": "STREAM_PAUSED", "is_running": True, "is_paused": True}

@app.post("/api/stream/inject-batch")
async def inject_batch(count: int = Query(15, ge=1, le=100)):
    """Injects a batch of continuous benign financial events immediately."""
    events = []
    for _ in range(count):
        evt = event_generator.generate_benign_event()
        await event_generator.process_and_broadcast_event(evt, broadcast_graph=False)
        events.append(evt.model_dump())
    return {"status": "BATCH_INJECTED", "count": len(events)}

@app.get("/api/incidents")
async def get_incidents():
    """Returns all incidents sorted by recency."""
    incidents = anomaly_engine.get_all_incidents()
    return [i.model_dump() for i in incidents]

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Returns details for a single incident."""
    inc = anomaly_engine.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc.model_dump()

@app.post("/api/incidents/reset")
async def reset_incidents():
    """Resets all incidents, correlation structures, and graph state to clean baseline."""
    anomaly_engine.reset_incidents()
    graph_engine.clear()
    event_generator.resume()
    await ws_manager.broadcast("incidents_reset", {"message": "All incidents and graph states reset"})
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 1,
        "code": "BASELINE",
        "title": "Baseline Financial Flow",
        "subtitle": "System baseline restored. Zero active threats.",
        "status": "NORMAL"
    })
    return {"status": "SUCCESS", "message": "Incidents and graph reset to clean baseline"}

@app.get("/api/graph")
async def get_graph(incident_id: Optional[str] = None):
    """Returns graph representation formatted for React Flow."""
    focus_nodes = None
    if incident_id:
        inc = anomaly_engine.get_incident(incident_id)
        if inc:
            focus_nodes = inc.affected_accounts + inc.affected_devices + inc.affected_recipients
    else:
        # Default to latest active or contained incident so topology always has prime focus
        all_inc = anomaly_engine.get_all_incidents()
        if all_inc:
            latest = all_inc[0]
            focus_nodes = latest.affected_accounts + latest.affected_devices + latest.affected_recipients

    return graph_engine.to_react_flow(focus_nodes=focus_nodes)

@app.get("/api/threat-dna/{incident_id}")
async def get_threat_dna(incident_id: str):
    """Calculates and returns the Threat DNA for an incident."""
    inc = anomaly_engine.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    dna = threat_dna_engine.extract_threat_dna(inc)
    return dna.model_dump()

@app.get("/api/forecast/{incident_id}")
async def get_forecast(incident_id: str):
    """Calculates dynamic propagation forecast across 15m, 30m, 60m horizons."""
    inc = anomaly_engine.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    forecast = propagation_engine.calculate_forecast(inc)
    return forecast.model_dump()

@app.post("/api/simulate")
async def simulate_attack(req: SimulateRequest):
    """Runs simulation across 5 intervention strategies for an incident."""
    inc = anomaly_engine.get_incident(req.incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    results = simulation_engine.simulate_strategies(inc, horizon=req.horizon)
    await ws_manager.broadcast("simulation_completed", {
        "incident_id": inc.id,
        "results": [r.model_dump() for r in results]
    })
    return [r.model_dump() for r in results]

@app.post("/api/response/approve")
async def approve_response(req: ResponseActionRequest):
    """Human analyst approves containment response. Updates actual backend state."""
    inc = anomaly_engine.get_incident(req.incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = response_engine.execute_approval(inc, req)
    logger.info(f"approve_response: incident_id={req.incident_id}, strategy={req.strategy}, source={req.source}, auto_spawn_next={getattr(req, 'auto_spawn_next', True)}")

    # If PQC key revocation, update quantum tamper entity in canonical graph
    if "PQC" in req.strategy or "LATTICE" in req.strategy or "KEY_REVOCATION" in req.strategy:
        graph_engine.update_pqc_tamper(10000.0, 1000000.0, is_contained=True)

    # Broadcast updates across WebSockets
    await ws_manager.broadcast("response_approved", result)
    await ws_manager.broadcast("incident_contained", {
        "incident_id": inc.id,
        "status": "CONTAINED",
        "action": result
    })

    # Broadcast live workflow stage 11 & 12
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 11,
        "code": "HUMAN_APPROVAL",
        "title": "Human Approval",
        "subtitle": f"Analyst APPROVED {req.strategy}",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 12,
        "code": "RESPONSE_EXECUTION",
        "title": "Response Execution",
        "subtitle": "Network isolation policy deployed to gateways",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 13,
        "code": "INCIDENT_RESOLUTION",
        "title": "Real-Time Incident Resolution",
        "subtitle": f"Threat {inc.id} contained successfully",
        "status": "CONTAINED"
    })

    # Broadcast updated canonical graph with contained states
    focus_nodes = inc.affected_accounts + inc.affected_devices + inc.affected_recipients + ["ADV-QUANTUM-MITM"]
    rf_graph = graph_engine.to_react_flow(focus_nodes=focus_nodes)
    await ws_manager.broadcast("graph_updated", rf_graph)

    # Record snapshot for Replay Attack feature
    graph_engine.record_attack_snapshot(inc.id, f"SOC Analyst Approved {req.strategy} -> THREAT CONTAINED", {"action": result})

    # Auto-spawn next incident if not from test lab or manual attack trigger
    should_spawn = getattr(req, "auto_spawn_next", True) and req.source not in ["testlab", "attack_trigger"]
    if should_spawn:
        async def schedule_next_incident_arrival():
            try:
                # Wait 9.0 seconds for containment stabilization before new threat arrives
                # Allows analyst to clearly observe green/yellow/red containment posture and connected edges
                await asyncio.sleep(9.0)
                next_scenario = get_next_auto_scenario()
                logger.info(f"Auto-arrival: Spawning next incoming threat scenario '{next_scenario}' post-approval")
                await event_generator.inject_attack_scenario(next_scenario)
            except Exception as ex:
                logger.error(f"Failed to auto-spawn next incident: {ex}")

        asyncio.create_task(schedule_next_incident_arrival())

    return {"status": "SUCCESS", "action": result, "incident": inc.model_dump(), "auto_spawn": should_spawn}

@app.post("/api/response/reject")
async def reject_response(req: ResponseActionRequest):
    """Human analyst rejects containment response."""
    inc = anomaly_engine.get_incident(req.incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = response_engine.execute_rejection(inc, req)
    await ws_manager.broadcast("response_rejected", result)
    return {"status": "REJECTED", "action": result, "incident": inc.model_dump()}

@app.post("/api/demo/inject-attack")
async def inject_attack(req: InjectAttackRequest):
    """Triggers coordinated synthetic attack sequence."""
    asyncio.create_task(event_generator.inject_attack_scenario(req.scenario))
    return {
        "status": "ATTACK_SEQUENCE_INITIATED",
        "scenario": req.scenario,
        "message": "Watch live workflow and real-time event stream"
    }

@app.get("/api/system-status")
async def get_system_status():
    """Returns status of edge nodes, processing engines, and PQC verification."""
    data = anomaly_engine.get_system_status_data()
    
    # Calculate live aggregate statistics
    all_incidents = anomaly_engine.get_all_incidents()
    active_incidents = [i for i in all_incidents if i.status == "ACTIVE"]
    total_acc_at_risk = len(set([acc for i in active_incidents for acc in i.affected_accounts]))
    total_exposure = sum([
        sum([graph_engine.graph.nodes[e].get("amount", 0.0) for e in i.event_ids if graph_engine.graph.has_node(e)])
        for i in active_incidents
    ])

    data["metrics"] = {
        "total_events": event_generator.event_counter - 10000,
        "active_incidents": len(active_incidents),
        "accounts_at_risk": total_acc_at_risk,
        "total_exposure": round(total_exposure, 2)
    }
    data["telemetry_history"] = telemetry_tracker.history
    return data

# ==========================================
# PHASE 2: EDGE SIMULATION ENDPOINTS
# ==========================================
@app.get("/api/edge/nodes")
async def get_edge_nodes():
    """Returns real-time status, buffers, and metrics for all edge nodes."""
    return anomaly_engine.edge_node_stats

@app.get("/api/edge/counters")
async def get_edge_counters():
    """Returns the 4 global Edge funnel counters."""
    return anomaly_engine.edge_counters

@app.post("/api/edge/{node_name}/disconnect")
async def disconnect_edge_node(node_name: str):
    """Simulates edge node disconnection, buffering events locally, and forms an Operational Incident."""
    res = anomaly_engine.disconnect_edge_node(node_name)
    inc = anomaly_engine.create_edge_partition_incident(node_name)

    # Mutate canonical graph state
    graph_engine.update_edge_resiliency(node_name, is_disconnected=True, stats=res)
    rf_graph = graph_engine.to_react_flow(focus_nodes=[f"EDGE-{node_name.upper()}", f"GATEWAY-{node_name.upper()}", "GATEWAY-PUNE"])
    await ws_manager.broadcast("graph_updated", rf_graph)
    graph_engine.record_attack_snapshot(inc.id, f"Regional Edge Partition: {node_name} Outage", {"status": "PARTITIONED"})

    await ws_manager.broadcast("edge_node_updated", res)
    await ws_manager.broadcast("incident_created", {"incident": inc.model_dump()})
    await ws_manager.broadcast("emergency_alert", {
        "incident_id": inc.id,
        "threat_type": inc.threat_type,
        "severity": inc.severity,
        "risk_score": inc.risk_score,
        "affected_accounts": inc.affected_accounts,
        "affected_devices": inc.affected_devices,
        "affected_recipients": inc.affected_recipients,
        "scenario": f"Edge Node Partition ({node_name})",
        "recommended_action": inc.recommended_action
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 2,
        "code": "EDGE_ANOMALY",
        "title": "Edge Autonomous Anomaly",
        "subtitle": f"{node_name} Node Link Partitioned - Local buffer active",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 3,
        "code": "INCIDENT_FORMATION",
        "title": "Incident Formation",
        "subtitle": f"{inc.id}: Operational Outage on {node_name}",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 10,
        "code": "RECOMMENDED_ACTION",
        "title": "Recommended Action",
        "subtitle": f"Autonomous Edge Failover & Regional Secondary Routing ({node_name})",
        "status": "COMPLETED"
    })
    return {**res, "incident": inc.model_dump()}

@app.post("/api/edge/{node_name}/reconnect")
async def reconnect_edge_node(node_name: str):
    """Simulates edge node reconnection, flushing buffered events to central, and resolving incident."""
    res = anomaly_engine.reconnect_and_sync_edge_node(node_name)

    # Mutate canonical graph state
    graph_engine.update_edge_resiliency(node_name, is_disconnected=False, stats=res)
    rf_graph = graph_engine.to_react_flow(focus_nodes=[f"EDGE-{node_name.upper()}", f"GATEWAY-{node_name.upper()}", "GATEWAY-PUNE"])
    await ws_manager.broadcast("graph_updated", rf_graph)

    # Find active edge partition incident for this node and contain it
    for inc in anomaly_engine.get_all_incidents():
        if inc.status == "ACTIVE" and ("Edge" in inc.threat_type or node_name in str(inc.affected_devices)):
            inc.status = "CONTAINED"
            await ws_manager.broadcast("incident_contained", {
                "incident_id": inc.id,
                "status": "CONTAINED",
                "action": {"strategy": "FAILOVER_REROUTE", "status": "SYNCED_AND_RESOLVED"}
            })

    await ws_manager.broadcast("edge_node_updated", res)
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 13,
        "code": "INCIDENT_RESOLUTION",
        "title": "Incident Resolution",
        "subtitle": f"{node_name} reconnected & {res.get('synced_events', 0)} buffered events synchronized",
        "status": "COMPLETED"
    })
    return res

# ==========================================
# PHASE 3: POST-QUANTUM CRYPTOGRAPHY LAB
# ==========================================
@app.get("/api/pqc/info")
async def get_pqc_info():
    """Returns algorithm suite details (ML-DSA-65, ML-KEM-768, AES-256-GCM, SHA-384)."""
    return pqc_lab.algorithm_suite

@app.post("/api/pqc/test-valid")
async def test_pqc_valid(amount: float = Query(10000.0)):
    """Runs end-to-end PQC verification on an untampered transaction."""
    res = pqc_lab.run_valid_test(amount=amount)
    return res

@app.post("/api/pqc/test-tamper")
async def test_pqc_tamper(original_amount: float = Query(10000.0), tampered_amount: float = Query(1000000.0)):
    """Runs PQC tamper test (₹10K -> ₹10L), creates SEV-1 incident, and broadcasts emergency alert."""
    res = pqc_lab.run_tamper_test(original_amount=original_amount, tampered_amount=tampered_amount)

    # Create SEV-1 Cryptographic Integrity Incident in anomaly engine
    inc = anomaly_engine.create_pqc_tamper_incident(original_amount, tampered_amount)

    # Mutate canonical graph state: A101 -> D45 -> ADV-QUANTUM-MITM -> TXN-PQC-TAMPER -> R900
    graph_engine.update_pqc_tamper(original_amount, tampered_amount, is_contained=False)
    rf_graph = graph_engine.to_react_flow(focus_nodes=["ACC-A101", "DEV-D45", "ADV-QUANTUM-MITM", "TXN-PQC-TAMPER", "REC-R900"])
    await ws_manager.broadcast("graph_updated", rf_graph)
    graph_engine.record_attack_snapshot(inc.id, "Simulated Adversarial Payload Tampering (ML-DSA-65 Failure)", {
        "original_amount": original_amount,
        "tampered_amount": tampered_amount
    })

    await ws_manager.broadcast("incident_created", {"incident": inc.model_dump()})
    await ws_manager.broadcast("emergency_alert", {
        "incident_id": inc.id,
        "threat_type": inc.threat_type,
        "severity": inc.severity,
        "risk_score": inc.risk_score,
        "affected_accounts": inc.affected_accounts,
        "affected_devices": inc.affected_devices,
        "affected_recipients": inc.affected_recipients,
        "scenario": "Simulated Adversarial Payload Tampering",
        "recommended_action": inc.recommended_action
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 2,
        "code": "EDGE_ANOMALY",
        "title": "Edge Anomaly Detection",
        "subtitle": "SHA-384 Digest Mismatch & ML-DSA-65 Signature Failure",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 3,
        "code": "INCIDENT_FORMATION",
        "title": "Incident Formation",
        "subtitle": f"{inc.id}: Quantum Layer Payload Tamper (₹{original_amount:,.0f} -> ₹{tampered_amount:,.0f})",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 5,
        "code": "THREAT_DNA",
        "title": "Threat DNA Extraction",
        "subtitle": "Simulated Adversarial Payload Tampering Profile",
        "status": "COMPLETED"
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 10,
        "code": "RECOMMENDED_ACTION",
        "title": "Recommended Action",
        "subtitle": "Lattice Session Key Revocation & Ingress Severance",
        "status": "COMPLETED"
    })

    return {**res, "incident": inc.model_dump()}

# ==========================================
# PHASE 4: DATASET ADAPTERS (AMLSim & PaySim)
# ==========================================
async def _replay_adapter_stream(events: List[Any], dataset_name: str, pattern: str, delay_sec: float = 0.08):
    await ws_manager.broadcast("attack_started", {
        "scenario_id": f"{dataset_name.lower()}_{pattern}",
        "scenario_name": f"{dataset_name} Stream Replay ({pattern.upper()})",
        "severity": "CRITICAL" if pattern != "normal" else "LOW",
        "message": f"Replaying {len(events)} synthetic transactions from {dataset_name} ({pattern.upper()})."
    })
    await ws_manager.broadcast("workflow_stage_update", {
        "stage_id": 1,
        "code": "EVENT_INGESTION",
        "title": "Real-Time Event Ingestion",
        "subtitle": f"Ingesting {len(events)} events from {dataset_name}",
        "status": "COMPLETED"
    })

    created_incident = None
    stream_entities = set()
    for idx, evt in enumerate(events):
        rep, sig, inc = anomaly_engine.evaluate_event(evt)
        graph_engine.add_event(evt, risk_level=rep.classification, anomaly_reasons=rep.reasons)
        stream_entities.add(evt.account_id)
        if evt.recipient_id:
            stream_entities.add(evt.recipient_id)
        if inc and not created_incident:
            created_incident = inc

        await ws_manager.broadcast("new_event", {
            "event": evt.model_dump(),
            "anomaly": rep.model_dump(),
            "signal": sig.model_dump() if sig else None
        })

        # Periodic real-time graph update during stream replay (every 3 events or last event)
        if idx % 3 == 0 or idx == len(events) - 1:
            rf_graph = graph_engine.to_react_flow(focus_nodes=list(stream_entities))
            await ws_manager.broadcast("graph_updated", rf_graph)

        await asyncio.sleep(delay_sec)

    # Final cohesive graph update
    rf_graph = graph_engine.to_react_flow(focus_nodes=list(stream_entities))
    await ws_manager.broadcast("graph_updated", rf_graph)

    if created_incident:
        graph_engine.record_attack_snapshot(
            created_incident.id, 
            f"{dataset_name} Stream Replay ({pattern.upper()})",
            {"events_count": len(events), "entities": len(stream_entities)}
        )
        await ws_manager.broadcast("incident_created", {"incident": created_incident.model_dump()})
        await ws_manager.broadcast("emergency_alert", {
            "incident_id": created_incident.id,
            "threat_type": created_incident.threat_type,
            "severity": created_incident.severity,
            "risk_score": created_incident.risk_score,
            "affected_accounts": created_incident.affected_accounts,
            "affected_devices": created_incident.affected_devices,
            "affected_recipients": created_incident.affected_recipients,
            "scenario": f"{dataset_name} ({pattern.upper()})",
            "recommended_action": created_incident.recommended_action
        })
        for st, title, sub in [
            (3, "Incident Formation", f"{created_incident.id}: {created_incident.threat_type}"),
            (4, "Temporal Graph", f"Graph enriched with {len(created_incident.affected_accounts)} accounts"),
            (5, "Threat DNA", "Multi-Entity Coordinated Topology Extracted"),
            (10, "Recommended Action", created_incident.recommended_action.get("label", "Coordinated Response") if created_incident.recommended_action else "Coordinated Isolation")
        ]:
            await asyncio.sleep(0.08)
            await ws_manager.broadcast("workflow_stage_update", {
                "stage_id": st,
                "code": f"STAGE_{st}",
                "title": title,
                "subtitle": sub,
                "status": "COMPLETED"
            })

@app.post("/api/adapters/amlsim/replay")
async def replay_amlsim(pattern: str = Query("fan_in"), count: int = Query(20)):
    """Replays synthetic IBM AMLSim topology (fan_in, cycle, scatter_gather, normal)."""
    events = amlsim_adapter.generate_synthetic_stream(pattern=pattern, count=count)
    asyncio.create_task(_replay_adapter_stream(events, "IBM_AMLSim", pattern))
    return {
        "status": "REPLAY_STARTED",
        "dataset": "IBM_AMLSim",
        "pattern": pattern,
        "events_count": len(events),
        "schema_isolation": "Strict: Converted to FinancialEvent without leaking external fields"
    }

@app.post("/api/adapters/paysim/replay")
async def replay_paysim(pattern: str = Query("transfer_cashout_drain"), count: int = Query(20)):
    """Replays synthetic PaySim mobile money fraud or payment burst."""
    events = paysim_adapter.generate_synthetic_stream(pattern=pattern, count=count)
    asyncio.create_task(_replay_adapter_stream(events, "PaySim_MobileMoney", pattern))
    return {
        "status": "REPLAY_STARTED",
        "dataset": "PaySim_MobileMoney",
        "pattern": pattern,
        "events_count": len(events),
        "schema_isolation": "Strict: Converted to FinancialEvent without leaking external fields"
    }

# ==========================================
# PHASE 5: LOAD TESTING ENGINE
# ==========================================
@app.post("/api/load-test/start")
async def start_load_test(tier: int = Query(100)):
    """Starts high-throughput load test at tier (10, 100, 1000, 5000, 10000 evts/s)."""
    load_test_engine.start(tier_eps=tier)

    inc_data = None
    if tier >= 1000:
        inc = anomaly_engine.create_load_stress_incident(tier)
        inc_data = inc.model_dump()

        # Mutate canonical graph state: BOTNET -> EDGE-INGRESS (98.7% dropped) -> CORE-LEDGER
        graph_engine.update_load_stress(tier, is_stopped=False)
        rf_graph = graph_engine.to_react_flow(focus_nodes=["BOTNET-SYNDICATE-ALPHA", "BOTNET-SYNDICATE-BETA", "EDGE-INGRESS-FILTER", "CORE-LEDGER-PIPELINE"])
        await ws_manager.broadcast("graph_updated", rf_graph)
        graph_engine.record_attack_snapshot(inc.id, f"Volumetric Botnet Assault ({tier:,} EPS)", {"filtered_rate": "98.7%"})

        await ws_manager.broadcast("incident_created", {"incident": inc_data})
        await ws_manager.broadcast("emergency_alert", {
            "incident_id": inc.id,
            "threat_type": inc.threat_type,
            "severity": inc.severity,
            "risk_score": inc.risk_score,
            "affected_accounts": inc.affected_accounts,
            "affected_devices": inc.affected_devices,
            "affected_recipients": inc.affected_recipients,
            "scenario": f"High Velocity Load Stress ({tier:,} EPS)",
            "recommended_action": inc.recommended_action
        })
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 2,
            "code": "EDGE_ANOMALY",
            "title": "Edge Volumetric Anomaly",
            "subtitle": f"Stress spike: {tier:,} EPS. Filtering 98.7% locally at edge.",
            "status": "COMPLETED"
        })
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 3,
            "code": "INCIDENT_FORMATION",
            "title": "Incident Formation",
            "subtitle": f"{inc.id}: Volumetric Botnet Assault Detected",
            "status": "COMPLETED"
        })
        await ws_manager.broadcast("workflow_stage_update", {
            "stage_id": 10,
            "code": "RECOMMENDED_ACTION",
            "title": "Recommended Action",
            "subtitle": "Adaptive Ingress Rate-Limiting & Edge Sharding",
            "status": "COMPLETED"
        })

    return {
        "status": "LOAD_TEST_STARTED",
        "tier_eps": tier,
        "metrics": load_test_engine.get_status(),
        "incident": inc_data
    }

@app.post("/api/load-test/stop")
async def stop_load_test():
    """Stops the active load test and resolves load stress incidents."""
    load_test_engine.stop()

    # Mutate canonical graph to contained
    graph_engine.update_load_stress(0, is_stopped=True)
    rf_graph = graph_engine.to_react_flow(focus_nodes=["BOTNET-SYNDICATE-ALPHA", "BOTNET-SYNDICATE-BETA", "EDGE-INGRESS-FILTER", "CORE-LEDGER-PIPELINE"])
    await ws_manager.broadcast("graph_updated", rf_graph)

    for inc in anomaly_engine.get_all_incidents():
        if inc.status == "ACTIVE" and "Volumetric" in inc.threat_type:
            inc.status = "CONTAINED"
            await ws_manager.broadcast("incident_contained", {
                "incident_id": inc.id,
                "status": "CONTAINED",
                "action": {"strategy": "RATE_LIMIT_ISOLATION", "status": "LOAD_CONTAINED"}
            })
    return {"status": "LOAD_TEST_STOPPED"}

# ==========================================
# PHASE 10: REPLAY ATTACK FEATURE
# ==========================================
@app.get("/api/incidents/{incident_id}/replay-steps")
async def get_incident_replay_steps(incident_id: str):
    """Returns recorded progression timeline snapshots for Replay Attack feature."""
    steps = graph_engine.get_attack_snapshots(incident_id)
    return {
        "incident_id": incident_id,
        "total_steps": len(steps),
        "steps": steps
    }

@app.post("/api/incidents/{incident_id}/replay-step/{step_index}")
async def replay_single_step(incident_id: str, step_index: int):
    """Broadcasts a specific replay step across WebSocket for synchronized client playback."""
    steps = graph_engine.get_attack_snapshots(incident_id)
    if 0 <= step_index < len(steps):
        target_step = steps[step_index]
        await ws_manager.broadcast("graph_updated", target_step["graph"])
        return {"status": "STEP_BROADCAST", "step": target_step}
    raise HTTPException(status_code=404, detail="Step index out of range")

@app.get("/api/load-test/metrics")
async def get_load_test_metrics():
    """Returns current load test throughput, latency percentiles, and Fraud Evaluation Metrics."""
    return load_test_engine.get_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial snapshot upon connection
        system_status = await get_system_status()
        await websocket.send_json({
            "type": "initial_state",
            "data": {
                "events": [e.model_dump() for e in event_generator.recent_events[:20]],
                "incidents": [i.model_dump() for i in anomaly_engine.get_all_incidents()[:5]],
                "system_status": system_status,
                "telemetry_history": telemetry_tracker.history,
                "graph": graph_engine.to_react_flow()
            }
        })
        while True:
            # Keep socket alive and handle incoming client pings or commands
            data = await websocket.receive_text()
            logger.debug(f"Received WS text from client: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
