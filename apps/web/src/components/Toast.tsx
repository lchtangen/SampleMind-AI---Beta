"use client"

import React from 'react'
import clsx from 'clsx'

export type ToastType = 'info' | 'success' | 'warning' | 'error'

export type Toast = {
  id: string
  message: string
  type: ToastType
  duration?: number
}

type Props = {
  toasts: Toast[]
  onDismiss: (id: string) => void
  position?: 'top-right' | 'top-center' | 'top-left' | 'bottom-right' | 'bottom-center' | 'bottom-left'
}

const typeStyles: Record<ToastType, string> = {
  info: 'border-cyber-blue shadow-glow-blue',
  success: 'border-success shadow-glow-cyan',
  warning: 'border-warning',
  error: 'border-error shadow-glow-magenta',
}

const positionStyles = {
  'top-right': 'top-4 right-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  'bottom-left': 'bottom-4 left-4',
}

export default function Toast({ toasts, onDismiss, position = 'top-right' }: Props) {
  return (
    <div className={clsx('fixed z-50 flex flex-col gap-2 w-80', positionStyles[position])}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={clsx(
            'rounded-glass border glass p-4 shadow-glass animate-slide-down transition duration-fast ease-smooth',
            typeStyles[toast.type]
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-text-primary">{toast.message}</p>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-text-secondary hover:text-text-primary transition"
              aria-label="Dismiss"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
