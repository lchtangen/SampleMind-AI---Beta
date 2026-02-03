/**
 * Tests for AuthContext
 * Tests authentication state management
 */

import React, { useContext } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthContext } from '@/contexts/AuthContext';

// Mock component that uses AuthContext
const AuthConsumer = () => {
  const { user, loading, error, login, logout } = useContext(AuthContext);

  return (
    <div>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      {user && <div>User: {user.email}</div>}
      {!user && <div>Not authenticated</div>}
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  test('provides initial unauthenticated state', () => {
    render(
      <AuthContext.Provider value={{ user: null, loading: false, error: null, login: jest.fn(), logout: jest.fn() }}>
        <AuthConsumer />
      </AuthContext.Provider>
    );
    expect(screen.getByText('Not authenticated')).toBeInTheDocument();
  });

  test('provides authenticated state with user', () => {
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };
    render(
      <AuthContext.Provider
        value={{ user: mockUser, loading: false, error: null, login: jest.fn(), logout: jest.fn() }}
      >
        <AuthConsumer />
      </AuthContext.Provider>
    );
    expect(screen.getByText('User: test@example.com')).toBeInTheDocument();
  });

  test('shows loading state', () => {
    render(
      <AuthContext.Provider value={{ user: null, loading: true, error: null, login: jest.fn(), logout: jest.fn() }}>
        <AuthConsumer />
      </AuthContext.Provider>
    );
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('displays error message', () => {
    render(
      <AuthContext.Provider
        value={{ user: null, loading: false, error: 'Invalid credentials', login: jest.fn(), logout: jest.fn() }}
      >
        <AuthConsumer />
      </AuthContext.Provider>
    );
    expect(screen.getByText('Error: Invalid credentials')).toBeInTheDocument();
  });

  test('login button is clickable', () => {
    const mockLogin = jest.fn();
    render(
      <AuthContext.Provider value={{ user: null, loading: false, error: null, login: mockLogin, logout: jest.fn() }}>
        <AuthConsumer />
      </AuthContext.Provider>
    );
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password');
  });

  test('logout button is clickable', () => {
    const mockLogout = jest.fn();
    const mockUser = { id: '1', email: 'test@example.com' };
    render(
      <AuthContext.Provider value={{ user: mockUser, loading: false, error: null, login: jest.fn(), logout: mockLogout }}>
        <AuthConsumer />
      </AuthContext.Provider>
    );
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(mockLogout).toHaveBeenCalled();
  });
});
