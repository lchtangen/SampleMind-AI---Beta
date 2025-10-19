"use client"

import React from 'react'
import clsx from 'clsx'

type Option = { value: string; label: string }

type Props = {
  options: Option[]
  value?: string
  onChange?: (v: string) => void
  placeholder?: string
  className?: string
}

export default function Dropdown({ options, value, onChange, placeholder = 'Select…', className }: Props) {
  const [open, setOpen] = React.useState(false)
  const [active, setActive] = React.useState<string | undefined>(value)
  const buttonRef = React.useRef<HTMLButtonElement | null>(null)
  const listRef = React.useRef<HTMLUListElement | null>(null)

  React.useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!listRef.current || !buttonRef.current) return
      if (!listRef.current.contains(e.target as Node) && !buttonRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const onSelect = (v: string) => {
    setActive(v)
    setOpen(false)
    onChange?.(v)
  }

  return (
    <div className={clsx('relative inline-block text-left', className)}>
      <button
        ref={buttonRef}
        className={clsx(
          'px-4 py-2 rounded-glass border border-glass-border glass hover:glass-hover transition duration-fast ease-smooth min-w-[10rem] text-left'
        )}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {options.find(o => o.value === active)?.label || <span className="text-text-tertiary">{placeholder}</span>}
      </button>
      {open && (
        <ul
          ref={listRef}
          className="absolute mt-2 w-full rounded-glass border border-glass-border glass p-1 shadow-glass-glow-blue z-50 max-h-64 overflow-auto"
          role="listbox"
        >
          {options.map(o => (
            <li
              key={o.value}
              role="option"
              aria-selected={o.value === active}
              onClick={() => onSelect(o.value)}
              className={clsx(
                'px-3 py-2 rounded-glass cursor-pointer transition duration-fast ease-smooth',
                o.value === active ? 'bg-dark-300 text-text-primary' : 'text-text-secondary hover:text-text-primary hover:bg-dark-300'
              )}
            >
              {o.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
