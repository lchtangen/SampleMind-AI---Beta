import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface CyberpunkToastProps {
  /**
   * Toast message content
   */
  message: string;
  
  /**
   * Toast variant determines color scheme
   * @default 'info'
   */
  variant?: ToastVariant;
  
  /**
   * Show/hide the toast
   */
  isVisible: boolean;
  
  /**
   * Callback when toast should close
   */
  onClose?: () => void;
  
  /**
   * Auto-dismiss duration in milliseconds (0 = no auto-dismiss)
   * @default 5000
   */
  duration?: number;
  
  /**
   * Optional title
   */
  title?: string;
  
  /**
   * Optional icon component
   */
  icon?: React.ReactNode;
}

const variantStyles = {
  success: {
    border: 'border-green-500',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.5)]',
    text: 'text-green-400',
    bg: 'bg-green-500/10',
  },
  error: {
    border: 'border-red-500',
    glow: 'shadow-[0_0_20px_rgba(239,68,68,0.5)]',
    text: 'text-red-400',
    bg: 'bg-red-500/10',
  },
  warning: {
    border: 'border-yellow-500',
    glow: 'shadow-[0_0_20px_rgba(245,158,11,0.5)]',
    text: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
  },
  info: {
    border: 'border-primary',
    glow: 'neon-glow-purple',
    text: 'text-primary-light',
    bg: 'bg-primary/10',
  },
};

const icons = {
  success: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  error: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  warning: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  info: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

/**
 * CyberpunkToast Component
 * 
 * Notification toast with glassmorphism, neon borders, and cyberpunk styling.
 * Auto-dismisses after specified duration with smooth animations.
 * 
 * @example
 * ```tsx
 * <CyberpunkToast
 *   variant="success"
 *   message="Audio file processed successfully"
 *   isVisible={showToast}
 *   onClose={() => setShowToast(false)}
 * />
 * ```
 */
export const CyberpunkToast: React.FC<CyberpunkToastProps> = ({
  message,
  variant = 'info',
  isVisible,
  onClose,
  duration = 5000,
  title,
  icon,
}) => {
  const styles = variantStyles[variant];
  const defaultIcon = icons[variant];

  React.useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.3 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
          className={`
            fixed top-4 right-4 z-[1080]
            glass-card-heavy
            ${styles.border} ${styles.glow}
            border-2 rounded-xl p-4
            min-w-[320px] max-w-[480px]
            backdrop-blur-md
          `}
          role="alert"
          aria-live="polite"
        >
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div className={`flex-shrink-0 ${styles.text} ${styles.bg} p-2 rounded-lg`}>
              {icon || defaultIcon}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {title && (
                <h4 className={`font-heading font-bold ${styles.text} mb-1`}>
                  {title}
                </h4>
              )}
              <p className="text-text-secondary text-sm leading-relaxed">
                {message}
              </p>
            </div>

            {/* Close button */}
            {onClose && (
              <button
                onClick={onClose}
                className={`
                  flex-shrink-0 
                  ${styles.text} 
                  hover:${styles.bg} 
                  p-1 rounded 
                  transition-colors
                  focus:outline-none focus:ring-2 focus:ring-primary
                `}
                aria-label="Close notification"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Progress bar */}
          {duration > 0 && (
            <motion.div
              className={`mt-3 h-1 ${styles.bg} rounded-full overflow-hidden`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <motion.div
                className={`h-full ${styles.text.replace('text-', 'bg-')}`}
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: duration / 1000, ease: 'linear' }}
              />
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CyberpunkToast;
