"use client";

/**
 * QueryProvider — Wraps the app with TanStack Query v5 QueryClient. (P2-007)
 *
 * Usage: wrap in RootLayout (layout.tsx) around children.
 *
 * Default config:
 *   - staleTime: 30s  (most data stays fresh for 30s before refetch)
 *   - gcTime: 5min    (unused cache cleared after 5 min)
 *   - retry: 1        (one retry on failure, not 3)
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState, type ReactNode } from "react";

interface QueryProviderProps {
  children: ReactNode;
}

export default function QueryProvider({ children }: QueryProviderProps) {
  // Create QueryClient inside useState so each component tree gets its own
  // instance (avoids sharing state between server/client renders).
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,           // 30 seconds
            gcTime: 5 * 60_000,          // 5 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
