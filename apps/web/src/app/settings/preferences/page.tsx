'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useAuthContext } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/LoadingSpinner';

interface Preferences {
  analysis: {
    default_analysis_level: string;
    auto_analyze_on_upload: boolean;
    include_ai_analysis: boolean;
    preferred_ai_provider?: string;
    extract_all_features: boolean;
    cache_analysis_results: boolean;
  };
  ui: {
    theme: string;
    accent_color: string;
    language: string;
    compact_mode: boolean;
    show_tooltips: boolean;
    animations_enabled: boolean;
  };
  notifications: {
    email_on_analysis_complete: boolean;
    email_on_upload_error: boolean;
    in_app_notifications: boolean;
    notification_sound: boolean;
    digest_frequency: string;
  };
  cloud_sync: {
    enabled: boolean;
    sync_frequency: number;
    sync_library: boolean;
    sync_analysis_results: boolean;
    sync_settings: boolean;
    auto_backup: boolean;
    backup_frequency: string;
  };
}

export default function PreferencesPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load preferences
  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    const fetchPreferences = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/settings/preferences', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load preferences');
        }

        const data = await response.json();
        setPreferences(data.preferences);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load preferences');
      } finally {
        setLoading(false);
      }
    };

    fetchPreferences();
  }, [user, router]);

  const handleChange = (section: keyof Preferences, field: string, value: any) => {
    if (!preferences) return;
    setPreferences({
      ...preferences,
      [section]: {
        ...preferences[section],
        [field]: value,
      },
    });
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/settings/preferences', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to save preferences');
      }

      setSuccess('Preferences updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !preferences) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Link href="/settings">
            <button className="flex items-center text-slate-400 hover:text-slate-200 transition-colors">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </button>
          </Link>
          <h1 className="text-3xl font-bold text-white ml-4">Preferences</h1>
        </div>

        {/* Preferences Card */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-green-300 text-sm">
              {success}
            </div>
          )}

          {/* Analysis Preferences */}
          <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Analysis Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Default Analysis Level
                </label>
                <select
                  value={preferences.analysis.default_analysis_level}
                  onChange={(e) => handleChange('analysis', 'default_analysis_level', e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                >
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="detailed">Detailed</option>
                  <option value="professional">Professional</option>
                </select>
              </div>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.analysis.auto_analyze_on_upload}
                  onChange={(e) => handleChange('analysis', 'auto_analyze_on_upload', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Auto-analyze files after upload</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.analysis.include_ai_analysis}
                  onChange={(e) => handleChange('analysis', 'include_ai_analysis', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Include AI-powered analysis</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.analysis.cache_analysis_results}
                  onChange={(e) => handleChange('analysis', 'cache_analysis_results', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Cache analysis results for reuse</span>
              </label>
            </div>
          </div>

          {/* UI Preferences */}
          <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">UI Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Theme
                </label>
                <select
                  value={preferences.ui.theme}
                  onChange={(e) => handleChange('ui', 'theme', e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Accent Color
                </label>
                <select
                  value={preferences.ui.accent_color}
                  onChange={(e) => handleChange('ui', 'accent_color', e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                >
                  <option value="blue">Blue</option>
                  <option value="purple">Purple</option>
                  <option value="green">Green</option>
                  <option value="cyan">Cyan</option>
                </select>
              </div>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.ui.compact_mode}
                  onChange={(e) => handleChange('ui', 'compact_mode', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Compact mode</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.ui.animations_enabled}
                  onChange={(e) => handleChange('ui', 'animations_enabled', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Enable animations</span>
              </label>
            </div>
          </div>

          {/* Notification Preferences */}
          <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Notifications</h2>
            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.notifications.in_app_notifications}
                  onChange={(e) => handleChange('notifications', 'in_app_notifications', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">In-app notifications</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.notifications.email_on_analysis_complete}
                  onChange={(e) => handleChange('notifications', 'email_on_analysis_complete', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Email when analysis completes</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.notifications.notification_sound}
                  onChange={(e) => handleChange('notifications', 'notification_sound', e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-slate-300">Notification sounds</span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-4 pt-6">
            <button
              type="button"
              onClick={() => router.push('/settings')}
              className="px-6 py-2 rounded-lg border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white transition-colors disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
