# FinResolve Predict — Implementation Plan

Build **FinResolve Predict**, a real-time financial fraud & threat intelligence platform prototype with edge anomaly detection, temporal graph analysis (NetworkX), Threat DNA extraction, dynamic threat propagation forecasting, multi-strategy intervention simulation, and human-in-the-loop containment response execution.

## Proposed Architecture

```
                               ┌────────────────────────────────────────┐
                               │       Synthetic Event Generator        │
                               │  (Benign baseline + Coordinated ATO /  │
                               │   Mule Network / Merchant Attacks)     │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │   Edge Detection Nodes (5 Regions)     │
                               │   Pune, Mumbai, Delhi, BLR, Hyderabad │
                               │   ML-DSA-65/SHA-384 Verified Signals   │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │    Anomaly & Incident Engines          │
                               │  (Multi-factor scoring, explainability │
                               │   incident aggregation & timeline)     │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │     Temporal Graph Engine (NetworkX)   │
                               │  Nodes: Account, Device, IP, Txn, etc. │
                               │  Edges: USES, ACCESSED_FROM, PAID_TO   │
                               └─────────┬──────────────────┬───────────┘
                                         │                  │
                    ┌────────────────────┴─────┐      ┌─────┴────────────────────┐
                    ▼                          ▼      ▼                          ▼
       ┌────────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐
       │   Threat DNA Engine    │  │ Propagation Engine  │  │    Simulator Engine     │
       │ Velocity, Coordination,│  │ Horizon: Now, 15m,  │  │ 5 Strategies (No action,│
       │ Spread, Concentration  │  │ 30m, 60m expansion  │  │ block, hold, step-up...)│
       └────────────────────────┘  └─────────────────────┘  └────────────┬────────────┘
                                                                         │
                                                                         ▼
                                                            ┌─────────────────────────┐
                                                            │ Response Recommendation │
                                                            │ & Human Approval Action │
                                                            └─────────────────────────┘
                                                                         │
                                                                         ▼
                                                            ┌─────────────────────────┐
                                                            │ WebSocket Broadcast     │
                                                            │ & React Flow UI         │
                                                            └─────────────────────────┘
```

---

## User Review Required

> [!IMPORTANT]
> - **Live Workflow Centerpiece**: The 13-stage workflow (`Financial Events → Event Ingestion → Edge Anomaly Detection → Incident Formation → Temporal Graph → Threat DNA → Propagation Forecast → Attack Simulation → Intervention Comparison → Recommended Action → Human Approval → Response Execution → Incident Resolution`) is the visual centerpiece of the UI, visibly firing and highlighting each stage in sequence with live telemetry when an attack is injected.
> - **Dynamic Graph Propagation**: Forecasts are dynamically calculated directly from the actual NetworkX graph topology (degree centrality, uncompromised neighbor reach, transaction velocity, amount variance), never hardcoded.
> - **Explicit Demonstrational PQC**: Cryptographic signal verification uses SHA-384 payload hashing and signature metadata formatted as `ML-DSA-65` abstraction, with clear SOC badge: *"Demonstrational PQC Abstraction (ML-DSA-65 / SHA-384)"*.
> - **Technology Stack**: Backend uses Python 3.13 + FastAPI + Uvicorn + NetworkX + WebSockets + Pydantic. Frontend uses Vite + React + Tailwind CSS + Lucide React + React Flow (`@xyflow/react`) + Recharts. Zero external infrastructure.

---

## Proposed Changes

### 1. Directory Structure

We will create the project in `c:\Hack2Ignite\finresolve`:
```text
finresolve/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── event_generator.py
│   ├── anomaly_engine.py
│   ├── graph_engine.py
│   ├── threat_dna.py
│   ├── propagation_engine.py
│   ├── simulation_engine.py
│   ├── response_engine.py
│   ├── websocket_manager.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── SystemStatusPanel.jsx
│   │   │   ├── MetricsBanner.jsx
│   │   │   ├── LiveEventStream.jsx
│   │   │   ├── ThreatGraphView.jsx
│   │   │   ├── ThreatDnaCard.jsx
│   │   │   ├── PropagationForecastCard.jsx
│   │   │   ├── AttackSimulator.jsx
│   │   │   ├── HumanApprovalModal.jsx
│   │   │   ├── IncidentDetailModal.jsx
│   │   │   └── EdgeNodesMap.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
└── README.md
```

---

### 2. Backend Modules

#### `backend/models.py`
- Pydantic models for `FinancialEvent`, `EventType`, `EdgeNodeSignal`, `AnomalyReport`, `Incident`, `ThreatDNA`, `PropagationForecast`, `InterventionStrategy`, `SimulationResult`, `ResponseAction`, and `SystemStatus`.

#### `backend/event_generator.py`
- Background event generation for standard benign traffic (1 event every 1-2 sec across accounts, merchants, devices in Pune, Mumbai, Delhi, Bangalore, Hyderabad).
- 3 coordinated synthetic attack injectors:
  1. **Coordinated Account Takeover (ATO)**: Single suspicious device targeting multiple accounts, repeated OTP failures, fast login, new beneficiary addition, micro-deposit test, followed by large transfer.
  2. **Mule Network**: Dozens of accounts rapidly routing funds to a common concentrated recipient/mule node.
  3. **Merchant/Payment Exploit**: Distributed payment failures, rapid retries, high card velocity across multiple merchants.

#### `backend/anomaly_engine.py`
- Local edge node processing across the 5 nodes: Pune, Mumbai, Delhi, Bangalore, Hyderabad.
- Explainable multi-factor scoring:
  - Multi-account device association (+25)
  - Anomaly transaction volume (+20)
  - Consecutive OTP failures (+15)
  - Velocity / Rapid transaction frequency (+15)
  - High-risk recipient creation (+15)
  - Velocity across distinct geolocations (+10)
- Classification: Normal (0-30), Elevated (31-60), High (61-80), Critical (81-100).
- Post-quantum verification abstraction: generates cryptographic payload hash (SHA-384) and ML-DSA-65 signature envelope.
- Incident aggregation: Groups correlated anomaly signals into consolidated incidents (`INC-xxxx`) with state tracking (`ACTIVE`, `CONTAINED`, `REJECTED`).

#### `backend/graph_engine.py`
- Uses `networkx.MultiDiGraph` to model financial entities:
  - Nodes: `ACCOUNT`, `DEVICE`, `IP`, `TRANSACTION`, `RECIPIENT`, `MERCHANT`, `LOCATION`.
  - Edges: `USES`, `ACCESSED_FROM`, `MAKES`, `SENT_TO`, `PAID_TO`, `LOCATED_IN`.
- Updates dynamically on incoming events.
- Exports graph and subgraph data (nodes with positions, labels, risk badges; edges with relationship types and amounts) formatted for React Flow.

#### `backend/threat_dna.py`
- Extracts structural fingerprint from incident subgraph:
  - Attack Type identification
  - Structural characteristics list
  - Velocity index (transactions/min)
  - Coordination score (node degree concentration)
  - Geographic dispersion
  - Recipient concentration index
  - Historical pattern similarity match percentage

#### `backend/propagation_engine.py`
- Analyzes the current graph topology to simulate threat propagation across 4 horizons: `NOW`, `+15 min`, `+30 min`, `+60 min`.
- Dynamically computes:
  - Accounts at risk
  - Transactions at risk
  - Financial exposure (₹)
  - Propagation velocity & vectors
- Propagation rate scales with device degree centrality, recipient concentration, and recent transaction velocity.

#### `backend/simulation_engine.py`
- Evaluates 5 intervention strategies:
  1. `NO_ACTION`
  2. `BLOCK_DEVICE`
  3. `HOLD_RECIPIENT`
  4. `STEP_UP_AUTH`
  5. `COMBINED` (e.g. `BLOCK_DEVICE + STEP_UP_AUTH`)
- Computes for each strategy:
  - Projected affected accounts, transactions at risk, exposure (₹), propagation rating, customer friction rating, and overall containment score (0-100).
- Dynamically selects and justifies the optimal recommendation based on maximum exposure reduction with balanced customer friction.

#### `backend/response_engine.py`
- Handles analyst actions: `APPROVE` or `REJECT`.
- Modifies incident state:
  - `APPROVE`: isolates entity nodes in graph, halts further propagation, marks incident as `CONTAINED`, records response execution audit log.
  - `REJECT`: records reason, incident remains `ACTIVE`.

#### `backend/websocket_manager.py` & `backend/main.py`
- FastAPI app with CORS middleware, REST endpoints, and WebSocket route `/ws`.
- Broadcasts real-time events to all connected clients.

---

### 3. Frontend Implementation

#### React + Vite + Tailwind CSS + React Flow + Recharts
- **Dashboard Layout**:
  - **Header & Navbar**: Live WebSocket status, active scenario trigger button (`[ SIMULATE ATTACK ]` with scenario picker dropdown), system metrics summary.
  - **Metrics Banner**: Total Events, Active Incidents, Accounts at Risk, Total Financial Exposure (₹), Active Containment status.
  - **Main Working Grid**:
    - **Left Column**: Live Event Stream (auto-scrolling, color-coded by event type and risk) + Edge Nodes Map & PQC Status.
    - **Center Column**: Interactive Temporal Graph (React Flow with custom nodes for Account, Device, Recipient, Merchant, Txn; zoom/pan, click-to-inspect) + Active Threat & Threat DNA card.
    - **Right Column**: Threat Propagation Forecast (visual timeline + Recharts projection) + Attack Simulator & Intervention Matrix + Recommended Response & Human Approval Action Card.
- **Incident Detail Modal**:
  - Full deep-dive view into any selected incident: event timeline, threat DNA metrics, node details, full simulation comparisons, containment audit log.
- **Simulation Comparison View**:
  - Side-by-side radar or multi-bar chart comparing all 5 strategies on containment score, customer friction, and financial exposure prevented.
- **Human Approval Workflow**:
  - Modal / Banner with immediate real-time feedback when approving or rejecting interventions.

---

## Verification Plan

### Automated Tests
1. **Backend Verification Script**:
   - Test event generation and anomaly scoring calculation.
   - Test attack scenario injection and verify incident creation.
   - Test NetworkX graph updates and subgraph extraction.
   - Test propagation forecast numbers generation.
   - Test simulation engine for all 5 strategies.
   - Test approval endpoint to verify incident status transitions to `CONTAINED`.
2. **Endpoint Health Checks**:
   - Verify `/api/health`, `/api/events`, `/api/incidents`, `/api/graph`, `/api/system-status`.

### Manual / End-to-End Verification
1. Start backend: `uvicorn main:app --port 8000`.
2. Start frontend: `npm run dev -- --host 127.0.0.1 --port 5173`.
3. Test WebSocket connection and ensure live benign events stream into the UI.
4. Trigger "Simulate Attack" (Scenario 1: Coordinated Account Takeover).
5. Verify edge node signal lights up with ML-DSA-65 verification.
6. Verify risk score spikes to High/Critical and incident forms (`INC-XXXX`).
7. Verify React Flow graph expands with connected Accounts, Device, Recipient.
8. Verify Threat DNA and dynamic Propagation Forecast (e.g. 7 → 12 → 23 → 41).
9. Run Attack Simulator and verify side-by-side intervention strategy comparison.
10. Click "Approve Response" and verify state transition to `CONTAINED`.
