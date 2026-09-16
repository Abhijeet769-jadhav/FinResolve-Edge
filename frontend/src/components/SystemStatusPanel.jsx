import React from 'react';
import { Server, CheckCircle2, ShieldCheck, Database, FileText, Info } from 'lucide-react';

export default function SystemStatusPanel({ systemStatus }) {
  const services = systemStatus?.services || {
    'Event Stream': 'ONLINE',
    'Graph Engine': 'ONLINE',
    'Anomaly Engine': 'ONLINE',
    'Threat DNA Engine': 'ONLINE',
    'Forecast Engine': 'ONLINE',
    'Simulation Engine': 'READY',
    'Response Engine': 'READY'
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-xl font-mono text-xs">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-soc-border mb-4">
        <div className="flex items-center space-x-2">
          <Server className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
            System & Infrastructure Health Status
          </h3>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
          ALL LOCAL SERVICES OPERATIONAL
        </span>
      </div>

      {/* Services List */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {Object.entries(services).map(([svcName, status]) => (
          <div key={svcName} className="bg-soc-bg p-3 rounded-lg border border-soc-border/70 flex items-center justify-between">
            <div>
              <div className="font-semibold text-slate-200 text-[11px]">{svcName}</div>
              <div className="text-[9px] text-slate-400">Local Daemon</div>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] font-bold text-emerald-400">{status}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Demonstrational Post-Quantum & Privacy Notice */}
      <div className="p-4 rounded-lg bg-slate-900 border border-slate-700 space-y-2">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold">
          <ShieldCheck className="w-4 h-4" />
          <span>Demonstrational Architecture & Data Privacy Notice</span>
        </div>
        <div className="text-slate-300 text-[11px] space-y-1 leading-relaxed">
          <p>
            • <strong>DEMO MODE:</strong> All financial events, accounts, devices, and merchant IDs are synthetically generated in-memory. No live banking systems or real customer data are ever connected.
          </p>
          <p>
            • <strong>POST-QUANTUM INTEGRITY:</strong> Cryptographic signatures simulate the NIST FIPS 204 <strong>ML-DSA-65</strong> verification envelope using local SHA-384 hashing and payload integrity abstractions for demonstration purposes.
          </p>
          <p>
            • <strong>LOCAL GRAPH COMPUTATION:</strong> The temporal graph engine runs fully locally using <strong>NetworkX</strong> with zero external cloud or database dependencies.
          </p>
        </div>
      </div>

    </div>
  );
}
