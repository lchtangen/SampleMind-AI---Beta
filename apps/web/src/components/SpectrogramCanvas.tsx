"use client"

import React from 'react'

export default function SpectrogramCanvas({ height = 200 }: { height?: number }) {
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
    const freqBands = 64

    // Mel-scale spectrogram simulation
    const draw = () => {
      if (!ctx) return

      // Scroll effect: shift image left
      const imageData = ctx.getImageData(4 * devicePixelRatio, 0, w - 4 * devicePixelRatio, h)
      ctx.putImageData(imageData, 0, 0)

      // Draw new column on the right
      const x = w - 4 * devicePixelRatio

      for (let i = 0; i < freqBands; i++) {
        const freqY = (i / freqBands) * h
        const bandHeight = h / freqBands
        
        // Simulate frequency data with some variation
        const phase = (i / freqBands) * Math.PI * 4
        const intensity = Math.sin(phase + t * 0.5) * 0.5 + 0.5
        const noise = Math.random() * 0.2

        const value = Math.min(1, intensity + noise)

        // Neon color map (viridis-like)
        let r, g, b
        if (value < 0.25) {
          r = 0
          g = value * 4 * 100
          b = 150
        } else if (value < 0.5) {
          r = 0
          g = 100 + (value - 0.25) * 4 * 100
          b = 150 - (value - 0.25) * 4 * 50
        } else if (value < 0.75) {
          r = (value - 0.5) * 4 * 200
          g = 200
          b = 100 - (value - 0.5) * 4 * 100
        } else {
          r = 200 + (value - 0.75) * 4 * 55
          g = 200 - (value - 0.75) * 4 * 100
          b = 0
        }

        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`
        ctx.fillRect(x, freqY, 4 * devicePixelRatio, bandHeight)
      }

      t += 0.05
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
