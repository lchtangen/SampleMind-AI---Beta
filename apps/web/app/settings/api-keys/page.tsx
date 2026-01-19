'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Plus,
  Copy,
  Trash2,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import Link from 'next/link';
import { useAuthContext } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/LoadingSpinner';

interface APIKey {
  key_id: string;
  name: string;
  provider: string;
  permissions: string[];
  created_at: string;
  last_used?: string;
  is_active: boolean;
}

interface CreateAPIKeyData {
  name: string;
  provider: string;
  permissions: string[];
}

export default function APIKeysPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newSecret, setNewSecret] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [showSecret, setShowSecret] = useState(false);

  const [formData, setFormData] = useState<CreateAPIKeyData>({
    name: '',
    provider: 'custom',
    permissions: ['read'],
  });

  // Load API keys
  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    const fetchAPIKeys = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/settings/api-keys', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load API keys');
        }

        const data = await response.json();
        setApiKeys(data.keys || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load API keys');
      } finally {
        setLoading(false);
      }
    };

    fetchAPIKeys();
  }, [user, router]);

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError(null);
    setNewSecret(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/settings/api-keys', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create API key');
      }

      const data = await response.json();
      setNewSecret(data.secret);
      setFormData({ name: '', provider: 'custom', permissions: ['read'] });
      setShowCreateForm(false);

      // Reload API keys
      const keysResponse = await fetch('/api/v1/settings/api-keys', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const keysData = await keysResponse.json();
      setApiKeys(keysData.keys || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create API key');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    setDeleting(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/settings/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete API key');
      }

      setApiKeys(apiKeys.filter(key => key.key_id !== keyId));
      setDeleteConfirm(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete API key');
    } finally {
      setDeleting(false);
    }
  };

  const copyToClipboard = () => {
    if (newSecret) {
      navigator.clipboard.writeText(newSecret);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <Link href="/settings">
              <button className="flex items-center text-slate-400 hover:text-slate-200 transition-colors">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back
              </button>
            </Link>
            <h1 className="text-3xl font-bold text-white ml-4">API Keys</h1>
          </div>
          {!showCreateForm && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Key
            </button>
          )}
        </div>

        {/* New Secret Display */}
        {newSecret && (
          <div className="mb-8 p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-300 mb-2">API Key Created Successfully!</h3>
                <p className="text-sm text-green-200 mb-3">
                  Copy this key now. You won't be able to see it again.
                </p>
                <div className="flex items-center gap-2 bg-slate-900/50 rounded p-3 font-mono text-sm text-slate-300">
                  {showSecret ? newSecret : '•'.repeat(32)}
                  <button
                    onClick={() => setShowSecret(!showSecret)}
                    className="ml-2 text-slate-400 hover:text-slate-200"
                  >
                    {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={copyToClipboard}
                    className="ml-auto text-slate-400 hover:text-slate-200"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
                {copied && <p className="text-xs text-green-300 mt-2">Copied to clipboard!</p>}
              </div>
            </div>
          </div>
        )}

        {/* Create Form */}
        {showCreateForm && (
          <div className="mb-8 p-6 rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50">
            <h2 className="text-lg font-semibold text-white mb-4">Create New API Key</h2>

            {error && (
              <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <form onSubmit={handleCreateKey} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Key Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
                  placeholder="e.g., Production API Key"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Provider
                </label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                >
                  <option value="custom">Custom</option>
                  <option value="plugin">Plugin</option>
                  <option value="integration">Integration</option>
                </select>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white transition-colors"
                >
                  {creating ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Key'
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* API Keys List */}
        <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 overflow-hidden">
          {apiKeys.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-slate-400">No API keys yet. Create one to get started.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-slate-700 bg-slate-900/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                      Provider
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {apiKeys.map((key) => (
                    <tr key={key.key_id} className="hover:bg-slate-700/20 transition-colors">
                      <td className="px-6 py-4 text-sm text-white">{key.name}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{key.provider}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {new Date(key.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                          key.is_active
                            ? 'bg-green-500/10 text-green-300'
                            : 'bg-slate-500/10 text-slate-400'
                        }`}>
                          {key.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-right">
                        {deleteConfirm === key.key_id ? (
                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => setDeleteConfirm(null)}
                              className="text-slate-400 hover:text-slate-200"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleDeleteKey(key.key_id)}
                              disabled={deleting}
                              className="text-red-400 hover:text-red-300 disabled:opacity-50"
                            >
                              {deleting ? 'Deleting...' : 'Confirm'}
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setDeleteConfirm(key.key_id)}
                            className="text-slate-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Warning */}
        <div className="mt-8 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-200">
              Keep your API keys secret! Treat them like passwords. Don't share them in public repositories or emails.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
