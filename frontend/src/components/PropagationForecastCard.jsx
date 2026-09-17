import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, ShieldCheck, ArrowRight, Zap, Loader2 } from 'lucide-react';
import { 
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid 
} from 'recharts';
import { fetchForecast, injectAttack } from '../services/api';

export default function PropagationForecastCard({ forecast, incident }) {
  const [localForecast, setLocalForecast] = useState(forecast || incident?.propagation_forecast || null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInjecting, setIsInjecting] = useState(false);

  useEffect(() => {
    if (forecast) {
      setLocalForecast(forecast);
    } else if (incident?.propagation_forecast) {
      setLocalForecast(incident.propagation_forecast);
    } else if (incident?.id) {
      setIsLoading(true);
      fetchForecast(incident.id)
        .then(f => {
          if (f) setLocalForecast(f);
        })
        .catch(err => console.error("Failed to load forecast:", err))
        .finally(() => setIsLoading(false));
    } else {
      setLocalForecast(null);
    }
  }, [forecast, incident?.id, incident?.propagation_forecast]);

  const handleQuickInject = async () => {
    setIsInjecting(true);
    try {
      await injectAttack('account_takeover');
    } catch (e) {
      console.error('Failed to trigger attack:', e);
    } finally {
      setTimeout(() => setIsInjecting(false), 2000);
    }
  };

  const effectiveForecast = localForecast || forecast || incident?.propagation_forecast;

  if (!effectiveForecast) {
    return (
      <div className="bg-soc-card border border-soc-border rounded-xl p-6 flex flex-col justify-center items-center text-slate-400 font-mono text-xs h-full min-h-[260px] text-center shadow-lg">
        {isLoading ? (
          <>
            <Loader2 className="w-8 h-8 text-blue-400 mb-3 animate-spin" />
            <span className="text-slate-200 font-bold mb-1">Evaluating Graph Topology...</span>
            <span className="text-[11px] text-slate-500">Computing dynamic multi-hop propagation trajectory</span>
          </>
        ) : (
          <>
            <TrendingUp className="w-8 h-8 text-slate-600 mb-2" />
            <span className="text-slate-200 font-bold mb-1">Awaiting Threat Data</span>
            <p className="text-[11px] text-slate-400 max-w-sm mb-4">
              Select an active incident or trigger a synthetic attack scenario to compute dynamic multi-hop financial exposure forecasts.
            </p>
            <button
              onClick={handleQuickInject}
              disabled={isInjecting}
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center space-x-1.5 transition-all shadow-md shadow-blue-900/30 active:scale-95 disabled:opacity-50"
            >
              <Zap className={`w-3.5 h-3.5 ${isInjecting ? 'animate-bounce' : ''}`} />
              <span>{isInjecting ? 'INJECTING ATTACK...' : 'INJECT ATTACK TO FORECAST'}</span>
            </button>
          </>
        )}
      </div>
    );
  }
  const horizons = effectiveForecast.horizons || [];
  const isContained = incident?.status === 'CONTAINED';

  const formatINR = (val) => {
    if (!val || isNaN(val)) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${Number(val).toLocaleString('en-IN')}`;
  };

  const chartData = horizons.map(h => ({
    horizon: h.label,
    accounts: h.affected_accounts,
    transactions: h.transactions_at_risk,
    exposure: h.estimated_exposure / 100000 // In Lakhs for chart readability
  }));

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 shadow-lg flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-soc-border mb-3">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-rose-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Dynamic Threat Propagation Forecast
          </h3>
        </div>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
          isContained 
            ? 'bg-emerald-950/50 text-emerald-300 border-emerald-700' 
            : 'bg-rose-950/50 text-rose-300 border-rose-800 animate-pulse'
        }`}>
          {isContained ? 'GROWTH ARRESTED' : 'UNMITIGATED TRAJECTORY'}
        </span>
      </div>

      {/* Primary Vector & Info */}
      <div className="mb-2 text-[11px] font-mono flex items-center justify-between">
        <span className="text-slate-400">Primary Propagation Vector:</span>
        <span className="text-amber-300 font-bold">{effectiveForecast.primary_propagation_vector}</span>
      </div>

      {/* 4 Horizon Milestones with Progression Vector */}
      <div className="grid grid-cols-4 gap-2 mb-3 font-mono text-center">
        {horizons.map((h, idx) => (
          <div 
            key={h.label} 
            className={`p-2.5 rounded-lg border flex flex-col justify-between relative transition-all ${
              h.label === 'NOW' ? 'bg-soc-bg border-blue-500/70 shadow-sm shadow-blue-900/30' :
              isContained ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-200' :
              idx === horizons.length - 1 ? 'bg-rose-950/25 border-rose-600/50 shadow-sm shadow-rose-900/30' :
              'bg-soc-bg border-soc-border/70'
            }`}
          >
            <div className="flex items-center justify-between text-[10px] text-slate-400 font-semibold mb-1">
              <span>{h.label}</span>
              {idx > 0 && !isContained && (
                <span className="text-[9px] text-rose-400 font-normal">+{idx * 30}%</span>
              )}
            </div>
            <div className="text-base font-bold text-slate-100 my-0.5">
              {h.affected_accounts} <span className="text-[10px] font-normal text-slate-400">accs</span>
            </div>
            <div className={`text-[11px] font-bold ${
              isContained ? 'text-emerald-300' : idx === horizons.length - 1 ? 'text-rose-400 font-extrabold' : 'text-rose-300'
            }`}>
              {formatINR(h.estimated_exposure)}
            </div>
          </div>
        ))}
      </div>

      {/* Growth Curve Chart */}
      <div className="h-32 w-full mt-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="exposureGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isContained ? "#10B981" : "#EF4444"} stopOpacity={0.4}/>
                <stop offset="95%" stopColor={isContained ? "#10B981" : "#EF4444"} stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="horizon" stroke="#64748B" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
            <YAxis stroke="#64748B" tick={{ fontSize: 10, fontFamily: 'monospace' }} tickFormatter={(val) => `₹${val}L`} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '6px', fontSize: '11px', fontFamily: 'monospace' }}
              formatter={(value) => [`₹${Number(value).toFixed(2)} Lakhs`, 'Exposure']}
            />
            <Area 
              type="monotone" 
              dataKey="exposure" 
              stroke={isContained ? "#10B981" : "#EF4444"} 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#exposureGradient)" 
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Takeaway */}
      <div className="mt-2 text-[10px] font-mono text-slate-400 flex items-center justify-between border-t border-soc-border/60 pt-2">
        <span>Dynamic Graph Rate: <strong>{effectiveForecast.velocity_score}x / hr</strong></span>
        <span>Horizon: <strong>60-minute window</strong></span>
      </div>

    </div>
  );
}
