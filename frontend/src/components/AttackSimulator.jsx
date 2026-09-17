import React, { useState, useEffect } from 'react';
import { PlayCircle, CheckCircle2, ShieldAlert, BarChart2, Check, ArrowRight, Zap, Loader2, UserCheck } from 'lucide-react';
import { runSimulation, injectAttack, approveResponse } from '../services/api';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend 
} from 'recharts';

export default function AttackSimulator({ 
  incident, 
  incidents = [], 
  onSelectIncident, 
  simulationResults, 
  onSelectStrategyForApproval,
  onResponseExecuted
}) {
  const [horizon, setHorizon] = useState('60m');
  const [isSimulating, setIsSimulating] = useState(false);
  const [isInjecting, setIsInjecting] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [localResults, setLocalResults] = useState(simulationResults || []);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [countdownSeconds, setCountdownSeconds] = useState(null);

  // Sync when simulationResults prop updates from WebSocket or parent
  useEffect(() => {
    if (simulationResults && simulationResults.length > 0) {
      setLocalResults(simulationResults);
    }
  }, [simulationResults]);

  // Auto-run simulation when incident is provided or horizon changes
  useEffect(() => {
    if (incident?.id) {
      setIsSimulating(true);
      runSimulation(incident.id, horizon)
        .then(results => {
          if (results && results.length > 0) {
            setLocalResults(results);
          }
        })
        .catch(e => console.error('Failed to run simulation:', e))
        .finally(() => setIsSimulating(false));
    } else {
      setLocalResults([]);
    }
  }, [incident?.id, horizon]);

  // Live 9s countdown ticker when an incident is contained
  const isDone = incident?.status === 'CONTAINED' || incident?.status === 'RESOLVED';
  useEffect(() => {
    if (isDone) {
      setCountdownSeconds(9);
      const timer = setInterval(() => {
        setCountdownSeconds(prev => {
          if (prev === null || prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    } else {
      setCountdownSeconds(null);
    }
  }, [isDone, incident?.id]);

  const handleDirectApprove = async (strat) => {
    if (!incident || isApproving) return;
    setIsApproving(true);
    const stratCode = typeof strat === 'string' ? strat : (strat.strategy || 'COMBINED');
    try {
      const result = await approveResponse(incident.id, stratCode, 'Approved via Intervention Strategy Simulation Matrix', 'simulator', true);
      if (onResponseExecuted) {
        onResponseExecuted(result);
      }
    } catch (e) {
      console.error('Failed to approve strategy directly:', e);
    } finally {
      setIsApproving(false);
    }
  };

  const handleRunSimulation = async () => {
    if (!incident) return;
    setIsSimulating(true);
    try {
      const results = await runSimulation(incident.id, horizon);
      setLocalResults(results);
    } catch (e) {
      console.error('Failed to run simulation:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleQuickInject = async (scenario) => {
    setIsInjecting(true);
    try {
      await injectAttack(scenario);
    } catch (e) {
      console.error('Failed to inject attack:', e);
    } finally {
      setTimeout(() => setIsInjecting(false), 2000);
    }
  };

  const recommendedStrategy = localResults.find(s => s.is_recommended);

  const formatINR = (val) => {
    if (!val || isNaN(val)) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${Number(val).toLocaleString('en-IN')}`;
  };

  const chartData = localResults.map(s => ({
    name: s.strategy.replace('_', ' '),
    containmentScore: s.containment_score,
    accountsAtRisk: s.estimated_affected_accounts,
    exposureLakhs: (s.estimated_financial_exposure / 100000).toFixed(1)
  }));

  if (!incident) {
    return (
      <div className="bg-soc-card border border-soc-border rounded-xl p-8 flex flex-col justify-center items-center text-slate-400 font-mono text-xs text-center shadow-lg">
        <PlayCircle className="w-10 h-10 text-slate-600 mb-3" />
        <span className="text-slate-200 font-bold text-sm mb-1">
          Intervention Strategy Simulation Matrix
        </span>
        <p className="text-slate-400 max-w-md mb-5 text-[11px]">
          Simulates countermeasure trade-offs across 5 containment strategies, predicting exposure prevention, customer friction, and propagation arresting.
        </p>

        {incidents && incidents.length > 0 ? (
          <div className="flex flex-col items-center space-y-3 w-full max-w-sm">
            <span className="text-xs text-slate-300">Select an existing incident to evaluate:</span>
            <select
              onChange={(e) => {
                const found = incidents.find(i => i.id === e.target.value);
                if (found && onSelectIncident) onSelectIncident(found);
              }}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="">-- Choose Incident --</option>
              {incidents.map(inc => (
                <option key={inc.id} value={inc.id}>
                  {inc.id}: {inc.threat_type} ({inc.severity})
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="flex flex-wrap justify-center gap-2 max-w-md">
            <button
              onClick={() => handleQuickInject('account_takeover')}
              disabled={isInjecting}
              className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center space-x-1.5 transition-all shadow-md shadow-blue-900/30 active:scale-95 disabled:opacity-50"
            >
              <Zap className={`w-3.5 h-3.5 ${isInjecting ? 'animate-bounce' : ''}`} />
              <span>INJECT ACCOUNT TAKEOVER</span>
            </button>
            <button
              onClick={() => handleQuickInject('gateway_outage')}
              disabled={isInjecting}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 flex items-center space-x-1.5 transition-all"
            >
              <span>INJECT GATEWAY OUTAGE</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-xl font-mono">
      
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-soc-border mb-4">
        <div className="flex items-center space-x-2">
          <PlayCircle className="w-5 h-5 text-blue-400" />
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              Intervention Strategy Simulation Matrix
            </h3>
            <p className="text-[11px] text-slate-400 font-normal">
              Simulating countermeasure trade-offs for {incident.id} ({incident.threat_type})
            </p>
          </div>
        </div>

        {/* Horizon Toggle & Run Button */}
        <div className="flex items-center space-x-2 text-xs">
          {incidents && incidents.length > 1 && (
            <select
              value={incident.id}
              onChange={(e) => {
                const found = incidents.find(i => i.id === e.target.value);
                if (found && onSelectIncident) onSelectIncident(found);
              }}
              className="bg-soc-bg border border-soc-border rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              {incidents.map(inc => (
                <option key={inc.id} value={inc.id}>
                  {inc.id}: {inc.threat_type}
                </option>
              ))}
            </select>
          )}

          <div className="flex bg-soc-bg rounded-lg border border-soc-border p-0.5">
            {['15m', '30m', '60m'].map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-2.5 py-1 rounded text-[11px] transition-colors ${
                  horizon === h ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {h}
              </button>
            ))}
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className={`px-3.5 py-1.5 rounded-lg font-bold text-white transition-all text-xs flex items-center space-x-1.5 ${
              isSimulating ? 'bg-blue-800' : 'bg-blue-600 hover:bg-blue-500 active:scale-95'
            }`}
          >
            <PlayCircle className={`w-3.5 h-3.5 ${isSimulating ? 'animate-spin' : ''}`} />
            <span>{isSimulating ? 'EVALUATING...' : 'RUN SIMULATION'}</span>
          </button>

          <button
            onClick={() => handleQuickInject('account_takeover')}
            disabled={isInjecting}
            className="px-3 py-1.5 rounded-lg bg-red-600/90 hover:bg-red-500 text-white font-bold text-xs flex items-center space-x-1.5 transition-all shadow-md shadow-red-950/40 active:scale-95 disabled:opacity-50"
            title="Inject active synthetic threat scenario"
          >
            <Zap className={`w-3.5 h-3.5 ${isInjecting ? 'animate-bounce' : ''}`} />
            <span>{isInjecting ? 'INJECTING...' : 'INJECT THREAT'}</span>
          </button>
        </div>
      </div>

      {/* Dynamic Recommendation / Incident Done Banner */}
      {isDone && (
        <div className="mb-5 p-4 rounded-xl bg-gradient-to-r from-emerald-950/70 via-slate-900 to-emerald-950/50 border-2 border-emerald-500 shadow-xl shadow-emerald-950/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-in fade-in">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-emerald-500 text-slate-950 font-mono tracking-wider">
                INCIDENT DONE • CONTAINED & QUARANTINED
              </span>
              <span className="text-sm font-bold text-emerald-300 font-mono">
                {incident.id} ({incident.threat_type})
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-mono">
              Intervention strategy executed successfully. Target entities quarantined in canonical graph and threat growth arrested.
            </p>
            <div className="text-[11px] text-emerald-400 font-mono flex items-center space-x-2 pt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="font-bold">
                {countdownSeconds !== null && countdownSeconds > 0
                  ? `Auto-spawning next incoming threat scenario in ${countdownSeconds}s...`
                  : 'Awaiting next incoming threat telemetry stream...'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2 flex-shrink-0">
            <div className="px-3.5 py-2 rounded-lg bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 text-xs font-bold font-mono flex items-center space-x-1.5">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>CONTAINED (DONE)</span>
            </div>
            <button
              onClick={() => handleQuickInject('account_takeover')}
              disabled={isInjecting}
              className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs font-mono flex items-center space-x-1.5 shadow-lg shadow-blue-950/50 transition-all active:scale-95 disabled:opacity-50"
            >
              <Zap className={`w-3.5 h-3.5 ${isInjecting ? 'animate-bounce' : ''}`} />
              <span>{isInjecting ? 'INJECTING...' : 'INJECT NEXT THREAT'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Optimal Intervention Strategy Banner */}
      {recommendedStrategy && (
        <div className="mb-5 p-4 rounded-xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-emerald-950/30 border border-emerald-500/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg shadow-emerald-950/30 glow-border-emerald">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2.5">
              <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-emerald-500 text-slate-950 font-mono tracking-wider">
                ★ OPTIMAL INTERVENTION STRATEGY
              </span>
              <span className="text-sm font-bold text-emerald-300">
                {recommendedStrategy.label}
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/40">
                {recommendedStrategy.containment_score}% Arrest Rate
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
              {recommendedStrategy.recommendation_reason || recommendedStrategy.description}
            </p>
          </div>

          <div className="flex items-center space-x-2 flex-shrink-0">
            <button
              onClick={() => handleDirectApprove(recommendedStrategy)}
              disabled={isApproving}
              className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs flex items-center space-x-1.5 whitespace-nowrap shadow-lg shadow-emerald-950/50 transition-all active:scale-95 disabled:opacity-50"
              title="Directly approve and execute this optimal containment strategy"
            >
              <Check className="w-4 h-4" />
              <span>{isApproving ? 'DEPLOYING...' : isDone ? 'RE-APPROVE & DEPLOY' : 'APPROVE STRATEGY ✓'}</span>
            </button>

            <button
              onClick={() => onSelectStrategyForApproval && onSelectStrategyForApproval(recommendedStrategy, 'simulator')}
              className="px-3 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs flex items-center space-x-1 transition-all"
              title="Review in authorization modal"
            >
              <span>Review</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}

      {/* Strategy Comparison Table */}
      <div className="overflow-x-auto mb-6 rounded-lg border border-soc-border/60">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-soc-border bg-soc-bg text-slate-400 text-[10px] uppercase">
              <th className="p-3">Strategy</th>
              <th className="p-3">Accounts At Risk</th>
              <th className="p-3">Txns At Risk</th>
              <th className="p-3">Est. Exposure</th>
              <th className="p-3">Propagation</th>
              <th className="p-3">Friction</th>
              <th className="p-3">Containment Score</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-soc-border/50 text-slate-200">
            {localResults.length === 0 ? (
              <tr>
                <td colSpan="8" className="p-8 text-center text-slate-400 font-mono">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
                  <span>Computing multi-horizon countermeasure simulations...</span>
                </td>
              </tr>
            ) : (
              localResults.map((strat) => {
                const isRec = strat.is_recommended;
                const score = strat.containment_score || 0;
                const barColor = score >= 90 
                  ? 'from-emerald-500 to-teal-400' 
                  : score >= 75 
                  ? 'from-blue-500 to-cyan-400' 
                  : 'from-amber-500 to-orange-400';
                const isDeployed = isDone && strat.strategy === (incident?.containment_action?.strategy || incident?.recommended_action?.strategy);

                return (
                  <tr 
                    key={strat.strategy} 
                    className={`transition-colors hover:bg-slate-800/50 ${isRec ? 'bg-emerald-950/25' : ''}`}
                  >
                    <td className="p-3">
                      <div className="font-bold flex items-center space-x-1.5">
                        <span className={isRec ? 'text-emerald-300' : 'text-slate-100'}>{strat.label}</span>
                        {isRec && (
                          <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 font-bold">
                            BEST
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate max-w-xs">{strat.description}</div>
                    </td>
                    <td className="p-3 font-bold">{strat.estimated_affected_accounts}</td>
                    <td className="p-3 text-slate-300">{strat.estimated_transactions_at_risk}</td>
                    <td className="p-3 text-rose-300 font-bold">{formatINR(strat.estimated_financial_exposure)}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        strat.propagation === 'LOW' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                        strat.propagation === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                        'bg-red-500/20 text-red-300 border border-red-500/40'
                      }`}>
                        {strat.propagation}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        strat.customer_friction === 'LOW' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                        strat.customer_friction === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                        'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                      }`}>
                        {strat.customer_friction}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700/60">
                          <div 
                            className={`h-full bg-gradient-to-r ${barColor} rounded-full`} 
                            style={{ width: `${score}%` }}
                          />
                        </div>
                        <span className={`font-bold ${isRec ? 'text-emerald-300' : 'text-slate-200'}`}>{score}%</span>
                      </div>
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        {isDeployed && (
                          <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/50 text-[10px] font-bold flex items-center space-x-1">
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span>Deployed ✓</span>
                          </span>
                        )}
                        <button
                          onClick={() => handleDirectApprove(strat)}
                          disabled={isApproving}
                          className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all border ${
                            isRec 
                              ? 'bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold border-emerald-500 shadow-sm shadow-emerald-950/40' 
                              : 'bg-blue-600 hover:bg-blue-500 text-white font-bold border-blue-500 shadow-sm shadow-blue-950/40'
                          } disabled:opacity-50 active:scale-95`}
                          title="Directly approve and deploy this containment strategy"
                        >
                          {isApproving ? '...' : 'Approve'}
                        </button>
                        <button
                          onClick={() => onSelectStrategyForApproval && onSelectStrategyForApproval(strat, 'simulator')}
                          className="px-2.5 py-1 rounded-lg text-[10px] font-mono text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700"
                          title="Open human authorization gate modal"
                        >
                          Review
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Visual Chart Comparison */}
      <div className="h-44 w-full pt-2 border-t border-soc-border/60">
        <div className="text-[11px] font-semibold text-slate-400 uppercase mb-2">
          Containment Efficiency vs. Exposure Prevented:
        </div>
        <ResponsiveContainer width="100%" height="80%">
          <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="name" stroke="#64748B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
            <YAxis stroke="#64748B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '6px', fontSize: '11px', fontFamily: 'monospace' }}
            />
            <Bar dataKey="containmentScore" name="Containment Score %" fill="#10B981" radius={[4, 4, 0, 0]} isAnimationActive={false} />
            <Bar dataKey="accountsAtRisk" name="Accounts at Risk" fill="#EF4444" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}
