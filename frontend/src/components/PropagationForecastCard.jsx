import React from 'react';
import { TrendingUp, AlertTriangle, ShieldCheck, ArrowRight } from 'lucide-react';
import { 
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid 
} from 'recharts';

export default function PropagationForecastCard({ forecast, incident }) {
  if (!forecast && !incident?.propagation_forecast) {
    return (
      <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col justify-center items-center text-slate-500 font-mono text-xs h-full min-h-[260px]">
        <TrendingUp className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
        <span>Awaiting threat data to compute propagation forecast...</span>
      </div>
    );
  }

  const effectiveForecast = forecast || incident.propagation_forecast;
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

      {/* 4 Horizon Milestones */}
      <div className="grid grid-cols-4 gap-2 mb-3 font-mono text-center">
        {horizons.map((h) => (
          <div 
            key={h.label} 
            className={`p-2 rounded-lg border flex flex-col justify-between ${
              h.label === 'NOW' ? 'bg-soc-bg border-blue-500/50' :
              isContained ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-200' :
              'bg-soc-bg border-soc-border/70'
            }`}
          >
            <span className="text-[10px] text-slate-400 font-semibold">{h.label}</span>
            <div className="text-base font-bold text-slate-100 my-0.5">
              {h.affected_accounts} <span className="text-[10px] font-normal text-slate-400">accs</span>
            </div>
            <div className="text-[10px] text-rose-300 font-semibold">
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
