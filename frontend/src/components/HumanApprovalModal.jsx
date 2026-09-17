import React, { useState } from 'react';
import { UserCheck, ShieldAlert, CheckCircle, XCircle, RefreshCw, AlertTriangle } from 'lucide-react';
import { approveResponse, rejectResponse } from '../services/api';

export default function HumanApprovalModal({ isOpen, onClose, incident, strategy, onResponseExecuted, source = 'simulator' }) {
  if (!isOpen || !incident) return null;

  const activeStrategy = strategy || incident.recommended_action || {
    strategy: 'COMBINED',
    label: 'Coordinated Response (Device Isolation + Step-Up Auth)',
    containment_score: 96.5,
    customer_friction: 'MEDIUM',
    description: 'Multi-layered defense combining entity isolation and adaptive friction checks.'
  };

  const [analystNote, setAnalystNote] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);

  const isTestLabOrManual = source === 'testlab' || source === 'attack_trigger';
  const shouldAutoSpawn = !isTestLabOrManual;

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      const stratCode = typeof activeStrategy === 'string' ? activeStrategy : (activeStrategy.strategy || 'COMBINED');
      const result = await approveResponse(incident.id, stratCode, analystNote, source, shouldAutoSpawn);
      setExecutionResult({ type: 'APPROVED', data: result, autoSpawn: shouldAutoSpawn });
      if (onResponseExecuted) onResponseExecuted(result);
      setTimeout(() => {
        onClose();
        setExecutionResult(null);
        setIsProcessing(false);
      }, 1400);
    } catch (e) {
      console.error('Error approving response:', e);
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    setIsProcessing(true);
    try {
      const stratCode = typeof activeStrategy === 'string' ? activeStrategy : (activeStrategy.strategy || 'COMBINED');
      const result = await rejectResponse(incident.id, stratCode, analystNote);
      setExecutionResult({ type: 'REJECTED', data: result });
      if (onResponseExecuted) onResponseExecuted(result);
      setTimeout(() => {
        onClose();
        setExecutionResult(null);
        setIsProcessing(false);
      }, 1200);
    } catch (e) {
      console.error('Error rejecting response:', e);
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 font-mono">
      <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="bg-slate-900 px-5 py-4 border-b border-soc-border flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
              <UserCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
                Human Analyst Containment Gate
              </h3>
              <p className="text-[11px] text-slate-400">SOC Level 2 Remediation Authorization</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            disabled={isProcessing}
            className="text-slate-400 hover:text-slate-200 text-sm"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4 text-xs">
          
          {executionResult ? (
            <div className="py-8 flex flex-col items-center justify-center text-center space-y-2">
              {executionResult.type === 'APPROVED' ? (
                <>
                  <CheckCircle className="w-12 h-12 text-emerald-400 animate-bounce" />
                  <div className="text-base font-bold text-emerald-300 font-mono">
                    CONTAINMENT PROTOCOL EXECUTED (DONE)
                  </div>
                  <p className="text-slate-400 max-w-xs text-xs font-mono">
                    {executionResult.autoSpawn 
                      ? "Target entities quarantined. Incident marked as DONE. New threat telemetry arriving shortly..."
                      : "Target entities quarantined in temporal graph. Threat propagation halted."}
                  </p>
                </>
              ) : (
                <>
                  <XCircle className="w-12 h-12 text-rose-400" />
                  <div className="text-base font-bold text-rose-300">
                    INTERVENTION REJECTED BY ANALYST
                  </div>
                  <p className="text-slate-400 max-w-xs text-xs">
                    Incident remains active. Escalated to Tier 3 monitoring.
                  </p>
                </>
              )}
            </div>
          ) : (
            <>
              <div className="bg-soc-bg p-3.5 rounded-lg border border-soc-border/70 space-y-2">
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Target Incident:</span>
                  <strong className="text-slate-200 font-mono">{incident.id} ({incident.threat_type})</strong>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Intervention:</span>
                  <strong className="text-blue-300 font-bold">{activeStrategy.label || activeStrategy.strategy}</strong>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Arrest Efficiency:</span>
                  <span className="text-emerald-400 font-bold">{activeStrategy.containment_score || 95}% Containment</span>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Customer Friction:</span>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    activeStrategy.customer_friction === 'LOW' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                    activeStrategy.customer_friction === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                    'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                  }`}>
                    {activeStrategy.customer_friction || 'LOW'}
                  </span>
                </div>
              </div>

              {/* Entity Quarantine Target Details with Chips */}
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 text-[11px] text-amber-200 space-y-1.5">
                <div className="font-bold flex items-center space-x-1 text-amber-300">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Isolation Quarantine Perimeter:</span>
                </div>
                
                <div className="space-y-1">
                  <div className="flex items-center space-x-1 flex-wrap gap-1">
                    <span className="text-slate-400 text-[10px]">Devices:</span>
                    {(incident.affected_devices || []).map(d => (
                      <span key={d} className="px-1.5 py-0.2 rounded bg-red-950/60 text-red-300 border border-red-700/60 font-mono text-[10px]">
                        {d}
                      </span>
                    ))}
                  </div>

                  {incident.affected_recipients?.length > 0 && (
                    <div className="flex items-center space-x-1 flex-wrap gap-1">
                      <span className="text-slate-400 text-[10px]">Mule Sinks:</span>
                      {incident.affected_recipients.map(r => (
                        <span key={r} className="px-1.5 py-0.2 rounded bg-purple-950/60 text-purple-300 border border-purple-700/60 font-mono text-[10px]">
                          {r}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center space-x-1 flex-wrap gap-1">
                    <span className="text-slate-400 text-[10px]">Accounts:</span>
                    {(incident.affected_accounts || []).slice(0, 4).map(a => (
                      <span key={a} className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono text-[10px]">
                        {a}
                      </span>
                    ))}
                    {(incident.affected_accounts || []).length > 4 && (
                      <span className="text-slate-400 text-[10px]">
                        +{incident.affected_accounts.length - 4} more
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Analyst Notes with Quick Presets */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-[11px] font-semibold text-slate-300">
                    SOC Authorization Audit Trail:
                  </label>
                  <div className="flex items-center space-x-1">
                    {[
                      'Verified Malicious Fingerprint',
                      'High-Velocity Anomaly',
                      'Emergency Blast Containment'
                    ].map(preset => (
                      <button
                        key={preset}
                        type="button"
                        onClick={() => setAnalystNote(preset)}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700"
                      >
                        +{preset.split(' ')[0]}
                      </button>
                    ))}
                  </div>
                </div>
                <textarea
                  value={analystNote}
                  onChange={(e) => setAnalystNote(e.target.value)}
                  placeholder="e.g., Verified coordinated ATO vectors across accounts. Authorized edge quarantine."
                  rows={2}
                  className="w-full bg-soc-bg border border-soc-border rounded-lg p-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  onClick={handleReject}
                  disabled={isProcessing}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                >
                  REJECT INTERVENTION
                </button>
                <button
                  onClick={handleApprove}
                  disabled={isProcessing}
                  className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold flex items-center space-x-1.5 transition-all shadow-lg shadow-emerald-950/50 active:scale-95"
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>EXECUTING...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>APPROVE & CONTAIN</span>
                    </>
                  )}
                </button>
              </div>
            </>
          )}

        </div>

      </div>
    </div>
  );
}
