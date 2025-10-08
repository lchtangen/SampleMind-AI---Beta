/**
 * CyberpunkModal Component
 *
 * A cyberpunk-themed modal dialog with backdrop blur, neon borders,
 * and smooth Framer Motion animations. Fully accessible with focus management.
 *
 * @module CyberpunkModal
 */

import React, { useEffect, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NeonButton } from '../../atoms/NeonButton/NeonButton';
import { NeonDivider } from '../../atoms/NeonDivider/NeonDivider';

/**
 * Modal size variants
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

/**
 * Props for the CyberpunkModal component
 */
export interface CyberpunkModalProps {
  /**
   * Whether the modal is open
   */
  isOpen: boolean;

  /**
   * Close handler function
   */
  onClose: () => void;

  /**
   * Modal title
   */
  title: string;

  /**
   * Modal content
   */
  children: ReactNode;

  /**
   * Footer content (typically action buttons)
   */
  footer?: ReactNode;

  /**
   * Modal size
   */
  size?: ModalSize;

  /**
   * Close modal on backdrop click
   */
  closeOnBackdropClick?: boolean;

  /**
   * Close modal on ESC key
   */
  closeOnEsc?: boolean;

  /**
   * Show close button
   */
  showCloseButton?: boolean;

  /**
   * Additional CSS classes for modal content
   */
  className?: string;

  /**
   * Test ID
   */
  testId?: string;
}

/**
 * Get size-specific styles
 */
const getSizeStyles = (size: ModalSize): string => {
  const styles = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[90vw] max-h-[90vh]',
  };

  return styles[size];
};

/**
 * CyberpunkModal - Modal dialog with cyberpunk styling.
 *
 * @example
 * ```tsx
 * <CyberpunkModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   title="Confirm Action"
 *   footer={
 *     <>
 *       <NeonButton variant="ghost" onClick={onClose}>Cancel</NeonButton>
 *       <NeonButton variant="primary" onClick={onConfirm}>Confirm</NeonButton>
 *     </>
 *   }
 * >
 *   <p>Are you sure you want to proceed?</p>
 * </CyberpunkModal>
 * ```
 */
export const CyberpunkModal: React.FC<CyberpunkModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnBackdropClick = true,
  closeOnEsc = true,
  showCloseButton = true,
  className = '',
  testId,
}) => {
  /**
   * Handle ESC key press
   */
  useEffect(() => {
    if (!isOpen || !closeOnEsc) return;

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, closeOnEsc, onClose]);

  /**
   * Prevent body scroll when modal is open
   */
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  /**
   * Handle backdrop click
   */
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={handleBackdropClick}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          data-testid={testId}
        >
          {/* Backdrop with blur */}
          <motion.div
            className="absolute inset-0 bg-black/50 backdrop-blur-md"
            initial={{ backdropFilter: 'blur(0px)' }}
            animate={{ backdropFilter: 'blur(12px)' }}
            exit={{ backdropFilter: 'blur(0px)' }}
            aria-hidden="true"
          />

          {/* Modal Content */}
          <motion.div
            className={`
              relative
              w-full
              ${getSizeStyles(size)}
              backdrop-blur-xl
              bg-white/5
              border-2
              border-primary/50
              rounded-xl
              shadow-[0_0_40px_rgba(139,92,246,0.6),0_0_80px_rgba(139,92,246,0.3)]
              overflow-hidden
              ${className}
            `.trim().replace(/\s+/g, ' ')}
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 30,
            }}
          >
            {/* Modal Header */}
            <div className="p-6 md:p-8">
              <div className="flex items-start justify-between gap-4">
                <h2
                  id="modal-title"
                  className="text-2xl md:text-3xl font-bold text-text-primary"
                >
                  {title}
                </h2>

                {/* Close Button */}
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="
                      flex-shrink-0
                      p-2
                      rounded-lg
                      text-text-secondary
                      hover:text-text-primary
                      hover:bg-white/10
                      transition-all
                      duration-normal
                      focus:outline-none
                      focus:ring-2
                      focus:ring-primary
                    "
                    aria-label="Close modal"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                )}
              </div>
            </div>

            <NeonDivider gradient="cyber" animated />

            {/* Modal Body */}
            <div className="p-6 md:p-8 text-text-secondary">
              {children}
            </div>

            {/* Modal Footer */}
            {footer && (
              <>
                <NeonDivider gradient="purple" animated />
                <div className="p-6 md:p-8 flex items-center justify-end gap-4 bg-white/5">
                  {footer}
                </div>
              </>
            )}

            {/* Glow Overlay */}
            <div
              className="
                absolute
                inset-0
                bg-gradient-glow
                opacity-20
                pointer-events-none
              "
              aria-hidden="true"
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

CyberpunkModal.displayName = 'CyberpunkModal';

export default CyberpunkModal;
