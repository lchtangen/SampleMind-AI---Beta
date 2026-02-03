'use client';

import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { AudioCollection, useCollections } from '@/hooks/useCollections';
import { ArrowLeft, MoreVertical, Play, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation'; // Correct import for App Router
import { useEffect, useState } from 'react';

export default function CollectionDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { user } = useAuthContext();
  const { getCollection, getCollectionItems, deleteCollection, loading } = useCollections();

  const [collection, setCollection] = useState<AudioCollection | null>(null);
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    if (params.id) {
      loadData(params.id);
    }
  }, [params.id]);

  const loadData = async (id: string) => {
    const colResult = await getCollection(id);
    if (colResult.success) {
      setCollection(colResult.data);
    }

    const itemsResult = await getCollectionItems(id);
    if (itemsResult.success) {
      setItems(itemsResult.data);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this collection?')) return;

    const result = await deleteCollection(params.id);
    if (result.success) {
      router.push('/collections');
    }
  };

  if (loading || !collection) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading collection..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md bg-black/20">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
            <Link href="/collections" className="text-white/50 hover:text-white transition">
                <ArrowLeft size={24} />
            </Link>
            <h1 className="text-xl font-bold">Collection Details</h1>
        </div>
      </header>

      <main className="container mx-auto px-6 py-10">
        <div className="bg-white/5 border border-white/10 rounded-xl p-8 mb-8 relative">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-4xl font-bold mb-2">{collection.name}</h2>
                    <p className="text-white/60 text-lg mb-4">{collection.description || 'No description provided.'}</p>

                    <div className="flex gap-4 text-sm text-white/40">
                        <span>{items.length} tracks</span>
                        <span>•</span>
                        <span>Created {new Date(collection.created_at).toLocaleDateString()}</span>
                        {collection.is_public && (
                             <>
                                <span>•</span>
                                <span className="text-green-400">Public</span>
                             </>
                        )}
                    </div>
                     <div className="mt-4 flex gap-2">
                        {collection.tags.map(tag => (
                            <span key={tag} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full border border-blue-500/20">
                                #{tag}
                            </span>
                        ))}
                    </div>
                </div>

                <button
                    onClick={handleDelete}
                    className="p-2 hover:bg-red-500/20 text-white/50 hover:text-red-500 rounded-lg transition"
                    title="Delete Collection"
                >
                    <Trash2 size={20} />
                </button>
            </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/10 bg-white/5 flex gap-4 text-sm text-white/50 font-medium uppercase tracking-wider">
                <div className="w-12 text-center">#</div>
                <div className="flex-1">Title</div>
                <div className="w-32">Format</div>
                <div className="w-32 text-right">Duration</div>
                <div className="w-12"></div>
            </div>

            <div className="divide-y divide-white/5">
                {items.length === 0 ? (
                    <div className="p-8 text-center text-white/30">
                        No audio files in this collection yet.
                    </div>
                ) : (
                    items.map((item, index) => (
                        <div key={item.id} className="p-4 flex gap-4 items-center hover:bg-white/5 transition group">
                            <div className="w-12 text-center text-white/30 group-hover:text-white transition">
                                <button className="hidden group-hover:inline-block text-blue-400">
                                    <Play size={16} fill="currentColor" />
                                </button>
                                <span className="group-hover:hidden">{index + 1}</span>
                            </div>
                            <div className="flex-1 font-medium">{item.filename}</div>
                            <div className="w-32 text-white/50 uppercase text-xs">{item.format}</div>
                            <div className="w-32 text-right text-white/50 font-mono text-sm">{item.duration}s</div>
                            <div className="w-12 text-right text-white/30 hover:text-white cursor-pointer">
                                <MoreVertical size={16} />
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
      </main>
    </div>
  );
}
