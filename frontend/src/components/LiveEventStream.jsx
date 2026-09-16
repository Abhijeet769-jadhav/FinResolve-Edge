import React, { useState } from 'react';
import { Activity, ShieldAlert, ChevronDown, ChevronUp, Pause, Play, Filter } from 'lucide-react';

export default function LiveEventStream({ events, anomalies }) {
  const [isPaused, setIsPaused] = useState(false);
  const [filterCriticalOnly, setFilterCriticalOnly] = useState(false);
  const [expandedEventId, setExpandedEventId] = useState(null);

  const getEventBadge = (type) => {
    switch (type) {
      case 'OTP_FAILURE':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'DEVICE_CHANGE':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'NEW_RECIPIENT':
        return 'bg-pink-500/20 text-pink-300 border-pink-500/30';
      case 'TRANSACTION':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'MERCHANT_PAYMENT':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'FAILED_LOGIN':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-slate-700/40 text-slate-300 border-slate-600/40';
    }
  };

  const filteredEvents = events.filter(evt => {
    if (filterCriticalOnly) {
      const anomaly = anomalies[evt.event_id];
      return anomaly && (anomaly.classification === 'HIGH' || anomaly.classification === 'CRITICAL');
    }
    return true;
  });

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col h-[560px] shadow-lg">
      
      {/* Header & Controls */}
      <div className="flex items-center justify-between pb-3 border-b border-soc-border mb-2">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Live Event Stream
          </h3>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            {events.length} Recv
          </span>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setFilterCriticalOnly(!filterCriticalOnly)}
            className={`px-2 py-1 rounded text-[11px] font-mono flex items-center space-x-1 border transition-colors ${
              filterCriticalOnly 
                ? 'bg-rose-950/60 text-rose-300 border-rose-600' 
                : 'bg-soc-bg text-slate-400 border-soc-border hover:text-slate-200'
            }`}
            title="Filter anomalies only"
          >
            <Filter className="w-3 h-3" />
            <span>High Risk</span>
          </button>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className="p-1 rounded bg-soc-bg border border-soc-border text-slate-400 hover:text-slate-200"
            title={isPaused ? "Resume auto-scroll" : "Pause stream"}
          >
            {isPaused ? <Play className="w-3 h-3 text-emerald-400" /> : <Pause className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Stream List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs font-mono text-slate-500">
            Waiting for real-time transactions...
          </div>
        ) : (
          filteredEvents.map((evt) => {
            const anomaly = anomalies[evt.event_id];
            const isHighRisk = anomaly && (anomaly.classification === 'HIGH' || anomaly.classification === 'CRITICAL');
            const isExpanded = expandedEventId === evt.event_id;
            const timeStr = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '--:--:--';

            return (
              <div 
                key={evt.event_id}
                className={`rounded-lg p-2.5 text-xs font-mono transition-all border ${
                  isHighRisk 
                    ? 'bg-rose-950/20 border-rose-700/50 hover:border-rose-500' 
                    : 'bg-soc-bg/80 border-soc-border/60 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400 text-[10px]">{timeStr}</span>
                    <span className="font-bold text-slate-200">{evt.event_id}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded border uppercase ${getEventBadge(evt.type)}`}>
                      {evt.type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {anomaly && (
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${
                        anomaly.classification === 'CRITICAL' ? 'bg-red-500/30 text-red-300 border border-red-500' :
                        anomaly.classification === 'HIGH' ? 'bg-orange-500/30 text-orange-300 border border-orange-500' :
                        anomaly.classification === 'ELEVATED' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        Risk {anomaly.risk_score}
                      </span>
                    )}
                    {anomaly?.reasons?.length > 0 && (
                      <button 
                        onClick={() => setExpandedEventId(isExpanded ? null : evt.event_id)}
                        className="text-slate-400 hover:text-slate-200 p-0.5"
                      >
                        {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                      </button>
                    )}
                  </div>
                </div>

                {/* Event Core Entities */}
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-400">
                  <span>Acc: <strong className="text-slate-200">{evt.account_id}</strong></span>
                  <span>Dev: <strong className="text-slate-300">{evt.device_id}</strong></span>
                  <span>Loc: <strong className="text-slate-300">{evt.location}</strong></span>
                  {evt.amount > 0 && (
                    <span className="text-emerald-400 font-bold">₹{evt.amount.toLocaleString()}</span>
                  )}
                  {evt.recipient_id && (
                    <span>Rec: <strong className="text-amber-300">{evt.recipient_id}</strong></span>
                  )}
                  {evt.merchant_id && (
                    <span>Mer: <strong className="text-cyan-300">{evt.merchant_id}</strong></span>
                  )}
                </div>

                {/* Explainable Anomaly Factor Breakdown */}
                {isExpanded && anomaly && (
                  <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] space-y-1 bg-slate-900/60 p-2 rounded">
                    <div className="font-semibold text-rose-300 flex items-center space-x-1">
                      <ShieldAlert className="w-3 h-3" />
                      <span>Anomaly Reasoning & Risk Contributions:</span>
                    </div>
                    {anomaly.reasons?.map((reason, idx) => (
                      <div key={idx} className="text-slate-300 flex items-start space-x-1">
                        <span className="text-emerald-400">✓</span>
                        <span>{reason}</span>
                      </div>
                    ))}
                    {anomaly.factors?.map((f, idx) => (
                      <div key={idx} className="text-slate-400 flex justify-between">
                        <span>{f.description}</span>
                        <span className="text-amber-400 font-mono">+{f.score_contribution}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
