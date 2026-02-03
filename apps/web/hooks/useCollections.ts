import { useCallback, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const ENDPOINT = `${API_URL}/api/v1/collections`;

export interface AudioCollection {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  is_public: boolean;
  tags: string[];
  file_count: number;
  total_duration: number;
  created_at: string;
  updated_at: string;
}

export function useCollections() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listCollections = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(ENDPOINT);
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const data = await res.json();
      setLoading(false);
      return { success: true, data };
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  }, []);

  const createCollection = useCallback(async (collectionData: { name: string; description?: string; is_public?: boolean; tags?: string[] }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(collectionData),
      });
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const data = await res.json();
      setLoading(false);
      return { success: true, data };
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  }, []);

  const getCollection = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${ENDPOINT}/${id}`);
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const data = await res.json();
      setLoading(false);
      return { success: true, data };
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  }, []);

  const deleteCollection = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${ENDPOINT}/${id}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      setLoading(false);
      return { success: true };
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  }, []);

  const getCollectionItems = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${ENDPOINT}/${id}/items`);
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const data = await res.json();
      setLoading(false);
      return { success: true, data };
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  }, []);

  return { listCollections, createCollection, getCollection, deleteCollection, getCollectionItems, loading, error };
}
