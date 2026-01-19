/**
 * useSync Hook
 * React hook for cloud sync integration
 */

import { useEffect, useState, useCallback } from 'react';
import { initSyncClient, getSyncClient, SyncStatus, SyncEvent } from '@/lib/sync/syncClient';
import { useAuthContext } from '@/contexts/AuthContext';

export interface UseSyncOptions {
  autoInit?: boolean;
  autoSync?: boolean;
  syncInterval?: number;
  persistQueue?: boolean;
}

const DEFAULT_SYNC_INTERVAL = 60 * 1000; // 60 seconds

export function useSync(options: UseSyncOptions = {}) {
  const { user } = useAuthContext();
  const [status, setStatus] = useState<SyncStatus>({
    enabled: false,
    syncing: false,
    pendingEvents: 0,
  });
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize sync client
  useEffect(() => {
    if (!options.autoInit || !user) return;

    const initializeSync = async () => {
      try {
        const syncClient = await initSyncClient({
          userId: user.user_id || user.id || 'unknown',
          apiUrl: process.env.NEXT_PUBLIC_API_URL || '/api/v1',
          syncInterval: options.syncInterval || DEFAULT_SYNC_INTERVAL,
          autoSync: options.autoSync !== false,
          persistQueue: options.persistQueue !== false,
        });

        // Subscribe to status changes
        const unsubscribe = syncClient.subscribe((newStatus) => {
          setStatus(newStatus);
          if (newStatus.error) {
            setError(newStatus.error);
          }
        });

        setIsInitialized(true);
        setError(null);

        return () => {
          unsubscribe();
        };
      } catch (err) {
        console.error('Failed to initialize sync:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize sync');
        setIsInitialized(false);
      }
    };

    const cleanup = initializeSync();
    return () => {
      cleanup.then(fn => fn?.());
    };
  }, [user, options.autoInit, options.syncInterval, options.autoSync, options.persistQueue]);

  // Queue an event
  const queueEvent = useCallback(
    (event: Omit<SyncEvent, 'eventId' | 'timestamp' | 'deviceId'>) => {
      try {
        const syncClient = getSyncClient();
        syncClient.queueEvent(event);
      } catch (err) {
        console.error('Failed to queue event:', err);
        setError(err instanceof Error ? err.message : 'Failed to queue event');
      }
    },
    []
  );

  // Enable sync
  const enableSync = useCallback(async () => {
    try {
      const syncClient = getSyncClient();
      await syncClient.enable();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to enable sync';
      setError(message);
      throw err;
    }
  }, []);

  // Disable sync
  const disableSync = useCallback(async () => {
    try {
      const syncClient = getSyncClient();
      await syncClient.disable();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to disable sync';
      setError(message);
      throw err;
    }
  }, []);

  // Manual sync
  const syncNow = useCallback(async () => {
    try {
      const syncClient = getSyncClient();
      await syncClient.sync();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sync failed';
      setError(message);
      throw err;
    }
  }, []);

  // Get pending count
  const getPendingCount = useCallback(() => {
    try {
      const syncClient = getSyncClient();
      return syncClient.getPendingCount();
    } catch {
      return 0;
    }
  }, []);

  // Clear queue
  const clearQueue = useCallback(() => {
    try {
      const syncClient = getSyncClient();
      syncClient.clearQueue();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to clear queue';
      setError(message);
    }
  }, []);

  return {
    // Status
    status,
    isInitialized,
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    error,

    // Actions
    queueEvent,
    enableSync,
    disableSync,
    syncNow,
    getPendingCount,
    clearQueue,

    // Convenience flags
    isSyncing: status.syncing,
    isSyncEnabled: status.enabled,
    pendingCount: status.pendingEvents,
  };
}

export default useSync;
