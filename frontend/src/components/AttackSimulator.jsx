import React, { useState } from 'react';
import { PlayCircle, CheckCircle2, ShieldAlert, BarChart2, Check, ArrowRight } from 'lucide-react';
import { runSimulation } from '../services/api';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend 
} from 'recharts';

export default function AttackSimulator({ incident, simulationResults, onSelectStrategyForApproval }) {
  const [horizon, setHorizon] = useState('60m');
  const [isSimulating, setIsSimulating] = useState(false);
  const [localResults, setLocalResults] = useState(simulationResults || []);
  const [selectedStrategy, setSelectedStrategy] = useState(null);

  React.useEffect(() => {
    if (simulationResults && simulationResults.length > 0) {
      setLocalResults(simulationResults);
    }
  }, [simulationResults]);

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
      <div className="bg-soc-card border border-soc-border rounded-xl p-8 flex flex-col justify-center items-center text-slate-500 font-mono text-xs">
        <PlayCircle className="w-10 h-10 text-slate-600 mb-2 animate-pulse" />
        <span>Select or inject an attack to initialize intervention simulation matrix...</span>
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
        </div>
      </div>

      {/* Dynamic Recommendation Banner */}
      {recommendedStrategy && (
        <div className="mb-5 p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500 text-slate-950">
                RECOMMENDED CONTAINMENT
              </span>
              <span className="text-sm font-bold text-emerald-300">
                {recommendedStrategy.label}
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-snug">
              {recommendedStrategy.recommendation_reason || recommendedStrategy.description}
            </p>
          </div>

          <button
            onClick={() => onSelectStrategyForApproval && onSelectStrategyForApproval(recommendedStrategy)}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center space-x-1.5 whitespace-nowrap shadow-lg shadow-emerald-900/40 transition-all"
          >
            <span>STAGE FOR APPROVAL</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Strategy Comparison Table */}
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-soc-border bg-soc-bg/60 text-slate-400 text-[10px] uppercase">
              <th className="p-2.5">Strategy</th>
              <th className="p-2.5">Accounts At Risk</th>
              <th className="p-2.5">Txns At Risk</th>
              <th className="p-2.5">Est. Exposure</th>
              <th className="p-2.5">Propagation</th>
              <th className="p-2.5">Friction</th>
              <th className="p-2.5">Containment Score</th>
              <th className="p-2.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-soc-border/50 text-slate-200">
            {localResults.map((strat) => {
              const isRec = strat.is_recommended;
              return (
                <tr 
                  key={strat.strategy} 
                  className={`transition-colors hover:bg-slate-800/40 ${isRec ? 'bg-emerald-950/20' : ''}`}
                >
                  <td className="p-2.5">
                    <div className="font-bold flex items-center space-x-1.5">
                      <span>{strat.label}</span>
                      {isRec && <span className="text-[9px] px-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">BEST</span>}
                    </div>
                    <div className="text-[10px] text-slate-400 truncate max-w-xs">{strat.description}</div>
                  </td>
                  <td className="p-2.5 font-bold">{strat.estimated_affected_accounts}</td>
                  <td className="p-2.5 text-slate-300">{strat.estimated_transactions_at_risk}</td>
                  <td className="p-2.5 text-rose-300 font-bold">{formatINR(strat.estimated_financial_exposure)}</td>
                  <td className="p-2.5">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      strat.propagation === 'LOW' ? 'bg-emerald-500/20 text-emerald-300' :
                      strat.propagation === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                      'bg-red-500/20 text-red-300'
                    }`}>
                      {strat.propagation}
                    </span>
                  </td>
                  <td className="p-2.5">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      strat.customer_friction === 'LOW' ? 'bg-emerald-500/20 text-emerald-300' :
                      strat.customer_friction === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                      'bg-purple-500/20 text-purple-300'
                    }`}>
                      {strat.customer_friction}
                    </span>
                  </td>
                  <td className="p-2.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-emerald-400 rounded-full" 
                          style={{ width: `${strat.containment_score}%` }}
                        />
                      </div>
                      <span className="font-bold text-slate-100">{strat.containment_score}%</span>
                    </div>
                  </td>
                  <td className="p-2.5 text-right">
                    <button
                      onClick={() => onSelectStrategyForApproval && onSelectStrategyForApproval(strat)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] border border-slate-700 hover:border-slate-500"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              );
            })}
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
            <Bar dataKey="containmentScore" name="Containment Score %" fill="#10B981" radius={[4, 4, 0, 0]} />
            <Bar dataKey="accountsAtRisk" name="Accounts at Risk" fill="#EF4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}
