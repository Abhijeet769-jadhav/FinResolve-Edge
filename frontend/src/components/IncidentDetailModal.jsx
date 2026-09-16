import React from 'react';
import { AlertOctagon, Clock, ShieldCheck, UserCheck, CheckCircle2, X } from 'lucide-react';
import ThreatDnaCard from './ThreatDnaCard';
import PropagationForecastCard from './PropagationForecastCard';

export default function IncidentDetailModal({ isOpen, onClose, incident, onOpenApproval }) {
  if (!isOpen || !incident) return null;

  const isContained = incident.status === 'CONTAINED';

  const formatINR = (val) => {
    if (!val || isNaN(val)) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${Number(val).toLocaleString('en-IN')}`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 font-mono">
      <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-4xl max-h-[90vh] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="bg-slate-900 px-6 py-4 border-b border-soc-border flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center border ${
              isContained ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30'
            }`}>
              <AlertOctagon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-base font-bold text-slate-100">{incident.id}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${
                  isContained ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                  incident.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-300 border-red-500/40' :
                  'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}>
                  {isContained ? 'CONTAINED' : incident.severity}
                </span>
              </div>
              <p className="text-xs text-slate-400">{incident.threat_type} • Confidence {incident.confidence}%</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {!isContained && incident.recommended_action && (
              <button
                onClick={() => {
                  onClose();
                  onOpenApproval(incident.recommended_action);
                }}
                className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center space-x-1.5 transition-all shadow-md"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>APPROVE CONTAINMENT</span>
              </button>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-100 p-1">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs scrollbar-thin">
          
          {/* Key Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-soc-bg p-3 rounded-lg border border-soc-border">
              <div className="text-[10px] text-slate-400">Risk Score</div>
              <div className="text-xl font-bold text-red-400">{incident.risk_score} / 100</div>
            </div>
            <div className="bg-soc-bg p-3 rounded-lg border border-soc-border">
              <div className="text-[10px] text-slate-400">Affected Accounts</div>
              <div className="text-xl font-bold text-slate-100">{incident.affected_accounts?.length || 0}</div>
            </div>
            <div className="bg-soc-bg p-3 rounded-lg border border-soc-border">
              <div className="text-[10px] text-slate-400">Affected Devices</div>
              <div className="text-xl font-bold text-slate-100">{incident.affected_devices?.length || 0}</div>
            </div>
            <div className="bg-soc-bg p-3 rounded-lg border border-soc-border">
              <div className="text-[10px] text-slate-400">First Detected</div>
              <div className="text-xs font-bold text-slate-200 mt-1 truncate">
                {incident.first_detected ? new Date(incident.first_detected).toLocaleTimeString() : 'N/A'}
              </div>
            </div>
          </div>

          {/* Side-by-Side: Threat DNA & Dynamic Forecast */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ThreatDnaCard dna={incident.threat_dna} incident={incident} />
            <PropagationForecastCard forecast={incident.propagation_forecast} incident={incident} />
          </div>

          {/* Incident Timeline */}
          <div className="bg-soc-card border border-soc-border rounded-xl p-4">
            <div className="flex items-center space-x-2 pb-2.5 border-b border-soc-border mb-3">
              <Clock className="w-4 h-4 text-blue-400" />
              <h4 className="text-xs font-bold uppercase text-slate-200">Incident Event Timeline</h4>
            </div>
            <div className="space-y-2.5">
              {incident.timeline?.map((item, idx) => (
                <div key={idx} className="flex items-start space-x-3 text-xs">
                  <span className="text-slate-400 text-[10px] pt-0.5 whitespace-nowrap">
                    {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '--:--:--'}
                  </span>
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="font-bold text-slate-200">{item.summary}</div>
                    <div className="text-[11px] text-slate-400">{item.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
