'use client';

import React, { useEffect } from 'react';
import { getAnalytics } from '@/lib/analytics';

interface AnalyticsProviderProps {
  children: React.ReactNode;
}

/**
 * Analytics provider component
 * Initializes PostHog analytics and provides context to the app
 */
export function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  useEffect(() => {
    // Initialize analytics on mount
    const analytics = getAnalytics();

    // Set up user identification if user data is available
    try {
      const userId = localStorage.getItem('user_id');
      if (userId && analytics.isEnabled()) {
        analytics.identify(userId, {
          timestamp: new Date().toISOString(),
          source: 'web_app',
        });
      }
    } catch (error) {
      console.debug('Error setting up user identification:', error);
    }
  }, []);

  return <>{children}</>;
}
