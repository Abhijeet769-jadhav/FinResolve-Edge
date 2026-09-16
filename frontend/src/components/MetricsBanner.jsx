import React from 'react';
import { Activity, AlertOctagon, Users, DollarSign, ShieldCheck } from 'lucide-react';

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
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
      
      {/* Total Events */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-mono uppercase">Total Events</span>
          <Activity className="w-4 h-4 text-blue-400" />
        </div>
        <div className="text-xl font-bold font-mono text-slate-100">
          {(metrics?.total_events || 0).toLocaleString()}
        </div>
        <div className="text-[10px] text-emerald-400 font-mono mt-1">● Stream Active</div>
      </div>

      {/* Active Incidents */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-mono uppercase">Incidents</span>
          <AlertOctagon className="w-4 h-4 text-rose-500" />
        </div>
        <div className="text-xl font-bold font-mono text-slate-100">
          {String(metrics?.active_incidents || (activeIncident ? 1 : 0)).padStart(2, '0')}
        </div>
        <div className="text-[10px] text-slate-400 font-mono mt-1">
          {activeIncident ? `${activeIncident.severity} Severity` : '0 Active Threats'}
        </div>
      </div>

      {/* Accounts At Risk */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-mono uppercase">Accounts At Risk</span>
          <Users className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-xl font-bold font-mono text-slate-100">
          {activeIncident ? activeIncident.affected_accounts?.length || 0 : (metrics?.accounts_at_risk || 0)}
        </div>
        <div className="text-[10px] text-amber-400 font-mono mt-1">
          {activeIncident ? `${activeIncident.affected_devices?.length || 0} Devices Linked` : 'Baseline Normal'}
        </div>
      </div>

      {/* Financial Exposure */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-mono uppercase">Financial Exposure</span>
          <DollarSign className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-xl font-bold font-mono text-rose-300">
          {formatINR(activeIncident?.propagation_forecast?.horizons?.[0]?.estimated_exposure || metrics?.total_exposure || 0)}
        </div>
        <div className="text-[10px] text-slate-400 font-mono mt-1">
          {isContained ? 'Exposure Mitigated' : 'Unmitigated Run-Rate'}
        </div>
      </div>

      {/* Threat Status */}
      <div className={`col-span-2 md:col-span-1 rounded-lg p-3 border flex flex-col justify-between ${
        isContained 
          ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300' 
          : (activeIncident ? 'bg-rose-950/30 border-rose-500/40 text-rose-300' : 'bg-soc-card border-soc-border text-slate-300')
      }`}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-[11px] font-mono uppercase">SOC Containment</span>
          <ShieldCheck className={`w-4 h-4 ${isContained ? 'text-emerald-400' : 'text-slate-400'}`} />
        </div>
        <div className="text-base font-bold font-mono uppercase tracking-wide">
          {isContained ? 'CONTAINED' : (activeIncident ? 'THREAT ACTIVE' : 'NOMINAL')}
        </div>
        <div className="text-[10px] font-mono mt-1">
          {isContained ? 'Response Enforced' : (activeIncident ? 'Awaiting Containment' : 'Security Posture OK')}
        </div>
      </div>

    </div>
  );
}
