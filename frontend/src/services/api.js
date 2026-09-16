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
