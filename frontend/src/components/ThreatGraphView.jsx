import React, { useState, useCallback, useMemo } from 'react';
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
  ShieldAlert, ShieldCheck, Info, RefreshCw, ZoomIn
} from 'lucide-react';

// Custom Financial Node Component
function FinancialNodeComponent({ data }) {
  const { nodeType, label, risk, isBlocked, details } = data;

  const getIcon = () => {
    switch (nodeType) {
      case 'ACCOUNT': return <User className="w-3.5 h-3.5" />;
      case 'DEVICE': return <Smartphone className="w-3.5 h-3.5" />;
      case 'TRANSACTION': return <CreditCard className="w-3.5 h-3.5" />;
      case 'RECIPIENT': return <Landmark className="w-3.5 h-3.5" />;
      case 'MERCHANT': return <Store className="w-3.5 h-3.5" />;
      case 'LOCATION': return <MapPin className="w-3.5 h-3.5" />;
      default: return <Info className="w-3.5 h-3.5" />;
    }
  };

  const getBorderColor = () => {
    if (isBlocked || risk === 'CONTAINED') {
      return 'border-emerald-500 bg-emerald-950/60 text-emerald-300';
    }
    switch (risk) {
      case 'CRITICAL':
        return 'border-red-500 bg-red-950/70 text-red-200 ring-1 ring-red-500/40';
      case 'HIGH':
        return 'border-orange-500 bg-orange-950/60 text-orange-200';
      case 'ELEVATED':
        return 'border-amber-500 bg-amber-950/40 text-amber-200';
      default:
        return 'border-slate-700 bg-slate-900/90 text-slate-300';
    }
  };

  return (
    <div className={`px-2.5 py-1.5 rounded-lg border text-xs font-mono transition-all duration-200 min-w-[100px] max-w-[140px] ${getBorderColor()}`}>
      <Handle type="target" position={Position.Left} className="w-1.5 h-1.5 !bg-slate-400" />
      
      <div className="flex items-center justify-between space-x-1.5 mb-0.5">
        <div className="flex items-center space-x-1">
          {getIcon()}
          <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
            {nodeType}
          </span>
        </div>
        {isBlocked || risk === 'CONTAINED' ? (
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
        ) : risk in { HIGH: 1, CRITICAL: 1 } ? (
          <ShieldAlert className="w-3 h-3 text-red-400" />
        ) : null}
      </div>

      <div className="font-semibold text-[11px] truncate" title={label}>
        {label}
      </div>

      {isBlocked ? (
        <div className="text-[8px] text-emerald-400 font-bold uppercase tracking-wide mt-0.5">
          [ISOLATED]
        </div>
      ) : details?.amount ? (
        <div className="text-[9px] text-emerald-400 font-bold">
          ₹{details.amount.toLocaleString()}
        </div>
      ) : null}

      <Handle type="source" position={Position.Right} className="w-1.5 h-1.5 !bg-slate-400" />
    </div>
  );
}

export default function ThreatGraphView({ graphData, onRefresh, activeIncident }) {
  const [selectedNode, setSelectedNode] = useState(null);

  const nodeTypes = useMemo(() => ({
    financialNode: FinancialNodeComponent,
  }), []);

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  React.useEffect(() => {
    if (graphData) {
      setNodes(graphData.nodes || []);
      setEdges(graphData.edges || []);
    }
  }, [graphData]);

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

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col h-[560px] shadow-lg relative">
      
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-soc-border mb-2">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Temporal Financial Threat Graph
          </h3>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            {nodes.length} Nodes / {edges.length} Edges
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          {/* Legend */}
          <div className="hidden sm:flex items-center space-x-2 text-[10px] text-slate-400">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-slate-500" />
              <span>Normal</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span>Compromised</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Contained</span>
            </span>
          </div>

          <button
            onClick={onRefresh}
            className="p-1 rounded bg-soc-bg border border-soc-border text-slate-400 hover:text-slate-200"
            title="Refresh Graph Layout"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* React Flow Viewport */}
      <div className="flex-1 w-full h-full rounded-lg overflow-hidden relative border border-soc-border/50 bg-[#090D16]">
        {nodes.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-xs font-mono text-slate-500 space-y-2">
            <RefreshCw className="w-6 h-6 animate-spin text-slate-600" />
            <span>Building financial entity topology...</span>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#1E293B" gap={18} size={1} />
            <Controls showInteractive={false} className="!bg-slate-900 !border-slate-800" />
          </ReactFlow>
        )}

        {/* Node Inspector Floating Card */}
        {selectedNode && (
          <div className="absolute top-3 right-3 w-64 bg-soc-card/95 border border-soc-border p-3 rounded-lg shadow-2xl backdrop-blur text-xs font-mono z-30">
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
              <div><span className="text-slate-400">ID:</span> <strong className="text-slate-200">{selectedNode.id}</strong></div>
              <div>
                <span className="text-slate-400">Risk Status:</span>{' '}
                <span className={`px-1 rounded text-[10px] font-bold ${
                  selectedNode.data?.isBlocked ? 'bg-emerald-500/20 text-emerald-300' :
                  selectedNode.data?.risk === 'CRITICAL' ? 'bg-red-500/20 text-red-300' :
                  'bg-slate-800 text-slate-300'
                }`}>
                  {selectedNode.data?.isBlocked ? 'ISOLATED' : (selectedNode.data?.risk || 'NORMAL')}
                </span>
              </div>
              {selectedNode.data?.details?.location && (
                <div><span className="text-slate-400">Location:</span> <span className="text-slate-200">{selectedNode.data.details.location}</span></div>
              )}
              {selectedNode.data?.details?.amount && (
                <div><span className="text-slate-400">Amount:</span> <span className="text-emerald-400 font-bold">₹{selectedNode.data.details.amount.toLocaleString()}</span></div>
              )}
              <div className="pt-1 text-[10px] text-slate-400 border-t border-slate-800">
                Connected to incident blast radius.
              </div>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
