'use client';

import LoginForm from '@/components/LoginForm';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import ErrorBoundary from '@/components/ErrorBoundary';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <AuthProvider>
          <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center p-6">
            <div className="w-full max-w-6xl flex items-center justify-between">
              <div className="hidden lg:block flex-1 pr-12">
                <Link href="/" className="flex items-center space-x-3 mb-8">
                  <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                    <span className="text-white font-bold text-2xl">SM</span>
                  </div>
                  <h1 className="text-3xl font-bold text-[hsl(0,0%,98%)]">SampleMind AI</h1>
                </Link>
                <h2 className="text-4xl font-bold text-[hsl(0,0%,98%)] mb-4">
                  Revolutionary AI Music Production
                </h2>
                <p className="text-[hsl(220,10%,65%)] text-lg">
                  Analyze, transform, and master your audio with cutting-edge AI technology
                </p>
              </div>
              <div className="flex-1 max-w-md">
                <LoginForm />
              </div>
            </div>
          </div>
        </AuthProvider>
      </NotificationProvider>
    </ErrorBoundary>
  );
}
