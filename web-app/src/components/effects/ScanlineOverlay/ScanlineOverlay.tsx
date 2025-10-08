import React from 'react';
import { motion } from 'framer-motion';

export interface ScanlineOverlayProps {
  /**
   * Enable/disable the scanline effect
   * @default true
   */
  enabled?: boolean;
  
  /**
   * Animation speed in seconds
   * @default 8
   */
  speed?: number;
  
  /**
   * Opacity of the scanline
   * @default 0.8
   */
  opacity?: number;
  
  /**
   * Color of the scanline (supports hex, rgb, rgba)
   * @default '#8B5CF6'
   */
  color?: string;
  
  /**
   * Blur amount in pixels
   * @default 10
   */
  blur?: number;
}

/**
 * ScanlineOverlay Component
 * 
 * Creates a retro-futuristic scanline effect that moves across the screen.
 * Commonly used in cyberpunk interfaces for aesthetic enhancement.
 * Respects prefers-reduced-motion setting.
 * 
 * @example
 * ```tsx
 * <ScanlineOverlay enabled={true} speed={8} color="#8B5CF6" />
 * ```
 */
export const ScanlineOverlay: React.FC<ScanlineOverlayProps> = ({
  enabled = true,
  speed = 8,
  opacity = 0.8,
  color = '#8B5CF6',
  blur = 10,
}) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  if (!enabled || prefersReducedMotion) return null;

  return (
    <div
      className="scanline-overlay"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 9999,
        overflow: 'hidden',
      }}
      aria-hidden="true"
    >
      <motion.div
        style={{
          position: 'absolute',
          width: '100%',
          height: '2px',
          background: `linear-gradient(90deg, transparent 0%, ${color} 50%, transparent 100%)`,
          boxShadow: `0 0 ${blur}px ${color}`,
          opacity,
        }}
        animate={{
          y: ['-100%', '100vh'],
        }}
        transition={{
          duration: speed,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  );
};

export default ScanlineOverlay;
