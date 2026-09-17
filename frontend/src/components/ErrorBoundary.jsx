import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-soc-card border border-rose-600/50 rounded-xl p-6 m-4 text-slate-200 font-mono text-xs shadow-xl">
          <div className="flex items-center space-x-3 text-rose-400 mb-3">
            <AlertTriangle className="w-6 h-6 flex-shrink-0 animate-pulse" />
            <h3 className="text-sm font-bold">Component Render Error Recovered</h3>
          </div>
          <p className="text-slate-400 mb-4">
            {this.state.error?.message || 'An unexpected rendering error occurred in this view.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold flex items-center space-x-1.5 transition-all shadow-md active:scale-95"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Render</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
