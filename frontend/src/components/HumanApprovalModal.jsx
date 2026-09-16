import React, { useState } from 'react';
import { UserCheck, ShieldAlert, CheckCircle, XCircle, RefreshCw, AlertTriangle } from 'lucide-react';
import { approveResponse, rejectResponse } from '../services/api';

export default function HumanApprovalModal({ isOpen, onClose, incident, strategy, onResponseExecuted }) {
  if (!isOpen || !incident || !strategy) return null;

  const [analystNote, setAnalystNote] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      const result = await approveResponse(incident.id, strategy.strategy, analystNote);
      setExecutionResult({ type: 'APPROVED', data: result });
      if (onResponseExecuted) onResponseExecuted(result);
      setTimeout(() => {
        onClose();
        setExecutionResult(null);
      }, 1800);
    } catch (e) {
      console.error('Error approving response:', e);
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    setIsProcessing(true);
    try {
      const result = await rejectResponse(incident.id, strategy.strategy, analystNote);
      setExecutionResult({ type: 'REJECTED', data: result });
      if (onResponseExecuted) onResponseExecuted(result);
      setTimeout(() => {
        onClose();
        setExecutionResult(null);
      }, 1500);
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
                  <div className="text-base font-bold text-emerald-300">
                    CONTAINMENT PROTOCOL EXECUTED
                  </div>
                  <p className="text-slate-400 max-w-xs text-xs">
                    Target entities quarantined in temporal graph. Threat propagation halted.
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
                  <strong className="text-slate-200">{incident.id} ({incident.threat_type})</strong>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Intervention:</span>
                  <strong className="text-blue-300 font-bold">{strategy.label}</strong>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Containment Score:</span>
                  <span className="text-emerald-400 font-bold">{strategy.containment_score}%</span>
                </div>
                <div className="flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Customer Friction:</span>
                  <span className="text-amber-300 font-bold">{strategy.customer_friction}</span>
                </div>
              </div>

              {/* Entity Quarantine Target Details */}
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 text-[11px] text-amber-200 space-y-1">
                <div className="font-bold flex items-center space-x-1 text-amber-300">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Isolation Blast Radius:</span>
                </div>
                <div>• Devices to Quarantine: {incident.affected_devices.join(', ') || 'N/A'}</div>
                {incident.affected_recipients?.length > 0 && (
                  <div>• Beneficiary Holds: {incident.affected_recipients.join(', ')}</div>
                )}
                <div>• Affected Accounts Protected: {incident.affected_accounts.join(', ')}</div>
              </div>

              {/* Analyst Notes */}
              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  SOC Authorization Note (Audit Log):
                </label>
                <textarea
                  value={analystNote}
                  onChange={(e) => setAnalystNote(e.target.value)}
                  placeholder="e.g., Verified coordinated ATO vectors across 5 accounts. Authorized gateway quarantine."
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
                  className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold flex items-center space-x-1.5 transition-all shadow-lg shadow-emerald-950/50"
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
