'use client';

import React, { Component, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center p-6">
          <div className="max-w-md w-full">
            <div className="relative backdrop-blur-md bg-white/5 border border-red-500/30 rounded-2xl p-8">
              <div className="flex items-center space-x-4 mb-6">
                <div className="h-12 w-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                  <AlertCircle className="h-6 w-6 text-red-400" />
                </div>
                <h2 className="text-2xl font-bold text-[hsl(0,0%,98%)]">Something went wrong</h2>
              </div>
              <p className="text-[hsl(220,10%,65%)] mb-6">{this.state.error?.message || 'An unexpected error occurred'}</p>
              <button
                onClick={() => window.location.reload()}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg transition"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
