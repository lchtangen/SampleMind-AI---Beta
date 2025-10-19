"use client"

import React from 'react'
import clsx from 'clsx'

export type Tab = {
  id: string
  label: string
  content: React.ReactNode
}

type Props = {
  tabs: Tab[]
  defaultTabId?: string
  className?: string
}

export default function NeonTabs({ tabs, defaultTabId, className }: Props) {
  const [active, setActive] = React.useState<string>(defaultTabId ?? tabs[0]?.id)
  return (
    <div className={clsx('w-full', className)}>
      <div className="flex gap-2 mb-4">
        {tabs.map((t) => {
          const isActive = t.id === active
          return (
            <button
              key={t.id}
              onClick={() => setActive(t.id)}
              className={clsx(
                'px-4 py-2 rounded-glass border backdrop-blur transition duration-fast ease-smooth',
                isActive
                  ? 'border-glass-border text-text-primary shadow-glow-cyan glass'
                  : 'border-transparent text-text-secondary hover:text-text-primary glass-light'
              )}
            >
              {t.label}
            </button>
          )
        })}
      </div>
      <div className="rounded-glass border border-glass-border glass p-4">
        {tabs.find((t) => t.id === active)?.content}
      </div>
    </div>
  )
}
