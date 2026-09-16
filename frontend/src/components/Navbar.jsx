import React, { useState } from 'react';
import { Shield, Zap, RefreshCw, AlertTriangle, ChevronDown, CheckCircle2, Lock } from 'lucide-react';
import { injectAttack } from '../services/api';

export default function Navbar({ isConnected, onAttackTriggered, activeTab, setActiveTab }) {
  const [isInjecting, setIsInjecting] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('account_takeover');
  const [menuOpen, setMenuOpen] = useState(false);

  const scenarios = [
    { id: 'account_takeover', name: 'Scenario 1: Coordinated Account Takeover', desc: 'Rogue device, multi-account probe, OTP fail, large transfer' },
    { id: 'mule_network', name: 'Scenario 2: Mule Network Expansion', desc: 'Many accounts routing rapid payments to concentrated recipient' },
    { id: 'merchant_attack', name: 'Scenario 3: Merchant/Payment Exploit', desc: 'Payment failures & retry explosion across POS terminals' }
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

  return (
    <header className="border-b border-soc-border bg-soc-card/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Live Pulse */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold tracking-wider text-slate-100 text-base">FINRESOLVE PREDICT</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">v1.0 SOC</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">Financial Threat Detection & Attack Simulation</p>
            </div>
          </div>

          <div className="hidden md:flex items-center pl-4 border-l border-soc-border space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]' : 'bg-amber-400'}`} />
            <span className="text-xs font-mono text-slate-300">{isConnected ? 'LIVE WEBSOCKET' : 'RECONNECTING'}</span>
          </div>

          {/* PQC Abstraction Pill */}
          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-[11px] text-slate-300">
            <Lock className="w-3 h-3 text-cyan-400" />
            <span className="font-mono">PQC: ML-DSA-65</span>
            <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1 rounded">VERIFIED</span>
          </div>
        </div>

        {/* Action Controls & Navigation */}
        <div className="flex items-center space-x-3">
          
          {/* Navigation Tabs */}
          <nav className="hidden sm:flex items-center space-x-1 bg-soc-bg p-1 rounded-lg border border-soc-border">
            <button
              onClick={() => setActiveTab('console')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                activeTab === 'console' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              SOC Console
            </button>
            <button
              onClick={() => setActiveTab('simulator')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                activeTab === 'simulator' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Simulator Matrix
            </button>
            <button
              onClick={() => setActiveTab('status')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                activeTab === 'status' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              System & Edge
            </button>
          </nav>

          {/* Prominent Attack Simulator Trigger Button with Dropdown */}
          <div className="relative">
            <div className="flex rounded-lg shadow-sm border border-red-500/40 overflow-hidden">
              <button
                onClick={() => handleSimulateAttack(selectedScenario)}
                disabled={isInjecting}
                className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold tracking-wide text-white transition-all ${
                  isInjecting 
                    ? 'bg-red-700 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 active:scale-95'
                }`}
              >
                {isInjecting ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>INJECTING ATTACK...</span>
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
                className="px-2 bg-rose-800 hover:bg-rose-900 border-l border-red-400/40 text-white flex items-center justify-center"
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
