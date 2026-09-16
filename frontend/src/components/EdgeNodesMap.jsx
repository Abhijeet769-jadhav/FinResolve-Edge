import React from 'react';
import { Cpu, Lock, ShieldCheck, Activity } from 'lucide-react';

export default function EdgeNodesMap({ systemStatus, latestSignal }) {
  const edgeNodes = systemStatus?.edge_nodes || {
    Pune: { status: 'ONLINE', latency_ms: 14, signals_processed: 142, anomalies_detected: 4 },
    Mumbai: { status: 'ONLINE', latency_ms: 12, signals_processed: 210, anomalies_detected: 8 },
    Delhi: { status: 'ONLINE', latency_ms: 18, signals_processed: 185, anomalies_detected: 3 },
    Bangalore: { status: 'ONLINE', latency_ms: 15, signals_processed: 198, anomalies_detected: 2 },
    Hyderabad: { status: 'ONLINE', latency_ms: 16, signals_processed: 130, anomalies_detected: 1 }
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 shadow-lg font-mono">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-soc-border mb-3">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Edge Ingestion Nodes & Cryptographic Integrity
          </h3>
        </div>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          5 NODES SYNCHRONIZED
        </span>
      </div>

      {/* Edge Nodes Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 mb-4">
        {Object.entries(edgeNodes).map(([nodeName, data]) => (
          <div 
            key={nodeName} 
            className="bg-soc-bg border border-soc-border/70 rounded-lg p-2.5 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-slate-200 text-xs">{nodeName}</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="text-[10px] text-slate-400 space-y-0.5">
              <div>Latency: <strong className="text-slate-200">{data.latency_ms || 15}ms</strong></div>
              <div>Signals: <strong className="text-slate-200">{data.signals_processed || 0}</strong></div>
              <div>Anomalies: <strong className="text-amber-400">{data.anomalies_detected || 0}</strong></div>
            </div>
          </div>
        ))}
      </div>

      {/* Post-Quantum Signal Integrity Verification Banner */}
      <div className="p-3 rounded-lg bg-slate-900 border border-slate-700/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
            <Lock className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-200">Post-Quantum Signal Integrity Layer</span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.2 rounded border border-emerald-500/30 font-bold">
                ML-DSA-65 VERIFIED
              </span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center space-x-2">
              <span>Digest: SHA-384</span>
              <span>•</span>
              <span className="text-slate-500">Demonstrational Cryptographic Abstraction</span>
            </div>
          </div>
        </div>

        {latestSignal && (
          <div className="text-[10px] text-right font-mono bg-soc-bg px-2 py-1 rounded border border-soc-border text-slate-300">
            <div>Last Sig: <span className="text-cyan-400">{latestSignal.signal_id}</span></div>
            <div className="truncate max-w-[180px] text-slate-500">{latestSignal.payload_hash?.substring(0, 16)}...</div>
          </div>
        )}
      </div>

    </div>
  );
}
