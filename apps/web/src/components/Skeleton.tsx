import React from 'react'
import clsx from 'clsx'

type Props = React.HTMLAttributes<HTMLDivElement> & {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animation?: 'pulse' | 'wave' | 'none'
}

export default function Skeleton({
  variant = 'text',
  width,
  height,
  animation = 'pulse',
  className,
  ...rest
}: Props) {
  const baseClasses = 'bg-dark-300 rounded-glass'
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-spark-flow bg-gradient-to-r from-dark-300 via-dark-200 to-dark-300 bg-[length:200%_100%]',
    none: '',
  }

  const variantClasses = {
    text: 'h-4',
    circular: 'rounded-full',
    rectangular: '',
  }

  const style: React.CSSProperties = {}
  if (width) style.width = typeof width === 'number' ? `${width}px` : width
  if (height) style.height = typeof height === 'number' ? `${height}px` : height

  return (
    <div
      className={clsx(baseClasses, variantClasses[variant], animationClasses[animation], className)}
      style={style}
      {...rest}
    />
  )
}
