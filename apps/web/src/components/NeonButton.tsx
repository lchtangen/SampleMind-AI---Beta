import React from 'react'
import clsx from 'clsx'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  color?: 'blue' | 'purple' | 'cyan' | 'magenta'
  size?: 'sm' | 'md' | 'lg'
}

const colorMap: Record<NonNullable<Props['color']>, string> = {
  blue: 'text-text-primary bg-dark-400 hover:bg-dark-300 shadow-glow-blue',
  purple: 'text-text-primary bg-dark-400 hover:bg-dark-300 shadow-glow-purple',
  cyan: 'text-text-primary bg-dark-400 hover:bg-dark-300 shadow-glow-cyan',
  magenta: 'text-text-primary bg-dark-400 hover:bg-dark-300 shadow-glow-magenta',
}

const sizeMap: Record<NonNullable<Props['size']>, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-5 py-3 text-lg',
}

export default function NeonButton({ color = 'blue', size = 'md', className, children, ...rest }: Props) {
  return (
    <button
      className={clsx(
        'relative rounded-glass border border-glass-border backdrop-blur animate-[none] transition duration-fast ease-smooth',
        'hover:shadow-glow-blue hover:translate-y-[-1px] active:translate-y-0',
        'focus:outline-none focus:ring-2 focus:ring-cyber-blue/40',
        colorMap[color],
        sizeMap[size],
        className
      )}
      {...rest}
    >
      {children}
    </button>
  )
}
