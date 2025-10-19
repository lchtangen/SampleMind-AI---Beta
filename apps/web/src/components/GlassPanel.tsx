import React from 'react'
import clsx from 'clsx'

type Props = React.HTMLAttributes<HTMLDivElement> & {
  variant?: 'default' | 'light' | 'strong'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const variantMap: Record<NonNullable<Props['variant']>, string> = {
  default: 'glass',
  light: 'glass-light',
  strong: 'glass-strong',
}

const padMap: Record<NonNullable<Props['padding']>, string> = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
}

export default function GlassPanel({ variant = 'default', padding = 'md', className, children, ...rest }: Props) {
  return (
    <div className={clsx('rounded-glass border border-glass-border', variantMap[variant], padMap[padding], className)} {...rest}>
      {children}
    </div>
  )
}
