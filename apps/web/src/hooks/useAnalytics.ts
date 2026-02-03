/**
 * React hook for PostHog analytics integration
 */

import { useCallback, useEffect } from "react";
import { analytics, EventType } from "@/lib/analytics";

/**
 * Custom hook for tracking analytics events
 */
export function useAnalytics() {
  // Initialize analytics on mount
  useEffect(() => {
    // Analytics is initialized globally, but we can set up
    // any user-specific tracking here
  }, []);

  /**
   * Track audio upload
   */
  const trackUpload = useCallback(
    (fileSize: number, duration: number, format: string, metadata?: Record<string, any>) => {
      analytics.trackAudioUpload(fileSize, duration, format, metadata);
    },
    []
  );

  /**
   * Track analysis
   */
  const trackAnalysis = useCallback(
    (
      level: string,
      durationMs: number,
      fileSize: number,
      success: boolean = true,
      error?: string,
      metadata?: Record<string, any>
    ) => {
      analytics.trackAnalysis(level, durationMs, fileSize, success, error, metadata);
    },
    []
  );

  /**
   * Track search
   */
  const trackSearch = useCallback(
    (
      type: "semantic" | "library" | "similar",
      resultCount: number,
      queryTimeMs: number,
      metadata?: Record<string, any>
    ) => {
      analytics.trackSearch(type, resultCount, queryTimeMs, metadata);
    },
    []
  );

  /**
   * Track feature usage
   */
  const trackFeature = useCallback((featureName: string, metadata?: Record<string, any>) => {
    analytics.trackFeature(featureName, metadata);
  }, []);

  /**
   * Track export
   */
  const trackExport = useCallback(
    (format: string, fileSize: number, metadata?: Record<string, any>) => {
      analytics.trackExport(format, fileSize, metadata);
    },
    []
  );

  /**
   * Track feedback
   */
  const trackFeedback = useCallback(
    (type: string, message: string, metadata?: Record<string, any>) => {
      analytics.trackFeedback(type, message, metadata);
    },
    []
  );

  /**
   * Identify user
   */
  const identifyUser = useCallback((userId: string, properties?: Record<string, any>) => {
    analytics.identify(userId, properties);
  }, []);

  /**
   * Set user properties
   */
  const setUserProperties = useCallback((properties: Record<string, any>) => {
    analytics.setUserProperties(properties);
  }, []);

  return {
    // Track specific actions
    trackUpload,
    trackAnalysis,
    trackSearch,
    trackFeature,
    trackExport,
    trackFeedback,
    trackOnboarding: () => analytics.trackFeature("onboarding"),

    // User identification
    identifyUser,
    setUserProperties,

    // Direct event capture
    capture: analytics.capture.bind(analytics),

    // Check if enabled
    isEnabled: analytics.isEnabled(),
  };
}

export default useAnalytics;
