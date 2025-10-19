"use client"

import React from 'react'

export default function WaveformCanvas({ height = 120 }: { height?: number }) {
  const ref = React.useRef<HTMLCanvasElement | null>(null)
  const animRef = React.useRef<number | null>(null)

  React.useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let w = (canvas.width = canvas.offsetWidth * devicePixelRatio)
    let h = (canvas.height = height * devicePixelRatio)

    const onResize = () => {
      w = canvas.width = canvas.offsetWidth * devicePixelRatio
      h = canvas.height = height * devicePixelRatio
    }
    const ro = new ResizeObserver(onResize)
    ro.observe(canvas)

    let t = 0
    const bars = 120

    const draw = () => {
      if (!ctx) return
      ctx.clearRect(0, 0, w, h)

      // background subtle
      const bg = ctx.createLinearGradient(0, 0, w, h)
      bg.addColorStop(0, 'rgba(0,0,0,0.2)')
      bg.addColorStop(1, 'rgba(0,0,0,0.1)')
      ctx.fillStyle = bg
      ctx.fillRect(0, 0, w, h)

      const grad = ctx.createLinearGradient(0, 0, w, 0)
      grad.addColorStop(0, 'rgba(0, 255, 204, 0.9)') // cyan
      grad.addColorStop(0.5, 'rgba(0, 160, 255, 0.9)') // blue
      grad.addColorStop(1, 'rgba(255, 0, 255, 0.9)') // magenta

      const barW = w / bars
      for (let i = 0; i < bars; i++) {
        const phase = (i / bars) * Math.PI * 2
        const amp = Math.sin(phase + t) * 0.5 + 0.5
        const barH = (0.2 + amp * 0.7) * (h * 0.9)
        const x = i * barW
        const y = (h - barH) / 2
        ctx.fillStyle = grad
        ctx.fillRect(x + 1 * devicePixelRatio, y, barW - 2 * devicePixelRatio, barH)
      }

      t += 0.03
      animRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current)
      ro.disconnect()
    }
  }, [height])

  return (
    <div className="w-full rounded-glass overflow-hidden border border-glass-border glass">
      <canvas ref={ref} style={{ width: '100%', height }} />
    </div>
  )
}
