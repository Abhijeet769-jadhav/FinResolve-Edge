import React from 'react';
import { Activity } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export default function TelemetryActivityChart({ telemetryData = [] }) {
  const safeData = telemetryData.slice(-60);
  const latest = safeData[safeData.length - 1] || {
    events: 0,
    anomalies: 0,
    risk: 0,
    threat_level: 'NOMINAL'
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-3.5 shadow-lg font-mono mb-6">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-soc-border mb-2.5">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Decoupled SOC Telemetry Rate (60s Rolling Window)
          </h3>
          <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800">
            Static Recharts • 1 Hz
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="text-slate-400 text-[10px]">Throughput:</span>
            <strong className="text-cyan-300 text-[11px]">{latest.events} evts/s</strong>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span className="text-slate-400 text-[10px]">Anomalies:</span>
            <strong className="text-rose-300 text-[11px]">{latest.anomalies}/s</strong>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-slate-400 text-[10px]">Threat Level:</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold uppercase ${
              latest.threat_level === 'CRITICAL' ? 'bg-red-500/20 text-red-300 border border-red-500/40' :
              latest.threat_level === 'HIGH' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40' :
              latest.threat_level === 'CONTAINED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
              'bg-slate-800 text-slate-300'
            }`}>
              {latest.threat_level}
            </span>
          </div>
        </div>
      </div>

      <div className="h-28 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={safeData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis 
              dataKey="timestamp" 
              stroke="#64748B" 
              tick={{ fontSize: 9, fontFamily: 'monospace' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              stroke="#64748B" 
              tick={{ fontSize: 9, fontFamily: 'monospace' }}
              domain={[0, 'auto']}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#111827', 
                borderColor: '#374151', 
                borderRadius: '6px', 
                fontSize: '11px', 
                fontFamily: 'monospace' 
              }}
              formatter={(val, name) => [val, name === 'events' ? 'Events / Sec' : 'Anomalies / Sec']}
            />
            <Line 
              type="monotone" 
              dataKey="events" 
              stroke="#38BDF8" 
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
            <Line 
              type="monotone" 
              dataKey="anomalies" 
              stroke="#F43F5E" 
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
