import React from 'react'
import clsx from 'clsx'

type Props = React.HTMLAttributes<HTMLDivElement> & {
  variant?: 'spark-1' | 'spark-2' | 'spark-3' | 'spark-4' | 'animated'
  opacity?: number
}

export default function GradientBackground({ variant = 'animated', opacity = 0.2, className, ...rest }: Props) {
  const base = variant === 'animated' ? 'bg-spark-animated bg-[length:400%_400%] animate-spark-flow' : `bg-${variant}`
  return (
    <div
      className={clsx('absolute inset-0 pointer-events-none', base, className)}
      style={{ opacity }}
      {...rest}
    />
  )
}
