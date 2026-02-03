'use client';

import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { AudioCollection, useCollections } from '@/hooks/useCollections';
import { Folder, Layers, Plus } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function CollectionsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuthContext();
  const { listCollections, createCollection, loading: collectionsLoading } = useCollections();

  const [collections, setCollections] = useState<AudioCollection[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [newColName, setNewColName] = useState('');

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    const result = await listCollections();
    if (result.success && result.data) {
      setCollections(result.data);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColName.trim()) return;

    const result = await createCollection({ name: newColName });
    if (result.success) {
      setNewColName('');
      setIsCreating(false);
      loadCollections();
    }
  };

  if (authLoading || collectionsLoading) {
     return (
       <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
         <LoadingSpinner size="lg" text="Loading collections..." />
       </div>
     );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md bg-black/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                SampleMind AI
              </h1>
            </Link>

            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Dashboard
              </Link>
              <Link href="/upload" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Upload
              </Link>
              <Link href="/library" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Library
              </Link>
              <Link href="/collections" className="text-[hsl(220,90%,60%)] font-medium">
                Collections
              </Link>
            </nav>

            <div className="flex items-center space-x-4">
                {user ? (
                    <div className="h-8 w-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-xs flex items-center justify-center font-bold">
                        {user.username?.substring(0, 2).toUpperCase()}
                    </div>
                ) : (
                    <Link href="/login" className="text-sm border border-white/20 px-4 py-2 rounded-full hover:bg-white/10 transition">
                        Sign In
                    </Link>
                )}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold flex items-center gap-3">
                <Layers className="text-blue-500" />
                Your Collections
            </h2>
            <button
                onClick={() => setIsCreating(!isCreating)}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition"
            >
                <Plus size={18} />
                New Collection
            </button>
        </div>

        {isCreating && (
            <div className="mb-8 bg-white/5 p-6 rounded-xl border border-white/10 max-w-lg">
                <form onSubmit={handleCreate} className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Collection Name"
                        value={newColName}
                        onChange={(e) => setNewColName(e.target.value)}
                        className="flex-1 bg-black/20 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition"
                    />
                    <button type="submit" className="bg-green-600 hover:bg-green-500 text-white px-6 py-2 rounded-lg font-medium">
                        Create
                    </button>
                </form>
            </div>
        )}

        {collections.length === 0 ? (
             <div className="text-center py-20 bg-white/5 rounded-2xl border border-white/10 border-dashed">
                <Folder className="mx-auto h-16 w-16 text-white/20 mb-4" />
                <h3 className="text-xl font-medium text-white/50">No collections found</h3>
                <p className="text-white/30 mt-2">Create your first collection to organize your samples.</p>
             </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {collections.map(col => (
                    <Link href={`/collections/${col.id}`} key={col.id} className="group">
                        <div className="bg-white/5 border border-white/10 p-6 rounded-xl hover:bg-white/10 hover:border-blue-500/50 transition duration-300 h-full flex flex-col">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-3 bg-blue-500/20 rounded-lg text-blue-400">
                                    <Folder size={24} />
                                </div>
                                {col.is_public && (
                                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full border border-green-500/20">
                                        Public
                                    </span>
                                )}
                            </div>

                            <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition">{col.name}</h3>
                            <p className="text-white/50 text-sm mb-4 line-clamp-2 flex-grow">{col.description || 'No description'}</p>

                            <div className="flex items-center justify-between text-xs text-white/40 pt-4 border-t border-white/5">
                                <span>{col.file_count} items</span>
                                <span>{new Date(col.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        )}
      </main>
    </div>
  );
}
