'use client';

import { useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { Mail, Lock, User, AlertCircle } from 'lucide-react';
import { useNotification } from '@/contexts/NotificationContext';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const { login, register, loading, error } = useAuthContext();
  const { addNotification } = useNotification();
  const router = useRouter();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (!email || !password) {
      setLocalError('Email and password are required');
      return;
    }

    if (isRegisterMode && password.length < 8) {
      setLocalError('Password must be at least 8 characters');
      return;
    }

    const result = isRegisterMode
      ? await register(email, password, fullName)
      : await login(email, password);

    if (!result.success) {
      setLocalError(result.error || 'Authentication failed');
      return;
    }

    addNotification(
      'success',
      isRegisterMode ? 'Account created! Redirecting to dashboard...' : 'Welcome back! Redirecting...'
    );
    setEmail('');
    setPassword('');
    setFullName('');
    setIsRegisterMode(false);
    router.push('/dashboard');
  };

  const displayError = error || localError;

  return (
    <div className="w-full max-w-md">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-2xl blur-2xl"></div>
        
        <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-[hsl(0,0%,98%)] mb-6 text-center">
            {isRegisterMode ? 'Create Account' : 'Welcome Back'}
          </h2>

          {displayError && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400 text-sm">{displayError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegisterMode && (
              <div>
                <label className="block text-[hsl(220,10%,65%)] text-sm mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="John Doe"
                    className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-sm bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] placeholder-[hsl(220,10%,65%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-[hsl(220,10%,65%)] text-sm mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-sm bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] placeholder-[hsl(220,10%,65%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-[hsl(220,10%,65%)] text-sm mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-sm bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] placeholder-[hsl(220,10%,65%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition"
                />
              </div>
              {isRegisterMode && (
                <p className="text-xs text-[hsl(220,10%,65%)] mt-1">
                  Minimum 8 characters
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                isRegisterMode ? 'Create Account' : 'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setLocalError('');
              }}
              className="text-[hsl(220,90%,60%)] hover:text-[hsl(220,90%,70%)] transition text-sm"
            >
              {isRegisterMode
                ? 'Already have an account? Sign in'
                : "Don't have an account? Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
