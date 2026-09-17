const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchEvents(limit = 50) {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function fetchIncidents() {
  const res = await fetch(`${API_BASE}/incidents`);
  if (!res.ok) throw new Error('Failed to fetch incidents');
  return res.json();
}

export async function fetchIncident(id) {
  const res = await fetch(`${API_BASE}/incidents/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch incident ${id}`);
  return res.json();
}

export async function fetchGraph(incidentId = null) {
  const url = incidentId ? `${API_BASE}/graph?incident_id=${incidentId}` : `${API_BASE}/graph`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch graph data');
  return res.json();
}

export async function fetchThreatDna(incidentId) {
  const res = await fetch(`${API_BASE}/threat-dna/${incidentId}`);
  if (!res.ok) throw new Error(`Failed to fetch Threat DNA for ${incidentId}`);
  return res.json();
}

export async function fetchForecast(incidentId) {
  const res = await fetch(`${API_BASE}/forecast/${incidentId}`);
  if (!res.ok) throw new Error(`Failed to fetch forecast for ${incidentId}`);
  return res.json();
}

export async function runSimulation(incidentId, horizon = '60m', strategy = null) {
  const res = await fetch(`${API_BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId, horizon, strategy })
  });
  if (!res.ok) throw new Error('Simulation failed');
  return res.json();
}

export async function approveResponse(incidentId, strategy, analystNote = '') {
  const res = await fetch(`${API_BASE}/response/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      incident_id: incidentId,
      action_type: 'APPROVE',
      strategy,
      analyst_note: analystNote
    })
  });
  if (!res.ok) throw new Error('Approval execution failed');
  return res.json();
}

export async function rejectResponse(incidentId, strategy, analystNote = '') {
  const res = await fetch(`${API_BASE}/response/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      incident_id: incidentId,
      action_type: 'REJECT',
      strategy,
      analyst_note: analystNote
    })
  });
  if (!res.ok) throw new Error('Rejection failed');
  return res.json();
}

export async function injectAttack(scenario = 'account_takeover') {
  const res = await fetch(`${API_BASE}/demo/inject-attack`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario })
  });
  if (!res.ok) throw new Error('Failed to inject attack');
  return res.json();
}

export async function fetchSystemStatus() {
  const res = await fetch(`${API_BASE}/system-status`);
  if (!res.ok) throw new Error('Failed to fetch system status');
  return res.json();
}

// Phase 2: Edge Simulation
export async function fetchEdgeNodes() {
  const res = await fetch(`${API_BASE}/edge/nodes`);
  if (!res.ok) throw new Error('Failed to fetch edge nodes');
  return res.json();
}

export async function fetchEdgeCounters() {
  const res = await fetch(`${API_BASE}/edge/counters`);
  if (!res.ok) throw new Error('Failed to fetch edge counters');
  return res.json();
}

export async function disconnectEdgeNode(nodeName) {
  const res = await fetch(`${API_BASE}/edge/${encodeURIComponent(nodeName)}/disconnect`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to disconnect ${nodeName}`);
  return res.json();
}

export async function reconnectEdgeNode(nodeName) {
  const res = await fetch(`${API_BASE}/edge/${encodeURIComponent(nodeName)}/reconnect`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to reconnect ${nodeName}`);
  return res.json();
}

// Phase 3: PQC Lab
export async function fetchPqcInfo() {
  const res = await fetch(`${API_BASE}/pqc/info`);
  if (!res.ok) throw new Error('Failed to fetch PQC info');
  return res.json();
}

export async function testPqcValid(amount = 10000.0) {
  const res = await fetch(`${API_BASE}/pqc/test-valid?amount=${amount}`, { method: 'POST' });
  if (!res.ok) throw new Error('Valid PQC test failed');
  return res.json();
}

export async function testPqcTamper(origAmount = 10000.0, tamperedAmount = 1000000.0) {
  const res = await fetch(`${API_BASE}/pqc/test-tamper?original_amount=${origAmount}&tampered_amount=${tamperedAmount}`, { method: 'POST' });
  if (!res.ok) throw new Error('Tamper PQC test failed');
  return res.json();
}

// Phase 4: Dataset Adapters
export async function replayAmlSim(pattern = 'fan_in', count = 20) {
  const res = await fetch(`${API_BASE}/adapters/amlsim/replay?pattern=${encodeURIComponent(pattern)}&count=${count}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to replay AMLSim stream');
  return res.json();
}

export async function replayPaySim(pattern = 'transfer_cashout_drain', count = 20) {
  const res = await fetch(`${API_BASE}/adapters/paysim/replay?pattern=${encodeURIComponent(pattern)}&count=${count}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to replay PaySim stream');
  return res.json();
}

// Phase 5: Load Testing
export async function startLoadTest(tier = 100) {
  const res = await fetch(`${API_BASE}/load-test/start?tier=${tier}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to start load test');
  return res.json();
}

export async function stopLoadTest() {
  const res = await fetch(`${API_BASE}/load-test/stop`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to stop load test');
  return res.json();
}

export async function fetchLoadTestMetrics() {
  const res = await fetch(`${API_BASE}/load-test/metrics`);
  if (!res.ok) throw new Error('Failed to fetch load test metrics');
  return res.json();
}

