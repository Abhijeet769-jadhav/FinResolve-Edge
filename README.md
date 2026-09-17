# FinResolve Predict

## Real-Time Financial Threat Detection, Prediction & Response Platform

**FinResolve Predict** is a financial security operations platform
prototype designed to detect, correlate, predict, simulate, and contain
coordinated financial threats in real time.

Instead of treating every suspicious transaction as an isolated alert,
FinResolve builds a **canonical threat graph** connecting accounts,
devices, recipients, gateways, edge nodes, locations, and transactions.
It combines graph correlation, Threat DNA, propagation forecasting,
intervention simulation, edge resilience, post-quantum cryptography, and
human-approved response workflows.

> **Core flow:** Observe → Correlate → Predict → Simulate → Approve →
> Contain

------------------------------------------------------------------------

## Why FinResolve Predict?

Financial systems generate large volumes of events: payments, logins,
authentication failures, device activity, recipient transfers, merchant
failures, gateway errors, and API failures.

A single event may look harmless. A coordinated sequence can reveal a
much larger attack.

``` text
Multiple accounts
       ↓
Shared device
       ↓
Repeated failed authentication
       ↓
Small test transactions
       ↓
Common recipient
       ↓
Behavioral / geographic spread
       ↓
Coordinated financial threat
```

FinResolve correlates these signals into an explainable threat picture
and provides a response workflow instead of another disconnected alert.

------------------------------------------------------------------------

# Core Capabilities

## 1. Canonical Threat Graph

The platform maintains a connected graph representing the financial
environment.

``` text
LOCATION
    │
    ▼
  DEVICE ─────► EDGE NODE ─────► GATEWAY
    │
    ▼
 ACCOUNT ─────► RECIPIENT
    │
    ▼
TRANSACTION
```

The graph prioritizes meaningful structural relationships instead of
allowing high-risk ephemeral transaction nodes to hide the underlying
topology.

### Graph posture

  -----------------------------------------------------------------------
  Color                   Meaning                 Example
  ----------------------- ----------------------- -----------------------
  🟢 Green                Normal / protected /    Healthy accounts,
                          authorized              gateways, edge nodes

  🟡 Yellow               Step-up authentication  Challenged victim
                          / elevated risk         accounts

  🔴 Red                  Blocked / active threat Rogue devices and
                          / adversary             attack infrastructure
  -----------------------------------------------------------------------

Containment is reflected directly in graph edges:

-   **Red dashed** → `BLOCKED / DENIED`
-   **Yellow dashed** → `STEP-UP AUTH`
-   **Green dashed** → `PROTECTED / HELD`
-   **Green solid** → Authorized / healthy transaction flow

The implementation preserves a healthy baseline so normal infrastructure
remains visible during continuous attack simulations.

------------------------------------------------------------------------

## 2. Threat DNA

**Threat DNA** represents the behavioral characteristics of an emerging
coordinated threat.

The dashboard evaluates factors including:

-   Transaction velocity
-   Account coordination
-   Geographic spread
-   Mule / recipient concentration
-   Cluster similarity

``` text
Velocity              █████████░  High
Coordination          ██████████  Very High
Geo Spread            ███████░░░  Elevated
Mule Concentration    █████████░  High
Cluster Similarity    ██████████  Very High
```

This helps explain why several individually suspicious events can be
treated as one coordinated threat.

------------------------------------------------------------------------

## 3. Propagation Forecast

FinResolve projects possible threat evolution across multiple horizons.

``` text
NOW ───── 15 MIN ───── 30 MIN ───── 60 MIN
 │           │             │             │
Current    Expansion     Further       Projected
Threat     Risk          Spread        Exposure
```

The dashboard can transition from:

``` text
UNMITIGATED TRAJECTORY
```

to:

``` text
GROWTH ARRESTED
```

after containment.

Forecasts are decision-support simulations, not guarantees of future
losses.

------------------------------------------------------------------------

## 4. Intervention Strategy Simulation

Before containment, FinResolve compares response strategies:

-   `NO_ACTION`
-   `BLOCK_DEVICE`
-   `HOLD_RECIPIENT`
-   `STEP_UP_AUTH`
-   `COMBINED`

The simulation matrix provides an optimal-strategy banner, comparative
efficiency information, review controls, and direct approval.

``` text
Threat detected
      ↓
Threat DNA + graph correlation
      ↓
Propagation forecast
      ↓
Intervention simulation
      ↓
Strategy comparison
      ↓
Human approval
      ↓
Containment
```

------------------------------------------------------------------------

## 5. Human-in-the-Loop Response

FinResolve does not treat automated prediction as authorization for
irreversible actions.

``` text
DETECTED
   ↓
CORRELATING
   ↓
ASSESSING
   ↓
PENDING APPROVAL
   ↓
APPROVED
   ↓
CONTAINING
   ↓
CONTAINED
   ↓
RESOLVED
```

Analysts can review incidents, compare strategies, approve or reject
responses, and apply containment actions.

------------------------------------------------------------------------

## 6. Edge Detection & Resilience

An edge-oriented architecture supports scenarios where centralized
infrastructure is delayed or temporarily unavailable.

``` text
Financial Event
      ↓
Edge Collector
      ↓
Local Detection
      ↓
Important Signal?
   ↙          ↘
 NO            YES
 ↓              ↓
Local handling  PQC signing
                ↓
             Central SOC
```

Edge nodes can locally detect/filter events, identify important signals,
sign incident messages, buffer events during disconnection, and
synchronize after reconnection.

------------------------------------------------------------------------

## 7. Post-Quantum Cryptography

FinResolve includes a PQC security layer for incident communication and
control-plane operations.

  Component         Purpose
  ----------------- -----------------------------------------------------
  **ML-DSA-65**     Digital signatures for incident events and commands
  **ML-KEM-768**    Key establishment between edge and central systems
  **AES-256-GCM**   Confidentiality and authenticated encryption
  **SHA-384**       Audit-log integrity / hashing

The PQC lab supports both valid-message verification and tamper testing.

``` text
Original event → Signature verification → VALID

Modified event → Signature verification → INVALID / TAMPERED
```

PQC protects communication authenticity and integrity; it is not itself
the fraud-detection mechanism.

------------------------------------------------------------------------

# Attack Lab

FinResolve includes deterministic scenarios for demonstrations and
testing:

1.  Normal baseline
2.  Account takeover
3.  Mule network
4.  Coordinated fraud
5.  Recipient attack
6.  Credential stuffing
7.  Gateway outage
8.  Merchant failure
9.  Mixed attack
10. Weak-signal progression

``` text
Baseline
   ↓
Weak signals
   ↓
Threat correlation
   ↓
Active attack
   ↓
Forecast
   ↓
Intervention simulation
   ↓
Analyst approval
   ↓
Containment
```

## Continuous Incident Rotation

For interactive demonstrations, simulator-driven incidents can
automatically rotate after containment.

The current implementation uses a **9-second stabilization window** so
analysts can inspect the contained graph before the next scenario
arrives.

An instant:

``` text
⚡ Inject Next Threat Now
```

control can bypass the waiting period.

The `testlab` and `attack_trigger` sources intentionally do not
auto-spawn follow-up incidents, preserving deterministic test control.

------------------------------------------------------------------------

# Architecture

``` text
                         ┌───────────────────────┐
                         │ Financial Event Sources│
                         │ Payments / Auth / API  │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Edge Collector     │
                         │ Local detection/filter│
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   PQC Security Layer  │
                         │ ML-DSA / ML-KEM / AES │
                         └───────────┬───────────┘
                                     │
                                     ▼
                 ┌────────────────────────────────────┐
                 │       Central FinResolve Engine     │
                 │                                    │
                 │ Graph Correlation                   │
                 │ Threat DNA                          │
                 │ Risk / Incident Engine              │
                 │ Propagation Forecast                │
                 │ Intervention Simulation             │
                 │ Response / Playbook Engine          │
                 └─────────────────┬──────────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │       SOC Dashboard        │
                    │ Live Events / Graph        │
                    │ DNA / Forecast / Response  │
                    └────────────────────────────┘
```

------------------------------------------------------------------------

# Event Model

A representative event:

``` json
{
  "event_id": "EVT-23994",
  "event_type": "payment",
  "account_id": "ACC-A101",
  "device_id": "DEV-D45",
  "ip": "pseudonymized-network-id",
  "merchant": "MERCHANT-01",
  "recipient": "REC-R900",
  "amount": 12500,
  "city": "Mumbai",
  "timestamp": "2026-09-16T20:30:00",
  "status": "pending"
}
```

For distributed processing, unique event identity can be reinforced
with:

``` text
event_id + edge_id + sequence_number
```

to support deduplication and replay-safe processing.

------------------------------------------------------------------------

# Detection Signals

The prototype supports patterns such as:

-   Multiple failed logins from one device
-   Multiple accounts sharing a device
-   Multiple payments converging on a recipient
-   Merchant failure spikes
-   Payment API error spikes
-   Gateway outages
-   Coordinated account activity
-   Geographic / behavioral spread
-   Weak signals that become significant when correlated

The design distinguishes:

``` text
Individual event
      ≠
Confirmed incident
```

------------------------------------------------------------------------

# SOC Dashboard

## Live Event Stream

Provides:

-   Real-time events
-   Search
-   Event categories
-   High-risk filtering
-   Transaction/auth filtering
-   LIVE / PAUSED state
-   Edge sequence indicators

## Threat Graph

Provides:

-   Account relationships
-   Device relationships
-   Recipient relationships
-   Gateway / edge relationships
-   Attack paths
-   Blocked paths
-   Step-up authentication
-   Protected / held flows
-   Healthy baseline topology

## Threat DNA

Provides:

-   Velocity
-   Coordination
-   Geographic spread
-   Mule concentration
-   Cluster similarity

## Propagation Forecast

Provides:

-   NOW
-   15-minute horizon
-   30-minute horizon
-   60-minute horizon
-   Growth-arrest status

## Intervention Matrix

Provides:

-   Strategy comparison
-   Recommended countermeasure
-   Efficiency metrics
-   Direct approval
-   Review workflow

------------------------------------------------------------------------

# API Surface

  Endpoint                             Purpose
  ------------------------------------ -----------------------------
  `GET /api/health`                    Health check
  `GET /api/system-status`             System status
  `GET /api/events`                    Event stream/history
  `GET /api/incidents`                 Incident information
  `GET /api/graph`                     Canonical threat graph
  `GET /api/forecast/{id}`             Threat propagation forecast
  `GET /api/threat-dna/{id}`           Threat DNA
  `POST /api/simulate`                 Run intervention simulation
  `POST /api/response/approve`         Approve response
  `POST /api/response/reject`          Reject response
  `POST /api/demo/inject-attack`       Inject demonstration attack
  `POST /api/lab/scenario`             Run Attack Lab scenario
  `POST /api/datasets/amlsim/replay`   Replay AMLSim-style data
  `POST /api/datasets/paysim/replay`   Replay PaySim-style data
  `POST /api/pqc/test-valid`           Test valid PQC message
  `POST /api/pqc/test-tamper`          Test tampered message
  `POST /api/edge/disconnect`          Simulate edge disconnection
  `POST /api/edge/reconnect`           Restore edge connectivity
  `POST /api/load-test/start`          Start load test
  `POST /api/load-test/stop`           Stop load test
  `GET /api/load-test/benchmark`       Retrieve benchmark results
  `WS /ws`                             Real-time dashboard updates

Swagger at `/docs` is the authoritative local API reference.

------------------------------------------------------------------------

# Data Replay & Load Testing

FinResolve can be evaluated using synthetic financial data and
deterministic event streams.

Supported directions include:

-   AMLSim-style transaction replay
-   PaySim-style transaction replay
-   Built-in deterministic generators
-   External CSV replay

Load-test targets:

``` text
10 → 50 → 100 → 500 → 1,000 → 5,000 → 10,000 EPS
```

Measure:

-   Events generated / second
-   Events processed / second
-   Detection latency
-   Correlation latency
-   PQC verification latency
-   API / WebSocket latency
-   CPU and memory
-   Dropped events
-   Browser rendering performance

------------------------------------------------------------------------

# Performance Design

High-frequency event streams are buffered and rendered in controlled
batches.

Key principles:

-   Buffer WebSocket events
-   Batch React updates
-   Cap visible event history
-   Cap graph nodes and edges
-   Limit ephemeral transaction nodes
-   Disable unnecessary chart animation
-   Animate only active threat edges
-   Aggregate high-volume metrics
-   Decouple simulator speed from visualization speed

------------------------------------------------------------------------

# Graph Selection Strategy

Risk-only graph selection can break topology:

``` text
Many high-risk transaction nodes
        ↓
Structural nodes excluded
        ↓
Edges have missing endpoints
        ↓
React Flow cannot render them
        ↓
Disconnected graph
```

FinResolve instead uses topological cluster selection.

A selected threat can retain its structural neighborhood:

``` text
LOCATION ← DEVICE → EDGE_NODE → GATEWAY
               │
               ▼
             ACCOUNT
               │
               ▼
           RECIPIENT
```

Ephemeral transactions are bounded and included only when their parent
entities are already represented.

------------------------------------------------------------------------

# Containment Posture

### 🔴 BLOCKED

Rogue devices, adversaries, botnet clusters, and denied attack paths.

### 🟡 STEP-UP

Accounts requiring additional authentication.

### 🟢 PROTECTED

Protected recipients, healthy infrastructure, authorized paths, and
quarantine barriers.

Containment states are protected from being overwritten by lower-risk
benign background events.

------------------------------------------------------------------------

# Verification

The current graph implementation has been validated across multiple
cycles.

### Baseline

``` text
18 nodes
15 edges
18 NORMAL / GREEN
15 solid green edges
```

### Active Account-Takeover Threat

``` text
33 nodes
38 edges

7 CRITICAL / RED
3 ACTIVE_THREAT / RED
5 SUSPICIOUS / AMBER
18 NORMAL / GREEN

23 red animated edges
15 green solid edges
```

### Post-Approval / Contained

``` text
30 nodes
32 edges

1 BLOCKED / RED
5 STEP_UP / YELLOW
1 PROTECTED / GREEN
18 NORMAL / GREEN

7 red dashed BLOCKED edges
5 yellow dashed STEP-UP edges
20 green HELD + authorized edges
```

### Cycle 2 --- Mule Network

``` text
46 nodes
59 edges

1 BLOCKED
5 STEP_UP
1 PROTECTED
18 NORMAL
10 ACTIVE THREATS

31 red edges
7 yellow edges
21 green edges
```

Automated approval/source-rule tests and a clean frontend production
build have also been verified.

------------------------------------------------------------------------

# Project Structure

``` text
FinResolve/
│
├── backend/
│   ├── main.py
│   ├── graph_engine.py
│   ├── response_engine.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AttackSimulator.jsx
│   │   │   ├── ThreatGraphView.jsx
│   │   │   ├── ThreatDnaCard.jsx
│   │   │   ├── PropagationForecastCard.jsx
│   │   │   ├── HumanApprovalModal.jsx
│   │   │   └── LiveEventStream.jsx
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── walkthrough.md
└── README.md
```

------------------------------------------------------------------------

# Quick Start

## Prerequisites

-   Python 3.10+
-   Node.js
-   npm
-   Git

## Backend

``` bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

## Frontend

``` bash
cd frontend
npm install
npm run dev
```

Frontend:

``` text
http://127.0.0.1:5173/
```

## Production Build

``` bash
npm run build
```

------------------------------------------------------------------------

# Recommended Demo Flow

1.  **Show healthy baseline** --- green infrastructure and normal
    transactions.
2.  **Inject an attack** --- account takeover, mule network, or
    coordinated fraud.
3.  **Show correlation** --- accounts, shared device, recipient, and
    transaction cluster.
4.  **Show Threat DNA** --- explain velocity, coordination, spread, and
    concentration.
5.  **Show forecast** --- NOW, 15m, 30m, 60m.
6.  **Compare interventions** --- show the strategy matrix.
7.  **Approve response** --- use `APPROVE STRATEGY`.
8.  **Show containment** --- red `BLOCKED`, yellow `STEP-UP`, green
    `PROTECTED`.
9.  **Continue** --- inject another scenario or allow automatic
    rotation.

------------------------------------------------------------------------

# Production Evolution

The prototype can evolve toward:

``` text
Financial APIs
      ↓
Edge Collectors
      ↓
Event Streaming
      ↓
┌───────────────┬───────────────┐
│ Redis / State │ PostgreSQL    │
└───────────────┴───────────────┘
      ↓
FinResolve Core
      ↓
SOC Dashboard
```

Production additions should include:

-   Persistent event and incident storage
-   Redis for short-lived state
-   Durable event streaming
-   Edge offline queues and synchronization
-   Idempotency and replay protection
-   Authentication and RBAC
-   Least privilege
-   Secret management
-   TLS / mTLS
-   Immutable audit trails
-   Prometheus / Grafana observability
-   Structured logging
-   Automated security scanning
-   Failure testing
-   High availability and disaster recovery

Docker Compose is a suitable intermediate deployment stage; Kubernetes
and cloud deployment can follow when scale and operational requirements
justify them.

------------------------------------------------------------------------

# Privacy & Security

FinResolve Predict is a prototype / research / hackathon platform and
should not be connected directly to production financial infrastructure
without additional validation.

The demonstration uses synthetic or simulated financial activity.

A real deployment should remain inside the financial institution's
security boundary and use controlled telemetry with:

-   Pseudonymized identifiers
-   Tokenized device identifiers
-   Data minimization
-   Least-privilege access
-   Encryption in transit and at rest
-   Retention policies
-   Role-based access
-   Tamper-evident audit logging

------------------------------------------------------------------------

# Design Principles

### Correlation over isolated alerts

``` text
Many weak signals
       ↓
One explainable threat
```

### Topology over risk-only sorting

A useful graph must preserve structural relationships.

### Prediction before escalation

Identify emerging coordinated behavior as early as possible.

### Simulation before intervention

Compare response strategies before taking action.

### Human approval for consequential actions

Automation assists analysts rather than silently making irreversible
decisions.

### Resilience at the edge

Detection should not completely depend on a healthy central connection.

### Cryptographic trust

Incident communication and control-plane messages should be verifiable
and tamper-evident.

------------------------------------------------------------------------

# Current Status

-   [x] Real-time event stream
-   [x] WebSocket dashboard updates
-   [x] Canonical threat graph
-   [x] Connected structural graph topology
-   [x] Green baseline preservation
-   [x] Red / yellow / green containment posture
-   [x] Threat DNA visualization
-   [x] Propagation forecast
-   [x] Intervention strategy matrix
-   [x] Direct strategy approval
-   [x] Human approval workflow
-   [x] Incident containment state
-   [x] Attack Lab scenarios
-   [x] Automatic incident rotation
-   [x] Deterministic testlab / attack-trigger source rules
-   [x] PQC test workflow
-   [x] Dataset replay direction
-   [x] Load-testing direction
-   [x] Automated graph verification
-   [x] Frontend production build verification

------------------------------------------------------------------------

# Roadmap

## Phase 1 --- Prototype

Real-time simulation, threat graph, Threat DNA, forecasting,
intervention simulation, human approval, and PQC demonstration.

## Phase 2 --- Resilience

Persistent storage, Redis state, edge offline queues, synchronization,
idempotency, and replay protection.

## Phase 3 --- Intelligence

Advanced anomaly detection, graph anomaly scoring, learned Threat DNA,
improved propagation models, and adaptive intervention optimization.

## Phase 4 --- Production Operations

RBAC, audit platform, observability, structured logging, security
scanning, CI/CD, and failure testing.

## Phase 5 --- Scale

Distributed streaming, multi-region edge nodes, Kubernetes, cloud
deployment, and large-scale synthetic / institutional datasets.

------------------------------------------------------------------------

# Disclaimer

FinResolve Predict is a **prototype and research / hackathon platform**
intended to demonstrate financial threat detection, correlation,
prediction, simulation, and response concepts.

Synthetic attack scenarios and forecast values should not be interpreted
as validated predictions of real financial losses or production security
decisions.

------------------------------------------------------------------------

# Vision

Move financial security operations from:

``` text
Detect individual alert
        ↓
Investigate manually
        ↓
Respond after impact
```

toward:

``` text
Observe weak signals
        ↓
Correlate behavior
        ↓
Recognize emerging threat
        ↓
Forecast possible propagation
        ↓
Simulate interventions
        ↓
Get human approval
        ↓
Contain the threat
        ↓
Verify the resulting posture
```

**FinResolve Predict --- turning financial security events into an
explainable, predictive, and actionable threat-response workflow.**
