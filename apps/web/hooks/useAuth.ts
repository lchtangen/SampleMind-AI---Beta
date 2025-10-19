/**
 * Authentication hook for user management
 */

import { useState, useEffect, useCallback } from 'react';
import { AuthAPI, TokenManager } from '@/lib/api-client';

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
    isAuthenticated: false,
  });

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = TokenManager.getAccessToken();
    
    if (!token) {
      setState({
        user: null,
        loading: false,
        error: null,
        isAuthenticated: false,
      });
      return;
    }

    try {
      const user = await AuthAPI.getCurrentUser();
      setState({
        user,
        loading: false,
        error: null,
        isAuthenticated: true,
      });
    } catch (error) {
      // Token might be expired, try refresh
      try {
        await AuthAPI.refreshToken();
        const user = await AuthAPI.getCurrentUser();
        setState({
          user,
          loading: false,
          error: null,
          isAuthenticated: true,
        });
      } catch (refreshError) {
        // Refresh failed, clear tokens
        TokenManager.clearTokens();
        setState({
          user: null,
          loading: false,
          error: null,
          isAuthenticated: false,
        });
      }
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await AuthAPI.login(email, password);
      const user = await AuthAPI.getCurrentUser();
      
      setState({
        user,
        loading: false,
        error: null,
        isAuthenticated: true,
      });
      
      return { success: true, user };
    } catch (error: any) {
      const errorMessage = error.message || 'Login failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        isAuthenticated: false,
      }));
      
      return { success: false, error: errorMessage };
    }
  }, []);

  const register = useCallback(async (
    email: string,
    password: string,
    fullName?: string
  ) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      await AuthAPI.register(email, password, fullName);
      
      // Auto-login after registration
      const loginResult = await login(email, password);
      return loginResult;
    } catch (error: any) {
      const errorMessage = error.message || 'Registration failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      
      return { success: false, error: errorMessage };
    }
  }, [login]);

  const logout = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      await AuthAPI.logout();
    } catch (error) {
      // Ignore logout errors
    } finally {
      setState({
        user: null,
        loading: false,
        error: null,
        isAuthenticated: false,
      });
    }
  }, []);

  const refreshAuth = useCallback(async () => {
    await checkAuth();
  }, []);

  return {
    ...state,
    login,
    register,
    logout,
    refreshAuth,
  };
}
