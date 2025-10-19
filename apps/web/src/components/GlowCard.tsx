import React from 'react'
import clsx from 'clsx'

type Props = React.HTMLAttributes<HTMLDivElement> & {
  accent?: 'blue' | 'purple' | 'cyan' | 'magenta'
}

const shadowMap: Record<NonNullable<Props['accent']>, string> = {
  blue: 'shadow-glow-blue',
  purple: 'shadow-glow-purple',
  cyan: 'shadow-glow-cyan',
  magenta: 'shadow-glow-magenta',
}

export default function GlowCard({ accent = 'blue', className, children, ...rest }: Props) {
  return (
    <div
      className={clsx(
        'rounded-glass border border-glass-border glass p-6 transition duration-fast ease-smooth hover:glass-hover',
        shadowMap[accent],
        className
      )}
      {...rest}
    >
      {children}
    </div>
  )
}
