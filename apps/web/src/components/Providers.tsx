/**
 * @fileoverview Top-level context provider composition for SampleMind AI.
 *
 * Wraps the application's client-side context providers in a single component
 * for cleaner usage in layouts and pages.
 *
 * **Provider hierarchy (outermost → innermost):**
 * 1. {@link ErrorBoundary} — catches render-phase errors before they propagate.
 * 2. {@link NotificationProvider} — in-app notification state and dispatch.
 * 3. {@link AuthProvider} — Supabase authentication state (user, session, JWT).
 *
 * > **Note:** This is separate from the root layout's providers
 * > (`QueryProvider`, `AnalyticsProvider`, `ThemeProvider`) which are
 * > rendered in `app/layout.tsx`.
 *
 * @module components/Providers
 */

'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import ErrorBoundary from '@/components/ErrorBoundary';

/**
 * Composite provider wrapper that nests ErrorBoundary, NotificationProvider,
 * and AuthProvider around its children.
 *
 * @param props.children - The React subtree to wrap with providers.
 * @returns The nested provider tree.
 */
export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </NotificationProvider>
    </ErrorBoundary>
  );
}
