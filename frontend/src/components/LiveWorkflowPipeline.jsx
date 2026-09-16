import React from 'react';
import { 
  Activity, ArrowRight, Cpu, ShieldAlert, Network, Dna, 
  TrendingUp, PlayCircle, BarChart3, CheckSquare, UserCheck, 
  ShieldCheck, CheckCircle, ChevronRight
} from 'lucide-react';

export const WORKFLOW_STAGES = [
  { id: 1, key: 'EVENTS', label: 'Financial Events', icon: Activity, desc: 'Synthetic event stream generated' },
  { id: 2, key: 'INGESTION', label: 'Real-Time Ingestion', icon: Cpu, desc: 'Local edge ingestion buffer' },
  { id: 3, key: 'EDGE_ANOMALY', label: 'Edge Anomaly Detection', icon: ShieldAlert, desc: 'ML-DSA-65 / SHA-384 signed signal' },
  { id: 4, key: 'INCIDENT_FORMATION', label: 'Incident Formation', icon: Network, desc: 'Cross-entity anomaly aggregation' },
  { id: 5, key: 'TEMPORAL_GRAPH', label: 'Temporal Graph Engine', icon: Network, desc: 'NetworkX blast radius expansion' },
  { id: 6, key: 'THREAT_DNA', label: 'Threat DNA Extraction', icon: Dna, desc: 'Behavioral fingerprint & velocity' },
  { id: 7, key: 'PROPAGATION_FORECAST', label: 'Propagation Forecast', icon: TrendingUp, desc: 'Dynamic 15m/30m/60m projection' },
  { id: 8, key: 'ATTACK_SIMULATION', label: 'Attack Simulation', icon: PlayCircle, desc: '5 intervention strategies simulated' },
  { id: 9, key: 'INTERVENTION_COMPARISON', label: 'Intervention Comparison', icon: BarChart3, desc: 'Exposure vs. friction matrix' },
  { id: 10, key: 'RECOMMENDED_ACTION', label: 'Recommended Action', icon: CheckSquare, desc: 'Dynamic optimal containment pick' },
  { id: 11, key: 'HUMAN_APPROVAL', label: 'Human Approval', icon: UserCheck, desc: 'SOC Analyst gatekeeper review' },
  { id: 12, key: 'RESPONSE_EXECUTION', label: 'Response Execution', icon: ShieldCheck, desc: 'Automated entity quarantine' },
  { id: 13, key: 'INCIDENT_RESOLUTION', label: 'Incident Resolution', icon: CheckCircle, desc: 'Threat contained & stabilized' },
];

export default function LiveWorkflowPipeline({ activeStageId, stageData, onSelectStage, incidentStatus }) {
  // Determine overall status colors
  const isContained = incidentStatus === 'CONTAINED';

  return (
    <div className="w-full bg-soc-card border border-soc-border rounded-xl p-4 shadow-xl mb-6 relative overflow-hidden">
      
      {/* Background Subtle Gradient Glow */}
      <div className="absolute top-0 right-0 w-96 h-24 bg-blue-500/5 blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-soc-border/70">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping" />
          <h2 className="text-xs font-mono uppercase tracking-widest text-blue-400 font-semibold">
            End-To-End Threat Lifecycle Pipeline
          </h2>
          <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
            — Continuous Event-to-Containment Orchestration
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-slate-400">Current Phase:</span>
          {isContained ? (
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold flex items-center space-x-1">
              <CheckCircle className="w-3 h-3" />
              <span>CONTAINED (ALL 13 STAGES COMPLETE)</span>
            </span>
          ) : activeStageId > 0 ? (
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold animate-pulse">
              STAGE {activeStageId}: {WORKFLOW_STAGES.find(s => s.id === activeStageId)?.label.toUpperCase()}
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              IDLE MONITORING
            </span>
          )}
        </div>
      </div>

      {/* 13 Stage Flow Grid */}
      <div className="overflow-x-auto pb-2 scrollbar-thin">
        <div className="flex items-center min-w-[1100px] space-x-1.5 py-1">
          {WORKFLOW_STAGES.map((stage, idx) => {
            const Icon = stage.icon;
            const isCurrent = activeStageId === stage.id;
            const isCompleted = isContained || activeStageId > stage.id;
            const isUpcoming = !isContained && activeStageId < stage.id;

            // Compute stage card styling
            let cardBg = "bg-soc-bg/80 border-soc-border text-slate-500";
            let iconColor = "text-slate-500";
            let badgeStyle = "bg-slate-800 text-slate-500";

            if (isContained) {
              cardBg = "bg-emerald-950/20 border-emerald-800/40 text-emerald-300 hover:border-emerald-500/60";
              iconColor = "text-emerald-400";
              badgeStyle = "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
            } else if (isCurrent) {
              cardBg = "bg-blue-900/30 border-blue-500 text-slate-100 shadow-[0_0_15px_rgba(59,130,246,0.3)] ring-1 ring-blue-400";
              iconColor = "text-blue-400 animate-pulse";
              badgeStyle = "bg-blue-500 text-white font-bold animate-pulse";
            } else if (isCompleted) {
              cardBg = "bg-slate-900/90 border-slate-700 text-slate-300 hover:border-slate-500";
              iconColor = "text-emerald-400";
              badgeStyle = "bg-emerald-900/40 text-emerald-400 border border-emerald-700/40";
            }

            return (
              <React.Fragment key={stage.id}>
                <div 
                  onClick={() => onSelectStage && onSelectStage(stage.id)}
                  className={`flex-1 min-w-[95px] max-w-[125px] rounded-lg border p-2 flex flex-col justify-between transition-all cursor-pointer select-none group ${cardBg}`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${badgeStyle}`}>
                      #{stage.id}
                    </span>
                    <Icon className={`w-3.5 h-3.5 ${iconColor}`} />
                  </div>

                  <div className="text-[11px] font-semibold leading-tight mb-1 truncate group-hover:text-white" title={stage.label}>
                    {stage.label}
                  </div>

                  <div className="text-[9px] text-slate-400 truncate font-mono" title={stage.desc}>
                    {isCurrent ? (stageData?.subtitle || 'Processing...') : (isCompleted ? '✓ Completed' : 'Pending')}
                  </div>
                </div>

                {/* Arrow Connector */}
                {idx < WORKFLOW_STAGES.length - 1 && (
                  <div className="flex-shrink-0 flex items-center justify-center text-slate-600">
                    <ChevronRight className={`w-3.5 h-3.5 ${isCompleted ? 'text-emerald-500' : (isCurrent ? 'text-blue-400 animate-pulse' : 'text-slate-700')}`} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Live Stage Subtitle Telemetry Bar */}
      {stageData?.subtitle && (
        <div className="mt-3 px-3 py-2 rounded-lg bg-blue-950/40 border border-blue-800/40 flex items-center justify-between text-xs font-mono text-blue-200">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
            <span className="font-semibold text-blue-300">STAGE {stageData.stage_id} TELEMETRY:</span>
            <span>{stageData.subtitle}</span>
          </div>
          <span className="text-[10px] text-blue-400/80">{new Date().toLocaleTimeString()}</span>
        </div>
      )}

    </div>
  );
}
