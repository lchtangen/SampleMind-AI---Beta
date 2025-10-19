/**
 * TOAST NOTIFICATION COMPONENT
 * Neon toast notifications with auto-dismiss
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  description?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const iconMap = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const colorMap = {
  success: 'text-success border-success/30 shadow-[0_0_20px_hsl(145,85%,55%,0.3)]',
  error: 'text-error border-error/30 shadow-[0_0_20px_hsl(0,90%,60%,0.3)]',
  warning: 'text-warning border-warning/30 shadow-[0_0_20px_hsl(45,95%,60%,0.3)]',
  info: 'text-info border-info/30 shadow-[0_0_20px_hsl(210,90%,60%,0.3)]',
};

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  description,
  duration = 5000,
  onClose,
}) => {
  const Icon = iconMap[type];

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onClose(id), duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.95 }}
      className={cn(
        'glass-strong rounded-glass p-4 min-w-[320px] max-w-md',
        'border',
        colorMap[type]
      )}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
        
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-text-primary">{message}</p>
          {description && (
            <p className="text-sm text-text-secondary mt-1">{description}</p>
          )}
        </div>

        <button
          onClick={() => onClose(id)}
          className="flex-shrink-0 text-text-tertiary hover:text-text-primary transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Progress bar */}
      <motion.div
        className={cn('h-1 rounded-full mt-3', colorMap[type].split(' ')[0])}
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: duration / 1000, ease: 'linear' }}
      />
    </motion.div>
  );
};

// Toast Container
interface ToastContainerProps {
  toasts: Array<{
    id: string;
    type: ToastType;
    message: string;
    description?: string;
  }>;
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onClose }) => {
  return (
    <div className="fixed top-4 right-4 z-[1700] flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} onClose={onClose} />
        ))}
      </AnimatePresence>
    </div>
  );
};
