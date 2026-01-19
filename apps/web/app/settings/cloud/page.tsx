'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Loader2, Cloud, RotateCw } from 'lucide-react';
import Link from 'next/link';
import { useAuthContext } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/LoadingSpinner';

interface CloudSyncSettings {
  enabled: boolean;
  sync_frequency: number;
  sync_library: boolean;
  sync_analysis_results: boolean;
  sync_settings: boolean;
  auto_backup: boolean;
  backup_frequency: string;
}

interface SyncStatus {
  enabled: boolean;
  syncing: boolean;
  progress?: number;
  last_sync?: string;
  next_sync?: string;
}

export default function CloudSyncPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncSettings, setSyncSettings] = useState<CloudSyncSettings | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load cloud sync settings
  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    const fetchSettings = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/settings/preferences', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load settings');
        }

        const data = await response.json();
        setSyncSettings(data.preferences.cloud_sync);

        // Also fetch sync status
        try {
          const statusResponse = await fetch('/api/v1/sync/status', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            setSyncStatus(statusData);
          }
        } catch (err) {
          console.warn('Could not fetch sync status');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [user, router]);

  const handleChange = (field: keyof CloudSyncSettings, value: any) => {
    if (!syncSettings) return;
    setSyncSettings({
      ...syncSettings,
      [field]: value,
    });
    setError(null);
    setSuccess(null);
  };

  const handleEnableSync = async () => {
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/sync/enable', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to enable sync');
      }

      setSuccess('Cloud sync enabled successfully!');
      if (syncSettings) {
        setSyncSettings({ ...syncSettings, enabled: true });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enable sync');
    }
  };

  const handleManualSync = async () => {
    setSyncing(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/sync/now', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to sync');
      }

      setSuccess('Sync completed successfully!');
      setTimeout(() => setSuccess(null), 3000);

      // Refresh status
      try {
        const statusResponse = await fetch('/api/v1/sync/status', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setSyncStatus(statusData);
        }
      } catch (err) {
        console.warn('Could not refresh sync status');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sync');
    } finally {
      setSyncing(false);
    }
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
        body: JSON.stringify({
          analysis: {},
          ui: {},
          notifications: {},
          cloud_sync: syncSettings,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to save settings');
      }

      setSuccess('Cloud sync settings updated!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !syncSettings) {
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
          <h1 className="text-3xl font-bold text-white ml-4">Cloud Sync</h1>
        </div>

        {/* Status Card */}
        {syncStatus && (
          <div className="mb-8 rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Cloud className="w-6 h-6 text-blue-400" />
                <div>
                  <h2 className="text-lg font-semibold text-white">
                    {syncStatus.enabled ? 'Cloud Sync' : 'Cloud Sync Disabled'}
                  </h2>
                  <p className="text-sm text-slate-400">
                    {syncStatus.syncing ? 'Currently syncing...' : 'Status is up to date'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                {syncStatus.last_sync && (
                  <p className="text-sm text-slate-400">
                    Last sync: {new Date(syncStatus.last_sync).toLocaleString()}
                  </p>
                )}
              </div>
            </div>

            {syncStatus.syncing && syncStatus.progress !== undefined && (
              <div className="mt-4">
                <div className="w-full h-2 rounded-full bg-slate-700/50 overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${syncStatus.progress}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-2">{syncStatus.progress}% complete</p>
              </div>
            )}
          </div>
        )}

        {/* Settings Form */}
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

          {/* Enable/Disable Sync */}
          <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Enable Cloud Sync</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Automatically synchronize your data across devices
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={syncSettings.enabled}
                  onChange={(e) => handleChange('enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {!syncSettings.enabled && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={handleEnableSync}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                >
                  Enable Cloud Sync
                </button>
              </div>
            )}
          </div>

          {/* Sync Frequency */}
          <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Sync Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Sync Frequency (seconds)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="30"
                    max="3600"
                    step="30"
                    value={syncSettings.sync_frequency}
                    onChange={(e) => handleChange('sync_frequency', parseInt(e.target.value))}
                    className="flex-1"
                    disabled={!syncSettings.enabled}
                  />
                  <span className="text-white font-medium min-w-20">
                    {syncSettings.sync_frequency}s
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  How often to check for changes (30s to 60m)
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={syncSettings.sync_library}
                    onChange={(e) => handleChange('sync_library', e.target.checked)}
                    disabled={!syncSettings.enabled}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-slate-300">Sync library metadata</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={syncSettings.sync_analysis_results}
                    onChange={(e) => handleChange('sync_analysis_results', e.target.checked)}
                    disabled={!syncSettings.enabled}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-slate-300">Sync analysis results</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={syncSettings.sync_settings}
                    onChange={(e) => handleChange('sync_settings', e.target.checked)}
                    disabled={!syncSettings.enabled}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-slate-300">Sync user settings</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={syncSettings.auto_backup}
                    onChange={(e) => handleChange('auto_backup', e.target.checked)}
                    disabled={!syncSettings.enabled}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-slate-300">Auto backup</span>
                </label>
              </div>
            </div>
          </div>

          {/* Manual Sync Button */}
          <div className="flex justify-between items-center pt-6">
            <button
              type="button"
              onClick={handleManualSync}
              disabled={syncing || !syncSettings.enabled}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:bg-slate-700 disabled:opacity-50 text-white transition-colors"
            >
              {syncing ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <RotateCw className="w-4 h-4" />
                  Sync Now
                </>
              )}
            </button>

            <div className="flex gap-4">
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
          </div>
        </form>
      </div>
    </div>
  );
}
