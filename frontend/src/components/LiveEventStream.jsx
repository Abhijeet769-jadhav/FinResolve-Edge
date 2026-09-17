import React, { useState } from 'react';
import { Activity, ShieldAlert, ChevronDown, ChevronUp, Pause, Play, Filter, Zap } from 'lucide-react';
import { injectStreamBatch } from '../services/api';

export default function LiveEventStream({ events, anomalies }) {
  const [isPaused, setIsPaused] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL'); // ALL, HIGH_RISK, TXN, AUTH
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedEventId, setExpandedEventId] = useState(null);
  const [isInjecting, setIsInjecting] = useState(false);

  const handleBurstInject = async () => {
    setIsInjecting(true);
    try {
      await injectStreamBatch(15);
    } catch (e) {
      console.error('Failed to inject burst:', e);
    } finally {
      setTimeout(() => setIsInjecting(false), 500);
    }
  };

  const getEventBadge = (type) => {
    switch (type) {
      case 'OTP_FAILURE':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'DEVICE_CHANGE':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'NEW_RECIPIENT':
        return 'bg-pink-500/20 text-pink-300 border-pink-500/40';
      case 'TRANSACTION':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'MERCHANT_PAYMENT':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
      case 'FAILED_LOGIN':
        return 'bg-red-500/20 text-red-300 border-red-500/40';
      default:
        return 'bg-slate-700/40 text-slate-300 border-slate-600/40';
    }
  };

  const filteredEvents = events.filter(evt => {
    // 1. Category Filter
    if (activeCategory === 'HIGH_RISK') {
      const anomaly = anomalies[evt.event_id];
      if (!anomaly || (anomaly.classification !== 'HIGH' && anomaly.classification !== 'CRITICAL')) return false;
    } else if (activeCategory === 'TXN') {
      if (evt.type !== 'TRANSACTION' && evt.type !== 'MERCHANT_PAYMENT') return false;
    } else if (activeCategory === 'AUTH') {
      if (evt.type !== 'OTP_FAILURE' && evt.type !== 'DEVICE_CHANGE' && evt.type !== 'FAILED_LOGIN') return false;
    }

    // 2. Search Query Filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const matchAcc = (evt.account_id || '').toLowerCase().includes(q);
      const matchDev = (evt.device_id || '').toLowerCase().includes(q);
      const matchRec = (evt.recipient_id || '').toLowerCase().includes(q);
      const matchMer = (evt.merchant_id || '').toLowerCase().includes(q);
      const matchType = (evt.type || '').toLowerCase().includes(q);
      const matchLoc = (evt.location || '').toLowerCase().includes(q);
      const matchId = (evt.event_id || '').toLowerCase().includes(q);
      const matchEdge = (evt.edge_id || '').toLowerCase().includes(q);
      if (!matchAcc && !matchDev && !matchRec && !matchMer && !matchType && !matchLoc && !matchId && !matchEdge) {
        return false;
      }
    }

    return true;
  });

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col h-[580px] shadow-lg">
      
      {/* Header & Controls */}
      <div className="flex items-center justify-between pb-2.5 border-b border-soc-border mb-2.5">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Live Event Stream
          </h3>
          <div className="flex items-center space-x-1.5 text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700/80">
            <span className={`w-1.5 h-1.5 rounded-full ${isPaused ? 'bg-amber-400' : 'bg-emerald-400 animate-ping'}`} />
            <span className={isPaused ? 'text-amber-300' : 'text-emerald-400 font-bold'}>
              {isPaused ? 'PAUSED' : 'LIVE'}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={handleBurstInject}
            disabled={isInjecting}
            className="px-2.5 py-1 rounded text-[11px] font-mono flex items-center space-x-1 border border-blue-600/50 bg-blue-950/40 text-blue-300 hover:bg-blue-900/60 hover:text-white transition-colors"
            title="Inject batch of 15 transactions immediately"
          >
            <Zap className={`w-3 h-3 ${isInjecting ? 'animate-bounce' : ''}`} />
            <span>+15 Evts</span>
          </button>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className="p-1.5 rounded bg-soc-bg border border-soc-border text-slate-400 hover:text-slate-200"
            title={isPaused ? "Resume auto-scroll" : "Pause stream"}
          >
            {isPaused ? <Play className="w-3 h-3 text-emerald-400" /> : <Pause className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="space-y-2 mb-2.5">
        <div className="flex items-center space-x-1.5">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search Acc, Dev, Recipient, Edge..."
              className="w-full bg-soc-bg border border-soc-border/80 rounded-lg px-2.5 py-1 text-[11px] font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1.5 text-slate-400 hover:text-slate-200 text-[10px]"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono">
          <div className="flex items-center space-x-1">
            {[
              { id: 'ALL', label: 'All' },
              { id: 'HIGH_RISK', label: 'High Risk' },
              { id: 'TXN', label: 'Txns' },
              { id: 'AUTH', label: 'Auth' }
            ].map(cat => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-2 py-0.5 rounded border transition-colors ${
                  activeCategory === cat.id
                    ? 'bg-blue-600/30 border-blue-500 text-blue-300 font-bold'
                    : 'bg-soc-bg/80 border-soc-border text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <span className="text-slate-500">
            {filteredEvents.length} of {events.length}
          </span>
        </div>
      </div>

      {/* Stream List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-xs font-mono text-slate-500 space-y-1">
            <span>No events match active filter</span>
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="text-blue-400 text-[11px] underline"
              >
                Clear search query
              </button>
            )}
          </div>
        ) : (
          filteredEvents.map((evt, index) => {
            const anomaly = anomalies[evt.event_id];
            const isHighRisk = anomaly && (anomaly.classification === 'HIGH' || anomaly.classification === 'CRITICAL');
            const isExpanded = expandedEventId === evt.event_id;
            const timeStr = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '--:--:--';
            const eventKey = evt.edge_id && evt.sequence_number != null
              ? `${evt.edge_id}-${evt.sequence_number}-${evt.timestamp || ''}-${index}`
              : `${evt.event_id || 'evt'}-${evt.timestamp || ''}-${index}`;

            return (
              <div 
                key={eventKey}
                className={`rounded-lg p-2.5 text-xs font-mono transition-all border ${
                  isHighRisk 
                    ? 'bg-rose-950/20 border-rose-700/50 hover:border-rose-500' 
                    : 'bg-soc-bg/80 border-soc-border/60 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                    <span className="text-slate-400 text-[10px]">{timeStr}</span>
                    <span className="font-bold text-slate-200">{evt.event_id}</span>
                    {evt.edge_id && (
                      <span 
                        className="text-[9px] px-1 py-0.2 rounded bg-indigo-950/70 text-indigo-300 border border-indigo-700/50 font-mono tracking-tight"
                        title={`Edge: ${evt.edge_id} | Sequence: #${evt.sequence_number ?? 'N/A'}`}
                      >
                        {evt.edge_id}{evt.sequence_number != null ? `:#${evt.sequence_number}` : ''}
                      </span>
                    )}
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
