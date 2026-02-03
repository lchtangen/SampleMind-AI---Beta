'use client';

import { useState, useEffect } from 'react';
import { Mic, Upload, Moon, Sun, Laptop } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useAuthContext } from '@/contexts/AuthContext';
import LoginForm from '@/components/LoginForm';
import { useRouter } from 'next/navigation';
import LoadingSpinner from '@/components/LoadingSpinner';

// Dynamically import the AIChatWindow component with no SSR
const AIChatWindow = dynamic(
  () => import('@/components/AIChatWindow'),
  { ssr: false }
);

// Theme toggle component
function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    setMounted(true);
    // Get theme from localStorage or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' || 'system';
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  const applyTheme = (newTheme: string) => {
    const root = window.document.documentElement;
    
    if (newTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.remove('light', 'dark');
      root.classList.add(systemTheme);
    } else {
      root.classList.remove('light', 'dark');
      root.classList.add(newTheme);
    }
    
    localStorage.setItem('theme', newTheme);
  };

  const toggleTheme = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  if (!mounted) {
    return (
      <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse"></div>
    );
  }

  return (
    <div className="flex items-center space-x-1 p-1 rounded-full bg-gray-100 dark:bg-gray-800">
      <button
        onClick={() => toggleTheme('light')}
        className={`p-2 rounded-full transition-colors ${theme === 'light' ? 'bg-white text-amber-500 shadow' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
        aria-label="Light mode"
      >
        <Sun className="h-4 w-4" />
      </button>
      <button
        onClick={() => toggleTheme('dark')}
        className={`p-2 rounded-full transition-colors ${theme === 'dark' ? 'bg-gray-900 text-blue-400 shadow' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
        aria-label="Dark mode"
      >
        <Moon className="h-4 w-4" />
      </button>
      <button
        onClick={() => toggleTheme('system')}
        className={`p-2 rounded-full transition-colors ${theme === 'system' ? 'bg-gray-200 dark:bg-gray-700 text-blue-500' : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
        aria-label="System preference"
      >
        <Laptop className="h-4 w-4" />
      </button>
    </div>
  );
}

export default function Home() {
  const [showChat, setShowChat] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [allowContentRender, setAllowContentRender] = useState(false);
  const { isAuthenticated, loading: authLoading, user } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading) {
      setAllowContentRender(true);
      return;
    }

    if (allowContentRender) {
      return;
    }

    const timer = setTimeout(() => {
      setAllowContentRender(true);
    }, 4000);
    return () => clearTimeout(timer);
  }, [authLoading, allowContentRender]);

  const showPreparingState = authLoading && !allowContentRender;

  return (
    <div className="min-h-screen flex flex-col">
      {showPreparingState && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm">
          <LoadingSpinner size="lg" text="Preparing experience..." />
        </div>
      )}
      {showChat ? (
        <AIChatWindow />
      ) : (
        <main className="flex-1 flex flex-col items-center justify-center p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
          <div className="w-full max-w-6xl mx-auto">
            {/* Header */}
            <header className="flex items-center justify-between mb-12">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">SM</span>
                </div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
                  SampleMind AI
                </h1>
              </div>
              <ThemeToggle />
            </header>

            {/* Hero Section */}
            <div className="glass p-8 rounded-2xl shadow-xl mb-12">
              <div className="grid lg:grid-cols-2 gap-10 items-start">
                <div>
                  <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
                AI-Powered Music Production
              </h2>
                  <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-xl">
                    Create, edit, and master your music with the power of artificial intelligence. Experience the future of music production today with real-time insights, audio analysis, and creative assistance.
              </p>
              
                  <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => setShowChat(true)}
                  className="btn btn-primary flex items-center justify-center space-x-2"
                >
                  <span>Talk to AI Assistant</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                  </svg>
                </button>
                
                    {isAuthenticated ? (
                      <button
                        onClick={() => router.push('/dashboard')}
                        className="btn btn-secondary flex items-center justify-center space-x-2"
                      >
                        <Upload className="h-5 w-5" />
                        <span>Open Dashboard</span>
                      </button>
                    ) : (
                <button
                  onClick={() => setIsLoading(!isLoading)}
                  className="btn btn-secondary flex items-center justify-center space-x-2"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Mic className="h-5 w-5" />
                      <span>Start Recording</span>
                    </>
                  )}
                </button>
                    )}
                  </div>

                  {isAuthenticated && (
                    <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                      Signed in as <span className="font-medium text-gray-700 dark:text-gray-200">{user?.full_name || user?.email}</span>. Jump into the dashboard to manage your projects.
                    </p>
                  )}
                </div>

                <div className="flex justify-center">
                  {isAuthenticated ? (
                    <div className="w-full max-w-md backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 text-center">
                      <h3 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                        You&apos;re all set!
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300 mb-6">
                        Access the dashboard to upload new tracks, monitor analysis, and view insights in real time.
                      </p>
                      <button
                        onClick={() => router.push('/dashboard')}
                        className="btn btn-primary w-full"
                      >
                        Go to Dashboard
                      </button>
                    </div>
                  ) : (
                    <LoginForm />
                  )}
                </div>
              </div>
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              {[
                {
                  icon: '🎵',
                  title: 'AI-Powered Composition',
                  description: 'Generate unique melodies and harmonies with our advanced AI algorithms.'
                },
                {
                  icon: '🎛️',
                  title: 'Smart Mixing',
                  description: 'Automatically balance and enhance your tracks with intelligent mixing tools.'
                },
                {
                  icon: '🎧',
                  title: 'Mastering',
                  description: 'Get professional-sounding masters with our AI mastering technology.'
                }
              ].map((feature, index) => (
                <div key={index} className="glass p-6 rounded-xl hover:shadow-lg transition-all duration-300">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-auto pt-8 pb-6 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>© {new Date().getFullYear()} SampleMind AI. All rights reserved.</p>
          </footer>
        </main>
      )}
    </div>
  );
}
