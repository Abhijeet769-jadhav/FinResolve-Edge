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

@app.get("/api/graph")
async def get_graph(incident_id: Optional[str] = None):
    """Returns graph representation formatted for React Flow."""
    focus_nodes = None
    if incident_id:
        inc = anomaly_engine.get_incident(incident_id)
        if inc:
            focus_nodes = inc.affected_accounts + inc.affected_devices + inc.affected_recipients

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

    # Broadcast updated graph
    rf_graph = graph_engine.to_react_flow(focus_nodes=inc.affected_accounts + inc.affected_devices)
    await ws_manager.broadcast("graph_updated", rf_graph)

    return {"status": "SUCCESS", "action": result, "incident": inc.model_dump()}

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
    """Simulates edge node disconnection, buffering events locally."""
    res = anomaly_engine.disconnect_edge_node(node_name)
    await ws_manager.broadcast("edge_node_updated", res)
    return res

@app.post("/api/edge/{node_name}/reconnect")
async def reconnect_edge_node(node_name: str):
    """Simulates edge node reconnection, flushing buffered events to central."""
    res = anomaly_engine.reconnect_and_sync_edge_node(node_name)
    await ws_manager.broadcast("edge_node_updated", res)
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
    """Runs PQC tamper test where amount is altered in-flight (₹10,000 -> ₹1,000,000)."""
    res = pqc_lab.run_tamper_test(original_amount=original_amount, tampered_amount=tampered_amount)
    return res

# ==========================================
# PHASE 4: DATASET ADAPTERS (AMLSim & PaySim)
# ==========================================
async def _replay_adapter_stream(events: List[Any], delay_sec: float = 0.08):
    for evt in events:
        await event_generator.process_and_broadcast_event(evt, is_attack=False, broadcast_graph=True)
        await asyncio.sleep(delay_sec)

@app.post("/api/adapters/amlsim/replay")
async def replay_amlsim(pattern: str = Query("fan_in"), count: int = Query(20)):
    """Replays synthetic IBM AMLSim topology (fan_in, cycle, scatter_gather, normal)."""
    events = amlsim_adapter.generate_synthetic_stream(pattern=pattern, count=count)
    asyncio.create_task(_replay_adapter_stream(events))
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
    asyncio.create_task(_replay_adapter_stream(events))
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
    return {
        "status": "LOAD_TEST_STARTED",
        "tier_eps": tier,
        "metrics": load_test_engine.get_status()
    }

@app.post("/api/load-test/stop")
async def stop_load_test():
    """Stops the active load test."""
    load_test_engine.stop()
    return {
        "status": "LOAD_TEST_STOPPED",
        "final_metrics": load_test_engine.get_status()
    }

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
