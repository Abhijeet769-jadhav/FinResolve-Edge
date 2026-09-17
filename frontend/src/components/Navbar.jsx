import React, { useState, useEffect } from 'react';
import { 
  Shield, Zap, RefreshCw, AlertTriangle, ChevronDown, CheckCircle2, 
  Lock, FlaskConical, Radio, RotateCcw, LayoutDashboard, Layers, Server, Clock
} from 'lucide-react';
import { injectAttack, resetIncidents } from '../services/api';

export default function Navbar({ isConnected, onAttackTriggered, onReset, activeTab, setActiveTab }) {
  const [isInjecting, setIsInjecting] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('account_takeover');
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const scenarios = [
    { id: 'account_takeover', name: 'Scenario 1: Coordinated Account Takeover', desc: 'Rogue device, multi-account probe, OTP fail, ₹18.5L transfer' },
    { id: 'mule_network', name: 'Scenario 2: Mule Network Expansion', desc: 'Rapid payments funneling into collector node REC-MULE-88' },
    { id: 'gateway_outage', name: 'Scenario 3: Regional Gateway Outage', desc: 'Cluster of 504 timeouts triggering operational failover & circuit breaker' },
    { id: 'weak_signals', name: 'Scenario 4: Weak Signals Progression', desc: '5 compound low-risk probes escalating to Emerging Coordinated Nexus' },
    { id: 'coordinated_fraud', name: 'Scenario 5: Coordinated Fraud Ring', desc: 'Multi-entity synchronized velocity spike across merchant endpoints' },
    { id: 'credential_stuffing', name: 'Scenario 6: Credential Stuffing Blast', desc: 'Distributed multi-IP authentication burst causing lockouts' }
  ];

  const handleSimulateAttack = async (scenarioId) => {
    setIsInjecting(true);
    setMenuOpen(false);
    try {
      await injectAttack(scenarioId);
      if (onAttackTriggered) onAttackTriggered(scenarioId);
    } catch (e) {
      console.error('Failed to inject attack:', e);
    } finally {
      setTimeout(() => setIsInjecting(false), 2000);
    }
  };

  const handleResetState = async () => {
    setIsResetting(true);
    try {
      await resetIncidents();
      if (onReset) onReset();
    } catch (e) {
      console.error('Failed to reset state:', e);
    } finally {
      setTimeout(() => setIsResetting(false), 800);
    }
  };

  return (
    <header className="border-b border-soc-border bg-soc-card/95 backdrop-blur-md sticky top-0 z-40 shadow-lg">
      <div className="w-full px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        
        {/* Brand & Live Pulse */}
        <div className="flex items-center space-x-3 sm:space-x-4 flex-shrink-0 min-w-max">
          <div 
            className="flex items-center space-x-2.5 flex-shrink-0 cursor-pointer select-none"
            onClick={() => setActiveTab && setActiveTab('console')}
          >
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600/30 to-cyan-500/20 border border-blue-500/50 flex items-center justify-center text-blue-400 shadow-md shadow-blue-900/30 flex-shrink-0">
              <Shield className="w-5 h-5 text-cyan-300" />
            </div>
            <div className="flex-shrink-0">
              <div className="flex items-center space-x-2 whitespace-nowrap">
                <span className="font-extrabold tracking-wider text-white text-base sm:text-lg font-mono whitespace-nowrap drop-shadow-sm">
                  FINRESOLVE PREDICT
                </span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/40 font-bold whitespace-nowrap">
                  v1.0 SOC
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono tracking-tight whitespace-nowrap hidden sm:block">
                Autonomous Financial Threat Defense & Simulation
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center pl-3.5 border-l border-soc-border space-x-2 flex-shrink-0">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]' : 'bg-amber-400'}`} />
            <span className="text-[11px] font-mono text-slate-300 whitespace-nowrap">{isConnected ? 'LIVE WEBSOCKET' : 'RECONNECTING'}</span>
          </div>

          {/* PQC Abstraction Pill */}
          <div className="hidden xl:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-[11px] text-slate-300 flex-shrink-0 whitespace-nowrap">
            <Lock className="w-3 h-3 text-cyan-400" />
            <span className="font-mono">PQC: ML-DSA-65</span>
            <span className="text-[9px] text-emerald-400 bg-emerald-500/10 px-1 py-0.2 rounded font-bold">VERIFIED</span>
          </div>

          {/* Continuous Event Stream Pill */}
          <div className="hidden 2xl:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-[11px] text-slate-300 flex-shrink-0 whitespace-nowrap">
            <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
            <span className="font-mono">STREAM</span>
            <span className="text-[9px] text-blue-300 bg-blue-500/10 px-1 py-0.2 rounded font-mono font-bold">12.5 EPS</span>
          </div>

          {/* Live SOC Clock */}
          <div className="hidden 2xl:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-[11px] font-mono text-slate-300 flex-shrink-0 whitespace-nowrap">
            <Clock className="w-3 h-3 text-cyan-400" />
            <span>{currentTime}</span>
          </div>
        </div>

        {/* Action Controls & Navigation */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          
          {/* Navigation Tabs */}
          <nav className="hidden sm:flex items-center space-x-1 bg-soc-bg/90 p-1 rounded-lg border border-soc-border shadow-inner">
            <button
              onClick={() => setActiveTab('console')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'console' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>SOC Console</span>
            </button>
            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'simulator' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Simulator</span>
            </button>
            <button
              onClick={() => setActiveTab('status')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'status' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Server className="w-3.5 h-3.5" />
              <span>System & Edge</span>
            </button>
            <button
              onClick={() => setActiveTab('testlab')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'testlab' 
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md font-semibold' 
                  : 'text-cyan-400 hover:text-cyan-200 hover:bg-slate-800/80'
              }`}
            >
              <FlaskConical className="w-3.5 h-3.5 text-cyan-300" />
              <span>TEST LAB</span>
            </button>
          </nav>

          {/* Quick Reset Baseline Button */}
          <button
            onClick={handleResetState}
            disabled={isResetting}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 text-xs transition-all shadow-sm"
            title="Reset Incident & Graph Telemetry to Nominal Baseline"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin text-blue-400' : ''}`} />
          </button>

          {/* Prominent Attack Simulator Trigger Button with Dropdown */}
          <div className="relative">
            <div className="flex rounded-lg shadow-sm border border-red-500/50 overflow-hidden shadow-red-950/40">
              <button
                onClick={() => handleSimulateAttack(selectedScenario)}
                disabled={isInjecting}
                className={`flex items-center space-x-2 px-3.5 py-1.5 text-xs font-semibold tracking-wide text-white transition-all ${
                  isInjecting 
                    ? 'bg-red-700 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 active:scale-95'
                }`}
              >
                {isInjecting ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>INJECTING...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5 text-amber-300" />
                    <span>SIMULATE ATTACK</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                disabled={isInjecting}
                className="px-2 bg-rose-800 hover:bg-rose-900 border-l border-red-400/40 text-white flex items-center justify-center transition-colors"
                title="Select Attack Scenario"
              >
                <ChevronDown className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Scenario Dropdown Menu */}
            {menuOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-lg bg-soc-card border border-soc-border shadow-2xl z-50 p-2 text-xs">
                <div className="px-2 py-1 text-[11px] font-mono uppercase text-slate-400 border-b border-soc-border mb-1">
                  Select Synthetic Attack Pattern
                </div>
                {scenarios.map((sc) => (
                  <button
                    key={sc.id}
                    onClick={() => {
                      setSelectedScenario(sc.id);
                      handleSimulateAttack(sc.id);
                    }}
                    className={`w-full text-left p-2.5 rounded-md transition-colors hover:bg-slate-800 flex flex-col space-y-0.5 ${
                      selectedScenario === sc.id ? 'border-l-2 border-red-500 bg-slate-800/60' : ''
                    }`}
                  >
                    <div className="font-semibold text-slate-100 flex items-center justify-between">
                      <span>{sc.name}</span>
                      {selectedScenario === sc.id && <span className="text-[10px] text-red-400 font-mono">SELECTED</span>}
                    </div>
                    <p className="text-[11px] text-slate-400 leading-tight">{sc.desc}</p>
                  </button>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
}
