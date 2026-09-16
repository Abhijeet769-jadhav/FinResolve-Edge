# FinResolve Predict — Real-Time Financial Threat Detection & Attack Simulation Platform

**FinResolve Predict** is an advanced, real-time financial threat intelligence and attack simulation platform prototype designed to answer:

> *"Is this part of a coordinated financial threat, how could that threat spread, and which intervention could contain it with the smallest expected impact?"*

Rather than isolating individual transactions, FinResolve Predict correlates multi-factor anomalies across an in-memory temporal financial graph, dynamically forecasts propagation blast radius, simulates competing intervention strategies, and executes human-approved containment protocols.

---

## Architecture & Live Workflow Centerpiece

The platform features a 13-stage continuous threat lifecycle pipeline:

```text
1. Financial Events ──▶ 2. Real-Time Ingestion ──▶ 3. Edge Anomaly Detection ──▶ 4. Incident Formation
                                                                                          │
┌─────────────────────────────────────────────────────────────────────────────────────────┘
▼
5. Temporal Graph Engine ──▶ 6. Threat DNA Extraction ──▶ 7. Threat Propagation Forecast
                                                                   │
┌──────────────────────────────────────────────────────────────────┘
▼
8. Attack Simulation ──▶ 9. Intervention Comparison ──▶ 10. Recommended Containment
                                                                   │
┌──────────────────────────────────────────────────────────────────┘
▼
11. Human Analyst Approval ──▶ 12. Response Execution ──▶ 13. Incident Resolution
```

When an attack scenario is injected, each stage visibly triggers and lights up across the interface with live telemetry.

---

## Features

- **Continuous Synthetic Financial Stream**: Ingests `LOGIN`, `OTP_FAILURE`, `TRANSACTION`, `DEVICE_CHANGE`, `NEW_RECIPIENT`, and `MERCHANT_PAYMENT` events across 5 regional edge hubs (Pune, Mumbai, Delhi, Bangalore, Hyderabad).
- **Post-Quantum Cryptographic Verification Abstraction**: Edge signals are hashed via **SHA-384** and validated through an NIST FIPS 204 **ML-DSA-65** demonstrational envelope.
- **Explainable Multi-Factor Anomaly Scoring**: Real-time evaluation of device-to-account ratios, transaction velocity spikes, OTP failures, and geodispersion (0-100 risk score with clear human-readable factors).
- **Incident Formation**: Correlates multiple suspicious anomalies into unified incidents (`INC-xxxx`) instead of spamming alerts.
- **Temporal Financial Graph (NetworkX + React Flow)**: Models entities (`ACCOUNT`, `DEVICE`, `IP`, `TRANSACTION`, `RECIPIENT`, `MERCHANT`, `LOCATION`) with interactive node inspection and real-time blast radius expansion.
- **Threat DNA Extraction**: Derives behavioral fingerprint, velocity level, coordination score, geographic spread, and historical cluster similarity.
- **Dynamic Graph-Calculated Propagation Forecast**: Dynamically calculates unmitigated expansion across `NOW`, `15m`, `30m`, and `60m` horizons based on actual NetworkX topology, degree centrality, and velocity.
- **Attack Simulator & Strategy Comparison**: Simulates 5 interventions (`NO_ACTION`, `BLOCK_DEVICE`, `HOLD_RECIPIENT`, `STEP_UP_AUTH`, `COMBINED`) comparing financial exposure, customer friction, and containment efficiency.
- **Human-in-the-Loop Containment Execution**: Analyst approves or rejects interventions; approval immediately updates graph state, isolates nodes, halts propagation, and contains the incident.
- **Zero External Infrastructure**: Runs 100% locally with FastAPI, Uvicorn, NetworkX, and Vite React.

---

## Quick Start

### Option A: One-Click Launcher (Recommended for Windows)

Simply double-click:
```text
c:\Hack2Ignite\finresolve\start_all.bat
```
This automatically launches both the backend and frontend in separate lightweight windows and opens your browser.

---

### Option B: Manual Command Line

#### 1. Backend

Requirements: Python 3.10+ (tested on Python 3.13)

```bash
cd c:\Hack2Ignite\finresolve\backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
> [!TIP]
> Run `python -m uvicorn main:app --port 8000` without `--reload` to prevent Windows file-watchers from scanning `node_modules`.

The API will be available at `http://127.0.0.1:8000`.

#### 2. Frontend

Requirements: Node.js 18+ and npm

```bash
cd c:\Hack2Ignite\finresolve\frontend
npm install
npm run dev
```

The application will start at `http://127.0.0.1:5173`.

---

## Demonstration Script (2–3 Minutes)

1. **Observe Baseline Normal State**:
   - Open `http://127.0.0.1:5173`.
   - The WebSocket indicator will show **● LIVE**.
   - Background synthetic transactions stream in normally with low risk scores (0–30).
   - The 13-stage pipeline rests in nominal monitoring mode.

2. **Inject Coordinated Attack**:
   - Click the prominent **[ SIMULATE ATTACK ]** button in the top navigation bar (or choose from Scenario 1: ATO, Scenario 2: Mule Network, Scenario 3: Merchant Exploit).

3. **Watch the 13 Stages Fire in Sequence**:
   - **Stage 1 & 2**: High-velocity events stream in from a rogue hardware fingerprint (`DEV-ROGUE-xxx`).
   - **Stage 3**: Edge node (e.g. Pune) flags OTP failures and emits an **ML-DSA-65 / SHA-384** signed anomaly signal.
   - **Stage 4**: Anomaly engine aggregates related events into an active incident (`INC-xxxx`).
   - **Stage 5**: Temporal Graph in React Flow dynamically expands with connected victim accounts, device hubs, and beneficiary nodes.
   - **Stage 6**: Threat DNA is extracted, highlighting high velocity, coordination score, and 88%+ historical pattern match.
   - **Stage 7**: Propagation Forecast dynamically computes exposure exponential curve across 15m, 30m, and 60m horizons.
   - **Stage 8, 9 & 10**: Simulator runs 5 intervention strategies, selects the optimal strategy (e.g. *Device Isolation + Step-Up Auth*), and justifies the trade-off.

4. **Review & Approve Containment**:
   - Click **[ APPROVE RESPONSE ]** on the active threat banner.
   - Review the blast radius quarantine details in the modal and click **[ APPROVE & CONTAIN ]**.
   - Watch the backend update state in real time:
     - Target entities are flagged as `[ISOLATED]`.
     - Incident status transitions to **CONTAINED**.
     - Propagation forecast curve flatlines.
     - Pipeline marks all 13 stages as **COMPLETED**.

---

## REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health & PQC integrity check |
| `GET` | `/api/events` | Recent financial events buffer |
| `GET` | `/api/incidents` | All detected incidents & states |
| `GET` | `/api/incidents/{id}` | Detailed incident record |
| `GET` | `/api/graph` | NetworkX graph formatted for React Flow |
| `GET` | `/api/forecast/{id}` | Dynamic 15m/30m/60m propagation forecast |
| `GET` | `/api/threat-dna/{id}` | Structured behavioral Threat DNA |
| `POST` | `/api/simulate` | Run multi-strategy intervention simulation |
| `POST` | `/api/response/approve` | Human analyst response authorization |
| `POST` | `/api/response/reject` | Human analyst rejection |
| `POST` | `/api/demo/inject-attack` | Trigger synthetic attack scenario |
| `GET` | `/api/system-status` | Edge node metrics & engine statuses |
| `WS` | `/ws` | Real-time bidirectional WebSocket feed |

---

## Privacy & Synthetic Data Disclosure

This is a demonstration and attack simulation platform. All accounts, transactions, device identifiers, and locations are generated synthetically in-memory. Post-quantum cryptographic signatures are demonstrational abstractions simulating ML-DSA-65 over SHA-384 digests. No live financial data is ever collected or accessed.
