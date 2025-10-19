"use client"

import React from 'react'
import clsx from 'clsx'

type Props = {
  open: boolean
  onClose: () => void
  title?: string
  children?: React.ReactNode
  className?: string
}

export default function Modal({ open, onClose, title, children, className }: Props) {
  if (!open) return null
  return (
    <div className={clsx('fixed inset-0 z-50 flex items-center justify-center')}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-md" onClick={onClose} />
      <div className={clsx('relative z-10 w-full max-w-lg rounded-glass border border-glass-border glass p-6 shadow-glass-glow-blue', className)}>
        {title && <h3 className="text-xl mb-3">{title}</h3>}
        {children}
        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-glass border border-glass-border glass hover:glass-hover transition duration-fast ease-smooth">Close</button>
        </div>
      </div>
    </div>
  )
}
