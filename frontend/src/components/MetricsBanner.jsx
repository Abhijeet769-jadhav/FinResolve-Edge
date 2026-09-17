import React from 'react';
import { Activity, AlertOctagon, Users, DollarSign, ShieldCheck, TrendingUp, Radio } from 'lucide-react';

export default function MetricsBanner({ metrics, activeIncident }) {
  const formatINR = (val) => {
    if (!val || isNaN(val)) return '₹0';
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Cr`;
    } else if (val >= 100000) {
      return `₹${(val / 100000).toFixed(2)} L`;
    }
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const isContained = activeIncident?.status === 'CONTAINED';

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5 mb-6">
      
      {/* Total Events */}
      <div className="bg-soc-card/90 backdrop-blur border border-soc-border rounded-xl p-3.5 flex flex-col justify-between relative overflow-hidden shadow-md group hover:border-blue-500/50 transition-all">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-cyan-400" />
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider font-semibold">Total Ingestion</span>
          <div className="p-1 rounded-md bg-blue-500/10 text-blue-400">
            <Activity className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {(metrics?.total_events || 0).toLocaleString()}
        </div>
        <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/80 text-[10px] font-mono">
          <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>12.5 EPS</span>
          </span>
          <span className="text-slate-500">Live Continuous</span>
        </div>
      </div>

      {/* Active Incidents */}
      <div className="bg-soc-card/90 backdrop-blur border border-soc-border rounded-xl p-3.5 flex flex-col justify-between relative overflow-hidden shadow-md group hover:border-rose-500/50 transition-all">
        <div className={`absolute top-0 left-0 right-0 h-1 ${activeIncident ? 'bg-gradient-to-r from-rose-500 to-red-600' : 'bg-slate-700'}`} />
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider font-semibold">Active Incidents</span>
          <div className={`p-1 rounded-md ${activeIncident ? 'bg-rose-500/20 text-rose-400 animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
            <AlertOctagon className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {String(metrics?.active_incidents || (activeIncident ? 1 : 0)).padStart(2, '0')}
        </div>
        <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/80 text-[10px] font-mono">
          <span className={activeIncident ? "text-rose-400 font-bold uppercase" : "text-slate-400"}>
            {activeIncident ? `${activeIncident.severity} SEV-1` : '0 Active Threats'}
          </span>
          <span className="text-slate-500">Correlation</span>
        </div>
      </div>

      {/* Accounts At Risk */}
      <div className="bg-soc-card/90 backdrop-blur border border-soc-border rounded-xl p-3.5 flex flex-col justify-between relative overflow-hidden shadow-md group hover:border-amber-500/50 transition-all">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-orange-400" />
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider font-semibold">Accounts At Risk</span>
          <div className="p-1 rounded-md bg-amber-500/10 text-amber-400">
            <Users className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {activeIncident ? activeIncident.affected_accounts?.length || 0 : (metrics?.accounts_at_risk || 0)}
        </div>
        <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/80 text-[10px] font-mono">
          <span className="text-amber-400 font-semibold">
            {activeIncident ? `${activeIncident.affected_devices?.length || 0} Devices` : 'Baseline Nominal'}
          </span>
          <span className="text-slate-500">Topology</span>
        </div>
      </div>

      {/* Financial Exposure */}
      <div className="bg-soc-card/90 backdrop-blur border border-soc-border rounded-xl p-3.5 flex flex-col justify-between relative overflow-hidden shadow-md group hover:border-rose-500/50 transition-all">
        <div className={`absolute top-0 left-0 right-0 h-1 ${isContained ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : 'bg-gradient-to-r from-rose-600 to-red-500'}`} />
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider font-semibold">Financial Exposure</span>
          <div className={`p-1 rounded-md ${isContained ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
            <DollarSign className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className={`text-2xl font-bold font-mono tracking-tight ${isContained ? 'text-emerald-300' : 'text-rose-300'}`}>
          {formatINR(activeIncident?.propagation_forecast?.horizons?.[0]?.estimated_exposure || metrics?.total_exposure || 0)}
        </div>
        <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/80 text-[10px] font-mono">
          <span className={isContained ? "text-emerald-400 font-semibold" : "text-slate-400"}>
            {isContained ? '100% Mitigated' : 'Unmitigated Run-Rate'}
          </span>
          <span className="text-slate-500">Horizon 0m</span>
        </div>
      </div>

      {/* Threat Posture / Containment */}
      <div className={`col-span-2 md:col-span-1 rounded-xl p-3.5 border flex flex-col justify-between relative overflow-hidden shadow-md transition-all ${
        isContained 
          ? 'bg-emerald-950/40 border-emerald-500/60 text-emerald-200' 
          : (activeIncident ? 'bg-rose-950/40 border-rose-500/60 text-rose-200 animate-pulse' : 'bg-soc-card/90 border-soc-border text-slate-300')
      }`}>
        <div className={`absolute top-0 left-0 right-0 h-1 ${isContained ? 'bg-emerald-400' : (activeIncident ? 'bg-red-500' : 'bg-slate-700')}`} />
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider font-semibold">Security Posture</span>
          <ShieldCheck className={`w-4 h-4 ${isContained ? 'text-emerald-400' : (activeIncident ? 'text-rose-400' : 'text-slate-400')}`} />
        </div>
        <div className="text-xl font-bold font-mono uppercase tracking-tight">
          {isContained ? 'CONTAINED' : (activeIncident ? 'ELEVATED SEV-1' : 'NOMINAL')}
        </div>
        <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/80 text-[10px] font-mono">
          <span className={isContained ? "text-emerald-400 font-semibold" : (activeIncident ? "text-rose-400 font-bold" : "text-slate-400")}>
            {isContained ? 'Response Enforced' : (activeIncident ? 'Action Required' : 'All Nodes Guarded')}
          </span>
        </div>
      </div>

    </div>
  );
}
