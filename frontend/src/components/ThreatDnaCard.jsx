import React from 'react';
import { Dna, Gauge, GitFork, Globe, Layers, CheckCircle2 } from 'lucide-react';

export default function ThreatDnaCard({ dna, incident }) {
  if (!dna && !incident) {
    return (
      <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-col justify-center items-center text-slate-500 font-mono text-xs h-full min-h-[220px]">
        <Dna className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
        <span>Awaiting active incident to extract Threat DNA...</span>
      </div>
    );
  }

  const effectiveDna = dna || incident?.threat_dna || {
    attack_type: incident?.threat_type || 'Coordinated Account Takeover',
    characteristics: [
      'Shared hardware fingerprint across multiple accounts',
      'Rapid OTP failure sequence preceding credential authorization',
      'Sudden high-velocity recipient addition'
    ],
    velocity: 'HIGH',
    coordination: 'HIGH',
    geographic_spread: 'MEDIUM',
    recipient_concentration: 'HIGH',
    historical_similarity: 88.4
  };

  const getLevelBadge = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-300 border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-slate-700/30 text-slate-300 border-slate-600/40';
    }
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-4 shadow-lg flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-soc-border mb-3">
        <div className="flex items-center space-x-2">
          <Dna className="w-4 h-4 text-purple-400" />
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">
            Threat DNA Fingerprint
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950/50 text-purple-300 border border-purple-800">
          GENOME EXTRACTED
        </span>
      </div>

      {/* Attack Type & Similarity */}
      <div className="mb-3">
        <div className="text-[11px] text-slate-400 font-mono">Identified Vector:</div>
        <div className="text-sm font-bold text-slate-100 font-mono tracking-wide">
          {effectiveDna.attack_type}
        </div>

        {/* Historical Similarity Progress */}
        <div className="mt-2">
          <div className="flex justify-between text-[11px] font-mono mb-1">
            <span className="text-slate-400">Historical Cluster Similarity:</span>
            <span className="text-purple-400 font-bold">{effectiveDna.historical_similarity}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700/60">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(effectiveDna.historical_similarity, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* DNA Dimension Tags with Mini Meters */}
      <div className="grid grid-cols-2 gap-2.5 mb-3 font-mono text-[11px]">
        {[
          { label: 'Velocity', val: effectiveDna.velocity, color: 'from-orange-500 to-red-500', pct: effectiveDna.velocity === 'CRITICAL' ? 100 : effectiveDna.velocity === 'HIGH' ? 80 : effectiveDna.velocity === 'MEDIUM' ? 50 : 25 },
          { label: 'Coordination', val: effectiveDna.coordination, color: 'from-purple-500 to-indigo-500', pct: effectiveDna.coordination === 'CRITICAL' ? 100 : effectiveDna.coordination === 'HIGH' ? 85 : effectiveDna.coordination === 'MEDIUM' ? 50 : 25 },
          { label: 'Geo Spread', val: effectiveDna.geographic_spread, color: 'from-amber-500 to-orange-500', pct: effectiveDna.geographic_spread === 'CRITICAL' ? 100 : effectiveDna.geographic_spread === 'HIGH' ? 75 : effectiveDna.geographic_spread === 'MEDIUM' ? 50 : 25 },
          { label: 'Mule Conc.', val: effectiveDna.recipient_concentration, color: 'from-rose-500 to-pink-500', pct: effectiveDna.recipient_concentration === 'CRITICAL' ? 100 : effectiveDna.recipient_concentration === 'HIGH' ? 90 : effectiveDna.recipient_concentration === 'MEDIUM' ? 50 : 25 },
        ].map((dim) => (
          <div key={dim.label} className="bg-soc-bg/90 p-2 rounded-lg border border-soc-border/70 flex flex-col justify-between space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-[10px]">{dim.label}:</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] border font-bold ${getLevelBadge(dim.val)}`}>
                {dim.val}
              </span>
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full bg-gradient-to-r ${dim.color} rounded-full`}
                style={{ width: `${dim.pct}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Characteristics List */}
      <div className="space-y-1 text-[11px] font-mono text-slate-300 bg-soc-bg/80 p-2.5 rounded-lg border border-soc-border/60">
        <div className="text-[10px] font-semibold text-slate-400 uppercase mb-1 flex items-center justify-between">
          <span>Observed Structural Markers:</span>
          <span className="text-purple-400 text-[9px]">{effectiveDna.characteristics?.length || 0} Patterns</span>
        </div>
        {effectiveDna.characteristics?.map((char, idx) => (
          <div key={idx} className="flex items-start space-x-1.5">
            <span className="text-purple-400 text-xs leading-none">•</span>
            <span className="leading-tight">{char}</span>
          </div>
        ))}
      </div>

    </div>
  );
}
