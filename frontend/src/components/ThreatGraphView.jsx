import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  User, Smartphone, CreditCard, Landmark, Store, MapPin, 
  ShieldAlert, ShieldCheck, Info, RefreshCw, Server, Cpu, 
  Skull, Database, Play, Pause, RotateCcw, FastForward, Activity, Clock
} from 'lucide-react';
import { fetchIncidentReplaySteps } from '../services/api';

// Custom Financial Node Component with State-driven styling
function FinancialNodeComponent({ data }) {
  const { nodeType, label, risk, state, isBlocked, details, reason, metrics } = data;

  const getIcon = () => {
    switch (nodeType) {
      case 'ACCOUNT': return <User className="w-3.5 h-3.5" />;
      case 'DEVICE': return <Smartphone className="w-3.5 h-3.5" />;
      case 'TRANSACTION': return <CreditCard className="w-3.5 h-3.5" />;
      case 'RECIPIENT': return <Landmark className="w-3.5 h-3.5" />;
      case 'MERCHANT': return <Store className="w-3.5 h-3.5" />;
      case 'LOCATION': return <MapPin className="w-3.5 h-3.5" />;
      case 'EDGE_NODE': return <Server className="w-3.5 h-3.5 text-cyan-400" />;
      case 'GATEWAY': return <Cpu className="w-3.5 h-3.5 text-indigo-400" />;
      case 'ADVERSARY': return <Skull className="w-3.5 h-3.5 text-rose-400" />;
      case 'CORE_LEDGER': return <Database className="w-3.5 h-3.5 text-blue-400" />;
      default: return <Info className="w-3.5 h-3.5" />;
    }
  };

  const getStateBadge = () => {
    const st = state || (isBlocked ? 'BLOCKED' : (risk >= 75 ? 'CRITICAL' : risk >= 40 ? 'SUSPICIOUS' : 'NORMAL'));
    switch (st) {
      case 'BLOCKED':
        return <span className="px-1.5 py-0.5 rounded bg-red-600/30 text-red-300 border border-red-500 text-[8px] font-bold ring-1 ring-red-500/50">BLOCKED</span>;
      case 'STEP_UP':
      case 'CHALLENGED':
        return <span className="px-1.5 py-0.5 rounded bg-amber-500/30 text-amber-200 border border-amber-400 text-[8px] font-bold ring-1 ring-amber-500/50">STEP-UP AUTH</span>;
      case 'PROTECTED':
      case 'CONTAINED':
      case 'ISOLATED':
        return <span className="px-1.5 py-0.5 rounded bg-emerald-500/30 text-emerald-200 border border-emerald-400 text-[8px] font-bold ring-1 ring-emerald-500/50">PROTECTED</span>;
      case 'RESOLVED':
        return <span className="px-1 py-0.2 rounded bg-emerald-600/30 text-emerald-200 border border-emerald-500/60 text-[8px] font-bold">RESOLVED</span>;
      case 'PARTITIONED':
        return <span className="px-1 py-0.2 rounded bg-purple-500/30 text-purple-200 border border-purple-500/60 text-[8px] font-bold">PARTITIONED</span>;
      case 'BUFFERING':
        return <span className="px-1 py-0.2 rounded bg-amber-500/30 text-amber-200 border border-amber-500/60 text-[8px] font-bold">BUFFERING</span>;
      case 'TAMPERED':
        return <span className="px-1 py-0.2 rounded bg-rose-600/30 text-rose-200 border border-rose-500/60 text-[8px] font-bold">TAMPERED</span>;
      case 'CRITICAL':
      case 'ACTIVE_THREAT':
        return <span className="px-1 py-0.2 rounded bg-red-600/30 text-red-200 border border-red-500/60 text-[8px] font-bold animate-pulse">CRITICAL</span>;
      case 'SUSPICIOUS':
      case 'ELEVATED':
        return <span className="px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[8px] font-bold">SUSPICIOUS</span>;
      default:
        return <span className="px-1 py-0.2 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/50 text-[8px] font-bold">HEALTHY</span>;
    }
  };

  const getBorderColor = () => {
    // 1. Rogue adversary / blocked device (RED)
    if (state === 'BLOCKED' || (isBlocked && state !== 'PROTECTED' && state !== 'STEP_UP')) {
      return 'border-red-500 bg-red-950/85 text-red-200 ring-2 ring-red-500/70 shadow-lg shadow-red-950/70';
    }
    // 2. Step-up authentication / challenged entity (YELLOW / AMBER)
    if (state === 'STEP_UP' || state === 'CHALLENGED') {
      return 'border-amber-400 bg-amber-950/80 text-amber-200 ring-2 ring-amber-400/60 shadow-lg shadow-amber-950/60';
    }
    // 3. Protected customer account or quarantined sink (GREEN)
    if (state === 'PROTECTED' || state === 'CONTAINED' || state === 'ISOLATED') {
      return 'border-emerald-400 bg-emerald-950/80 text-emerald-200 ring-2 ring-emerald-400/60 shadow-lg shadow-emerald-950/60';
    }
    if (state === 'RESOLVED') {
      return 'border-emerald-500 bg-emerald-950/70 text-emerald-300 ring-1 ring-emerald-500/50';
    }
    if (state === 'PARTITIONED') {
      return 'border-purple-500 bg-purple-950/70 text-purple-200 ring-1 ring-purple-500/50';
    }
    if (state === 'TAMPERED') {
      return 'border-rose-500 bg-rose-950/80 text-rose-200 ring-1 ring-rose-500/60';
    }
    if (state === 'BUFFERING') {
      return 'border-amber-500 bg-amber-950/60 text-amber-200';
    }
    if (risk >= 75 || state === 'CRITICAL' || state === 'ACTIVE_THREAT') {
      return 'border-red-500 bg-red-950/80 text-red-200 ring-1 ring-red-500/50';
    }
    if (risk >= 40 || state === 'SUSPICIOUS') {
      return 'border-orange-500 bg-orange-950/60 text-orange-200';
    }
    // Normal / Benign / Healthy node
    return 'border-emerald-600/70 bg-emerald-950/35 text-emerald-200 ring-1 ring-emerald-500/30 hover:border-emerald-400';
  };

  const getHandleColor = () => {
    if (state === 'BLOCKED' || (isBlocked && state !== 'PROTECTED' && state !== 'STEP_UP')) return '!bg-red-500';
    if (state === 'STEP_UP' || state === 'CHALLENGED') return '!bg-amber-400';
    if (state === 'PROTECTED' || state === 'CONTAINED' || state === 'ISOLATED' || state === 'RESOLVED') return '!bg-emerald-400';
    if (risk >= 75 || state === 'CRITICAL' || state === 'ACTIVE_THREAT' || state === 'TAMPERED') return '!bg-red-500';
    if (risk >= 40 || state === 'SUSPICIOUS') return '!bg-amber-400';
    return '!bg-emerald-400';
  };

  return (
    <div className={`px-2.5 py-1.5 rounded-lg border text-xs font-mono min-w-[110px] max-w-[155px] shadow-md transition-all ${getBorderColor()}`}>
      <Handle type="target" position={Position.Left} className={`w-1.5 h-1.5 ${getHandleColor()}`} />
      
      <div className="flex items-center justify-between space-x-1.5 mb-1">
        <div className="flex items-center space-x-1">
          {getIcon()}
          <span className="text-[9px] font-bold uppercase tracking-wider text-slate-300">
            {nodeType}
          </span>
        </div>
        {getStateBadge()}
      </div>

      <div className="font-bold text-[11px] truncate text-slate-100" title={label}>
        {label}
      </div>

      {details?.amount ? (
        <div className="text-[10px] text-emerald-400 font-bold mt-0.5">
          ₹{details.amount.toLocaleString()}
        </div>
      ) : metrics?.events_buffered ? (
        <div className="text-[9px] text-amber-300 font-semibold mt-0.5">
          Buf: {metrics.events_buffered} | Failover: {metrics.failover}
        </div>
      ) : metrics?.filtered_rate ? (
        <div className="text-[9px] text-blue-300 font-semibold mt-0.5">
          Drop: {metrics.filtered_rate}
        </div>
      ) : reason ? (
        <div className="text-[8px] text-slate-400 truncate mt-0.5" title={reason}>
          {reason}
        </div>
      ) : null}

      <Handle type="source" position={Position.Right} className={`w-1.5 h-1.5 ${getHandleColor()}`} />
    </div>
  );
}

export default function ThreatGraphView({ graphData, onRefresh, activeIncident }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [showTimeline, setShowTimeline] = useState(false);
  const [rfInstance, setRfInstance] = useState(null);

  // Replay Attack State
  const [isReplaying, setIsReplaying] = useState(false);
  const [replaySteps, setReplaySteps] = useState([]);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [replaySpeed, setReplaySpeed] = useState(1);
  const replayTimerRef = useRef(null);

  const nodeTypes = useMemo(() => ({
    financialNode: FinancialNodeComponent,
  }), []);

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [timeline, setTimeline] = useState([]);

  // Sync graph state with strict capping and auto-centering
  useEffect(() => {
    if (graphData && !isReplaying) {
      const safeNodes = (graphData.nodes || []).slice(0, 50);
      const safeEdges = (graphData.edges || []).slice(0, 80);
      setNodes(safeNodes);
      setEdges(safeEdges);
      if (graphData.timeline) {
        setTimeline(graphData.timeline);
      }
      if (rfInstance && safeNodes.length > 0) {
        rfInstance.fitView({ padding: 0.18, duration: 350 });
      }
    }
  }, [graphData, rfInstance, isReplaying]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
  }, []);

  // Replay Attack Handlers
  const handleStartReplay = async () => {
    if (!activeIncident?.id) return;
    try {
      const res = await fetchIncidentReplaySteps(activeIncident.id);
      if (res?.steps && res.steps.length > 0) {
        setReplaySteps(res.steps);
        setIsReplaying(true);
        setCurrentStepIdx(0);
        applyReplayStep(res.steps[0]);
      } else {
        // Fallback synthetic steps from current nodes if no snapshot was captured
        const fallbackSteps = [
          { label: 'Step 1: Normal Ingress Baseline', graph: { nodes: nodes.slice(0, 10), edges: edges.slice(0, 8) } },
          { label: 'Step 2: Threat Anomaly Detected', graph: { nodes: nodes.slice(0, 20), edges: edges.slice(0, 18) } },
          { label: 'Step 3: Multi-Entity Nexus Correlated', graph: { nodes: nodes, edges: edges } },
        ];
        setReplaySteps(fallbackSteps);
        setIsReplaying(true);
        setCurrentStepIdx(0);
        applyReplayStep(fallbackSteps[0]);
      }
    } catch (e) {
      console.warn('Replay fetch failed, using current graph state:', e);
    }
  };

  const applyReplayStep = (step) => {
    if (!step?.graph) return;
    setNodes(step.graph.nodes || []);
    setEdges(step.graph.edges || []);
    if (rfInstance) rfInstance.fitView({ padding: 0.18, duration: 250 });
  };

  const togglePlayPause = () => {
    if (replayTimerRef.current) {
      clearInterval(replayTimerRef.current);
      replayTimerRef.current = null;
    } else {
      const intervalMs = Math.max(250, 1200 / replaySpeed);
      replayTimerRef.current = setInterval(() => {
        setCurrentStepIdx((prev) => {
          const next = prev + 1;
          if (next >= replaySteps.length) {
            clearInterval(replayTimerRef.current);
            replayTimerRef.current = null;
            return prev;
          }
          applyReplayStep(replaySteps[next]);
          return next;
        });
      }, intervalMs);
    }
  };

  const handleStopReplay = () => {
    if (replayTimerRef.current) {
      clearInterval(replayTimerRef.current);
      replayTimerRef.current = null;
    }
    setIsReplaying(false);
    if (graphData) {
      setNodes((graphData.nodes || []).slice(0, 50));
      setEdges((graphData.edges || []).slice(0, 80));
    }
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col h-[580px] shadow-lg relative font-mono">
      
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-soc-border mb-2 gap-2">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
          <h3 className="text-xs uppercase tracking-wider text-slate-200 font-bold">
            Canonical Threat Graph
          </h3>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            {nodes.length} Nodes / {edges.length} Edges
          </span>
          {isReplaying && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold animate-pulse">
              ⏪ REPLAY ACTIVE (Step {currentStepIdx + 1}/{replaySteps.length})
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2 text-xs">
          {/* Replay Attack Trigger Button */}
          {activeIncident?.id && !isReplaying && (
            <button
              onClick={handleStartReplay}
              className="px-2.5 py-1 rounded bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-500/50 flex items-center space-x-1 transition-all text-[11px] font-semibold"
              title="Replay this attack step-by-step"
            >
              <RotateCcw className="w-3 h-3 text-indigo-400" />
              <span>⏪ Replay Attack</span>
            </button>
          )}

          {/* Timeline Toggle */}
          <button
            onClick={() => setShowTimeline(!showTimeline)}
            className={`px-2 py-1 rounded border text-[11px] flex items-center space-x-1 transition-all ${
              showTimeline ? 'bg-cyan-950 text-cyan-300 border-cyan-500/60' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title="Toggle Live Mutation Timeline"
          >
            <Clock className="w-3 h-3" />
            <span>Timeline</span>
          </button>

          <button
            onClick={onRefresh}
            className="p-1 rounded bg-soc-bg border border-soc-border text-slate-400 hover:text-slate-200"
            title="Refresh Graph Layout"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Visual Color-Coding Legend */}
      <div className="flex flex-wrap items-center gap-3 py-1 px-2.5 bg-slate-900/90 border border-soc-border/70 rounded-lg mb-2 text-[10px]">
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/40 inline-block" />
          <span className="text-emerald-300 font-semibold">Protected / Healthy (Green)</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 ring-2 ring-red-500/40 inline-block" />
          <span className="text-red-300 font-semibold">Blocked Adversary (Red)</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 ring-2 ring-amber-400/40 inline-block" />
          <span className="text-amber-300 font-semibold">Step-Up Auth Challenge (Yellow)</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/40 animate-pulse inline-block" />
          <span className="text-rose-300 font-semibold">Active Threat (Red Pulse)</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block" />
          <span className="text-purple-300 font-semibold">Edge Partition (Purple)</span>
        </div>
      </div>

      {/* Replay Attack Floating Playback Controls Bar */}
      {isReplaying && (
        <div className="mb-2 p-2 rounded-lg bg-slate-900 border border-amber-500/40 flex items-center justify-between text-xs gap-3 shadow-xl">
          <div className="flex items-center space-x-2">
            <button
              onClick={togglePlayPause}
              className="p-1.5 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold flex items-center"
            >
              {replayTimerRef.current ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            </button>
            <span className="font-bold text-slate-200 text-[11px]">
              {replaySteps[currentStepIdx]?.label || `Step ${currentStepIdx + 1}`}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 text-[10px]">
              {[1, 5, 10].map((spd) => (
                <button
                  key={spd}
                  onClick={() => setReplaySpeed(spd)}
                  className={`px-1.5 py-0.5 rounded border ${
                    replaySpeed === spd ? 'bg-amber-500/30 text-amber-200 border-amber-500' : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}
                >
                  {spd}×
                </button>
              ))}
            </div>
            <button
              onClick={handleStopReplay}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] border border-slate-600"
            >
              Exit Replay
            </button>
          </div>
        </div>
      )}

      {/* React Flow Viewport */}
      <div className="flex-1 w-full h-full rounded-lg overflow-hidden relative border border-soc-border/50 bg-[#090D16]">
        {nodes.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-xs text-slate-500 space-y-2">
            <RefreshCw className="w-6 h-6 animate-spin text-slate-600" />
            <span>Connecting to Canonical Financial Graph...</span>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            onInit={setRfInstance}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#1E293B" gap={18} size={1} />
            <Controls showInteractive={false} className="!bg-slate-900 !border-slate-800" />
          </ReactFlow>
        )}

        {/* Node Inspector Card */}
        {selectedNode && (
          <div className="absolute top-3 right-3 w-68 bg-soc-card/95 border border-soc-border p-3 rounded-lg shadow-2xl backdrop-blur text-xs z-30">
            <div className="flex items-center justify-between pb-1.5 border-b border-soc-border mb-2">
              <span className="font-bold text-slate-200">{selectedNode.data?.nodeType} INSPECTOR</span>
              <button 
                onClick={() => setSelectedNode(null)} 
                className="text-slate-400 hover:text-slate-100"
              >
                ✕
              </button>
            </div>
            <div className="space-y-1.5 text-[11px]">
              <div><span className="text-slate-400">Node ID:</span> <strong className="text-slate-200">{selectedNode.id}</strong></div>
              <div>
                <span className="text-slate-400">State:</span>{' '}
                <strong className="text-cyan-300">{selectedNode.data?.state || 'NORMAL'}</strong>
              </div>
              <div>
                <span className="text-slate-400">Risk Score:</span>{' '}
                <span className="text-red-400 font-bold">{selectedNode.data?.risk || 15}/100</span>
              </div>
              {selectedNode.data?.reason && (
                <div className="p-1.5 rounded bg-slate-900/80 border border-slate-800 text-[10px] text-slate-300">
                  {selectedNode.data.reason}
                </div>
              )}
              {selectedNode.data?.details?.amount && (
                <div><span className="text-slate-400">Amount:</span> <span className="text-emerald-400 font-bold">₹{selectedNode.data.details.amount.toLocaleString()}</span></div>
              )}
              {selectedNode.data?.metrics?.failover && (
                <div><span className="text-slate-400">Failover Route:</span> <span className="text-purple-300 font-bold">{selectedNode.data.metrics.failover}</span></div>
              )}
            </div>
          </div>
        )}

        {/* Live Mutation Timeline Drawer */}
        {showTimeline && (
          <div className="absolute bottom-2 left-2 right-2 max-h-36 overflow-y-auto bg-black/90 border border-cyan-500/40 rounded-lg p-2.5 shadow-2xl backdrop-blur text-[10px] z-20 space-y-1">
            <div className="flex items-center justify-between border-b border-slate-800 pb-1 text-cyan-400 font-bold">
              <span>CANONICAL GRAPH TRANSITION LOG</span>
              <span className="text-slate-500 text-[9px]">{timeline.length} Events</span>
            </div>
            {timeline.length === 0 ? (
              <div className="text-slate-500">Baseline established. Zero active mutations.</div>
            ) : (
              timeline.slice(-8).reverse().map((m, idx) => (
                <div key={idx} className="flex items-center justify-between text-slate-300 py-0.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-500 font-semibold">{m.timestamp}</span>
                    <strong className="text-slate-100">{m.node_id}</strong>
                    <span className="text-cyan-400">→</span>
                    <span className="font-bold text-amber-300">[{m.state}]</span>
                  </div>
                  <span className="text-slate-400 truncate max-w-[240px]" title={m.reason}>
                    {m.reason}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </div>
  );
}

