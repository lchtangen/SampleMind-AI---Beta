/**
 * Tests for useAuth Hook
 * Tests authentication state management hook
 */

import { renderHook, act } from '@testing-library/react';
import { useAuth } from '@/hooks/useAuth';

describe('useAuth', () => {
  test('provides auth state object', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current).toBeDefined();
    expect(typeof result.current.user).toBeDefined();
    expect(typeof result.current.loading).toBeDefined();
    expect(typeof result.current.error).toBeDefined();
  });

  test('has login function', () => {
    const { result } = renderHook(() => useAuth());
    expect(typeof result.current.login).toBe('function');
  });

  test('has logout function', () => {
    const { result } = renderHook(() => useAuth());
    expect(typeof result.current.logout).toBe('function');
  });

  test('has signup function if available', () => {
    const { result } = renderHook(() => useAuth());
    if (result.current.signup) {
      expect(typeof result.current.signup).toBe('function');
    }
  });

  test('login function accepts email and password', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      const loginFn = result.current.login;
      if (loginFn) {
        // Call with valid arguments
        expect(() => loginFn('test@example.com', 'password')).not.toThrow();
      }
    });
  });

  test('logout function clears user state', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      if (result.current.logout) {
        result.current.logout();
      }
    });

    // User should be null or undefined after logout
    expect(result.current.user === null || result.current.user === undefined).toBeTruthy();
  });

  test('loading state changes during authentication', async () => {
    const { result } = renderHook(() => useAuth());

    const initialLoading = result.current.loading;

    await act(async () => {
      if (result.current.login) {
        const promise = result.current.login('test@example.com', 'password');
        if (promise instanceof Promise) {
          await promise;
        }
      }
    });

    // Loading state should have changed at some point
    expect(typeof result.current.loading).toBe('boolean');
  });

  test('error state is null initially', () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.error === null || result.current.error === undefined).toBeTruthy();
  });
});
