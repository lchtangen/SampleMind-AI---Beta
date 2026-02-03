/**
 * Jest Setup File
 * Configure test environment, mocks, and utilities
 */

import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
    back: jest.fn(),
    prefetch: jest.fn(),
    replace: jest.fn(),
  }),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

// Mock next-themes
jest.mock('next-themes', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
  useTheme: () => ({
    theme: 'dark',
    setTheme: jest.fn(),
    themes: ['light', 'dark'],
    systemTheme: 'dark',
    resolvedTheme: 'dark',
  }),
}));

// Mock WebSocket
class MockWebSocket {
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
  send = jest.fn();
  close = jest.fn();
  OPEN = 1;
  CLOSED = 3;
  readyState = 1;
}

(global as any).WebSocket = MockWebSocket;

// Mock axios
jest.mock('axios', () => ({
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    create: jest.fn(() => ({
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
      patch: jest.fn(),
    })),
  },
}));

// Suppress console errors in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
        args[0].includes('Not implemented: HTMLFormElement.prototype.submit'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
