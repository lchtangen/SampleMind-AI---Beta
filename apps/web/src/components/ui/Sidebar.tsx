/**
 * GLASS SIDEBAR COMPONENT
 * Collapsible sidebar with slide animation
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { X, Menu } from 'lucide-react';
import { IconButton } from './IconButton';

interface SidebarProps {
  children: React.ReactNode;
  isOpen: boolean;
  onClose: () => void;
  side?: 'left' | 'right';
  width?: string;
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  children,
  isOpen,
  onClose,
  side = 'left',
  width = '256px',
  className,
}) => {
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-[1200]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sidebar */}
          <motion.div
            className={cn(
              'fixed top-0 bottom-0 z-[1300]',
              'glass-strong border-glass-border',
              side === 'left' ? 'left-0 border-r' : 'right-0 border-l',
              className
            )}
            style={{ width }}
            initial={{ x: side === 'left' ? '-100%' : '100%' }}
            animate={{ x: 0 }}
            exit={{ x: side === 'left' ? '-100%' : '100%' }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 30,
            }}
          >
            {/* Close button */}
            <div className={cn(
              'absolute top-4 z-10',
              side === 'left' ? 'right-4' : 'left-4'
            )}>
              <IconButton
                icon={<X className="w-5 h-5" />}
                onClick={onClose}
                aria-label="Close sidebar"
              />
            </div>

            {/* Content */}
            <div className="h-full overflow-y-auto p-6 pt-16">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

Sidebar.displayName = 'Sidebar';

// Sidebar Toggle Button
interface SidebarToggleProps {
  onClick: () => void;
  className?: string;
  'aria-label'?: string;
}

export const SidebarToggle: React.FC<SidebarToggleProps> = ({
  onClick,
  className,
  'aria-label': ariaLabel = 'Toggle sidebar',
}) => {
  return (
    <IconButton
      icon={<Menu className="w-5 h-5" />}
      onClick={onClick}
      aria-label={ariaLabel}
      className={className}
    />
  );
};

SidebarToggle.displayName = 'SidebarToggle';
