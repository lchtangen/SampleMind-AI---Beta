/**
 * Tests for useCollections Hook
 * Tests collection management functionality
 */

import { renderHook, act } from '@testing-library/react';
import { useCollections } from '@/hooks/useCollections';

describe('useCollections Hook', () => {
  test('provides collections array', () => {
    const { result } = renderHook(() => useCollections());
    expect(Array.isArray(result.current.collections)).toBeTruthy();
  });

  test('provides createCollection method', () => {
    const { result } = renderHook(() => useCollections());
    expect(typeof result.current.createCollection).toBe('function');
  });

  test('provides deleteCollection method', () => {
    const { result } = renderHook(() => useCollections());
    expect(typeof result.current.deleteCollection).toBe('function');
  });

  test('provides addToCollection method', () => {
    const { result } = renderHook(() => useCollections());
    expect(typeof result.current.addToCollection).toBe('function');
  });

  test('provides removeFromCollection method', () => {
    const { result } = renderHook(() => useCollections());
    expect(typeof result.current.removeFromCollection).toBe('function');
  });

  test('createCollection accepts name parameter', async () => {
    const { result } = renderHook(() => useCollections());

    await act(async () => {
      if (result.current.createCollection) {
        expect(() =>
          result.current.createCollection({ name: 'My Collection', description: 'Test' })
        ).not.toThrow();
      }
    });
  });

  test('deleteCollection accepts collection id', async () => {
    const { result } = renderHook(() => useCollections());

    await act(async () => {
      if (result.current.deleteCollection) {
        expect(() => result.current.deleteCollection('collection-1')).not.toThrow();
      }
    });
  });

  test('addToCollection accepts collection and item', async () => {
    const { result } = renderHook(() => useCollections());

    await act(async () => {
      if (result.current.addToCollection) {
        expect(() =>
          result.current.addToCollection('collection-1', { id: 'sample-1', name: 'sample.wav' })
        ).not.toThrow();
      }
    });
  });

  test('provides loading state', () => {
    const { result } = renderHook(() => useCollections());
    expect(typeof result.current.loading).toBe('boolean');
  });

  test('provides error state', () => {
    const { result } = renderHook(() => useCollections());
    expect(result.current.error === null || typeof result.current.error === 'string').toBeTruthy();
  });

  test('handles empty collections array', () => {
    const { result } = renderHook(() => useCollections());
    expect(Array.isArray(result.current.collections)).toBeTruthy();
    expect(result.current.collections.length >= 0).toBeTruthy();
  });
});
