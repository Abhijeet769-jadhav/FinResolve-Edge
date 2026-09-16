import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import LiveWorkflowPipeline from './components/LiveWorkflowPipeline';
import MetricsBanner from './components/MetricsBanner';
import LiveEventStream from './components/LiveEventStream';
import ThreatGraphView from './components/ThreatGraphView';
import ThreatDnaCard from './components/ThreatDnaCard';
import PropagationForecastCard from './components/PropagationForecastCard';
import AttackSimulator from './components/AttackSimulator';
import HumanApprovalModal from './components/HumanApprovalModal';
import IncidentDetailModal from './components/IncidentDetailModal';
import EdgeNodesMap from './components/EdgeNodesMap';
import SystemStatusPanel from './components/SystemStatusPanel';

import { wsClient } from './services/websocket';
import { 
  fetchEvents, fetchIncidents, fetchGraph, fetchSystemStatus, 
  runSimulation, approveResponse 
} from './services/api';

import { ShieldCheck, UserCheck, AlertTriangle, ArrowRight, PlayCircle, Eye } from 'lucide-react';

export default function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('console'); // console, simulator, status

  // Core Data State
  const [events, setEvents] = useState([]);
  const [anomalies, setAnomalies] = useState({});
  const [incidents, setIncidents] = useState([]);
  const [activeIncident, setActiveIncident] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [systemStatus, setSystemStatus] = useState(null);
  const [latestSignal, setLatestSignal] = useState(null);
  const [simulationResults, setSimulationResults] = useState([]);

  // Live Workflow State
  const [activeStageId, setActiveStageId] = useState(1);
  const [stageData, setStageData] = useState(null);

  // Modals
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [selectedStrategyForApproval, setSelectedStrategyForApproval] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  // Load initial data
  const refreshAll = useCallback(async () => {
    try {
      const [evts, incs, grph, status] = await Promise.all([
        fetchEvents(35),
        fetchIncidents(),
        fetchGraph(),
        fetchSystemStatus()
      ]);
      setEvents(evts || []);
      setIncidents(incs || []);
      if (incs && incs.length > 0) {
        const primary = incs.find(i => i.status === 'ACTIVE') || incs[0];
        setActiveIncident(primary);
        if (primary.recommended_action) {
          setSelectedStrategyForApproval(primary.recommended_action);
        }
      }
      setGraphData(grph || { nodes: [], edges: [] });
      setSystemStatus(status);
    } catch (e) {
      console.error('Failed to load initial data:', e);
    }
  }, []);

  useEffect(() => {
    refreshAll();

    // WebSocket initialization
    wsClient.connect();

    const unsubStatus = wsClient.on('connection_status', (data) => {
      setIsConnected(data.connected);
      if (data.connected) refreshAll();
    });

    const unsubInit = wsClient.on('initial_state', (data) => {
      if (data.events) setEvents(data.events);
      if (data.incidents && data.incidents.length > 0) {
        setIncidents(data.incidents);
        const primary = data.incidents.find(i => i.status === 'ACTIVE') || data.incidents[0];
        setActiveIncident(primary);
      }
      if (data.graph) setGraphData(data.graph);
      if (data.system_status) setSystemStatus(data.system_status);
    });

    const unsubEvent = wsClient.on('new_event', (payload) => {
      if (payload.event) {
        setEvents((prev) => [payload.event, ...prev.slice(0, 34)]);
      }
      if (payload.anomaly && payload.anomaly.classification !== 'NORMAL') {
        setAnomalies((prev) => ({
          ...prev,
          [payload.anomaly.event_id]: payload.anomaly
        }));
      }
      if (payload.signal) {
        setLatestSignal(payload.signal);
      }
    });

    const unsubIncident = wsClient.on('incident_created', (payload) => {
      const inc = payload.incident;
      setIncidents((prev) => {
        const filtered = prev.filter(i => i.id !== inc.id);
        return [inc, ...filtered];
      });
      setActiveIncident(inc);
      if (payload.recommendation) {
        setSelectedStrategyForApproval(payload.recommendation);
      }
    });

    const unsubGraph = wsClient.on('graph_updated', (rfGraph) => {
      if (rfGraph && rfGraph.nodes) {
        setGraphData(rfGraph);
      }
    });

    const unsubSim = wsClient.on('simulation_completed', (payload) => {
      setSimulationResults(payload.results || []);
    });

    const unsubApproval = wsClient.on('response_approved', (action) => {
      console.log('Response approved:', action);
    });

    const unsubContained = wsClient.on('incident_contained', (data) => {
      setIncidents((prev) => prev.map(i => i.id === data.incident_id ? { ...i, status: 'CONTAINED' } : i));
      setActiveIncident((prev) => prev?.id === data.incident_id ? { ...prev, status: 'CONTAINED' } : prev);
      setActiveStageId(13);
      setStageData({
        stage_id: 13,
        subtitle: 'Threat successfully contained across financial graph.'
      });
    });

    const unsubWorkflow = wsClient.on('workflow_stage_update', (stage) => {
      setActiveStageId(stage.stage_id);
      setStageData(stage);
    });

    return () => {
      unsubStatus();
      unsubInit();
      unsubEvent();
      unsubIncident();
      unsubGraph();
      unsubSim();
      unsubApproval();
      unsubContained();
      unsubWorkflow();
    };
  }, [refreshAll]);

  const handleSelectStrategyForApproval = (strategy) => {
    setSelectedStrategyForApproval(strategy);
    setApprovalModalOpen(true);
  };

  const handleResponseExecuted = () => {
    refreshAll();
  };

  const isIncidentActive = activeIncident && activeIncident.status === 'ACTIVE';

  return (
    <div className="min-h-screen bg-soc-bg text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      
      {/* Top Navigation */}
      <Navbar 
        isConnected={isConnected}
        onAttackTriggered={() => {
          setActiveStageId(1);
          setStageData({ stage_id: 1, subtitle: 'Synthetic attack sequence initiated.' });
        }}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5">
        
        {/* CENTERPIECE: 13-STAGE LIVE WORKFLOW PIPELINE */}
        <LiveWorkflowPipeline 
          activeStageId={activeStageId}
          stageData={stageData}
          incidentStatus={activeIncident?.status}
          onSelectStage={(id) => {
            if (id >= 8) setActiveTab('simulator');
            else if (id === 3) setActiveTab('status');
            else setActiveTab('console');
          }}
        />

        {/* Global SOC Metrics Banner */}
        <MetricsBanner 
          metrics={systemStatus?.metrics}
          activeIncident={activeIncident}
        />

        {/* Action Containment Banner (Visible when unmitigated threat is detected) */}
        {isIncidentActive && (
          <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-red-950/60 via-slate-900 to-soc-card border border-red-500/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
                <span className="text-xs font-mono uppercase font-bold text-red-400">
                  ACTION REQUIRED: ACTIVE FINANCIAL THREAT DETECTED
                </span>
                <span className="text-xs font-mono text-slate-300 font-bold">
                  [{activeIncident.id}: {activeIncident.threat_type}]
                </span>
              </div>
              <p className="text-xs text-slate-300 font-mono">
                Recommended Action: <strong className="text-emerald-300">{activeIncident.recommended_action?.label || 'Isolate Suspicious Hardware & Step-Up Auth'}</strong>
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => setDetailModalOpen(true)}
                className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono flex items-center space-x-1.5 border border-slate-700 transition-colors"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>INSPECT INCIDENT</span>
              </button>

              <button
                onClick={() => {
                  setSelectedStrategyForApproval(activeIncident.recommended_action || {
                    strategy: 'COMBINED',
                    label: 'Coordinated Response',
                    containment_score: 96.5,
                    customer_friction: 'MEDIUM'
                  });
                  setApprovalModalOpen(true);
                }}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs font-mono flex items-center space-x-1.5 shadow-lg shadow-emerald-950/40 transition-all active:scale-95"
              >
                <UserCheck className="w-4 h-4" />
                <span>APPROVE RESPONSE</span>
              </button>
            </div>
          </div>
        )}

        {/* Tab 1: SOC Console (Main Operational View) */}
        {activeTab === 'console' && (
          <div className="space-y-6">
            
            {/* Split Screen: Live Event Stream (Left) vs. Temporal Threat Graph (Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              
              {/* Left Column: Live Event Stream (5 Cols) */}
              <div className="lg:col-span-5">
                <LiveEventStream 
                  events={events}
                  anomalies={anomalies}
                />
              </div>

              {/* Right Column: Temporal Financial Graph (7 Cols) */}
              <div className="lg:col-span-7">
                <ThreatGraphView 
                  graphData={graphData}
                  onRefresh={() => fetchGraph(activeIncident?.id).then(setGraphData)}
                  activeIncident={activeIncident}
                />
              </div>

            </div>

            {/* Bottom Row: Threat DNA & Dynamic Propagation Forecast */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <ThreatDnaCard 
                dna={activeIncident?.threat_dna}
                incident={activeIncident}
              />
              <PropagationForecastCard 
                forecast={activeIncident?.propagation_forecast}
                incident={activeIncident}
              />
            </div>

            {/* Edge Ingestion Nodes & PQC Integrity Strip */}
            <EdgeNodesMap 
              systemStatus={systemStatus}
              latestSignal={latestSignal}
            />

          </div>
        )}

        {/* Tab 2: Attack Simulator & Strategy Matrix */}
        {activeTab === 'simulator' && (
          <div className="space-y-6">
            <AttackSimulator 
              incident={activeIncident}
              simulationResults={simulationResults}
              onSelectStrategyForApproval={handleSelectStrategyForApproval}
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <PropagationForecastCard 
                forecast={activeIncident?.propagation_forecast}
                incident={activeIncident}
              />
              <ThreatDnaCard 
                dna={activeIncident?.threat_dna}
                incident={activeIncident}
              />
            </div>
          </div>
        )}

        {/* Tab 3: System Status & Edge Infrastructure */}
        {activeTab === 'status' && (
          <div className="space-y-6">
            <SystemStatusPanel systemStatus={systemStatus} />
            <EdgeNodesMap 
              systemStatus={systemStatus}
              latestSignal={latestSignal}
            />
          </div>
        )}

      </main>

      {/* Human Approval Modal */}
      <HumanApprovalModal 
        isOpen={approvalModalOpen}
        onClose={() => setApprovalModalOpen(false)}
        incident={activeIncident}
        strategy={selectedStrategyForApproval}
        onResponseExecuted={handleResponseExecuted}
      />

      {/* Incident Detail Modal */}
      <IncidentDetailModal 
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        incident={activeIncident}
        onOpenApproval={(strat) => {
          setSelectedStrategyForApproval(strat);
          setApprovalModalOpen(true);
        }}
      />

      {/* Footer */}
      <footer className="border-t border-soc-border py-4 mt-8 bg-soc-card/60 text-center text-xs font-mono text-slate-500">
        FinResolve Predict SOC Engine • Synthetic Demonstrational Prototype • Zero External Dependencies
      </footer>

    </div>
  );
}
