"use client"

import React from 'react'
import GlassPanel from '../../src/components/GlassPanel'
import NeonButton from '../../src/components/NeonButton'
import NeonTabs from '../../src/components/NeonTabs'
import GlowCard from '../../src/components/GlowCard'
import GradientBackground from '../../src/components/GradientBackground'
import WaveformCanvas from '../../src/components/WaveformCanvas'
import Skeleton from '../../src/components/Skeleton'
import SpectrogramCanvas from '../../src/components/SpectrogramCanvas'
import ThreeJSVisualizer from '../../src/components/ThreeJSVisualizer'

export default function GalleryPage() {
  return (
    <main className="min-h-screen bg-dark-500 text-text-primary relative overflow-hidden">
      {/* Animated background */}
      <GradientBackground variant="animated" opacity={0.2} />

      <section className="relative z-10 mx-auto max-w-6xl px-6 py-12 space-y-10">
        <header className="space-y-3">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight glow-text-cyan">SampleMind Neon Glass Gallery</h1>
          <p className="text-text-secondary max-w-3xl">
            Preview of the cyberpunk glassmorphism macOS-inspired UI theme. Explore glass panels, neon buttons, gradients,
            motion presets, and density suitable for high-DPI displays.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GlassPanel padding="lg" className="shadow-glass-glow-blue">
            <h2 className="text-2xl mb-3">Glass Panels</h2>
            <p className="text-text-secondary mb-6">Frosted surfaces with subtle borders and depth shadows.</p>
            <div className="flex gap-3 flex-wrap">
              <GlassPanel variant="light" padding="sm" className="w-full md:w-auto">light</GlassPanel>
              <GlassPanel variant="default" padding="sm" className="w-full md:w-auto">default</GlassPanel>
              <GlassPanel variant="strong" padding="sm" className="w-full md:w-auto">strong</GlassPanel>
            </div>
          </GlassPanel>

          <GlassPanel padding="lg" className="shadow-glass-glow-purple">
            <h2 className="text-2xl mb-3">Neon Buttons</h2>
            <p className="text-text-secondary mb-6">Glowing actions with macOS-like motion.</p>
            <div className="flex gap-3 flex-wrap">
              <NeonButton color="blue">Primary Blue</NeonButton>
              <NeonButton color="purple">Neon Purple</NeonButton>
              <NeonButton color="cyan">Accent Cyan</NeonButton>
              <NeonButton color="magenta">Accent Magenta</NeonButton>
            </div>
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Gradients & Motion</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-glass h-24 bg-spark-1 shadow-glow-blue" />
              <div className="rounded-glass h-24 bg-spark-2 shadow-glow-purple" />
              <div className="rounded-glass h-24 bg-spark-3 shadow-glow-magenta" />
            </div>
            <div className="mt-6 flex gap-3">
              <div className="rounded-glass h-24 w-full bg-spark-animated bg-[length:400%_400%] animate-spark-flow" />
            </div>
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Neon Tabs</h2>
            <NeonTabs
              tabs={[
                { id: 'one', label: 'Overview', content: <div className="text-text-secondary">Overview content in glass container.</div> },
                { id: 'two', label: 'Details', content: <div className="text-text-secondary">Details with macOS-like motion.</div> },
                { id: 'three', label: 'Settings', content: <div className="text-text-secondary">Settings panel preview.</div> },
              ]}
            />
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Glow Cards</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <GlowCard accent="blue">Blue glow</GlowCard>
              <GlowCard accent="purple">Purple glow</GlowCard>
              <GlowCard accent="magenta">Magenta glow</GlowCard>
            </div>
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Waveform Preview</h2>
            <WaveformCanvas height={140} />
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Skeleton Loading States</h2>
            <div className="space-y-3">
              <Skeleton animation="pulse" height={20} />
              <Skeleton animation="wave" height={20} width="80%" />
              <div className="flex gap-3">
                <Skeleton variant="circular" width={48} height={48} />
                <div className="flex-1 space-y-2">
                  <Skeleton height={16} />
                  <Skeleton height={16} width="60%" />
                </div>
              </div>
            </div>
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">Mel Spectrogram</h2>
            <SpectrogramCanvas height={180} />
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-4">3D Audio Visualizer (Placeholder)</h2>
            <ThreeJSVisualizer height={350} />
          </GlassPanel>

          <GlassPanel padding="lg" className="col-span-1 md:col-span-2">
            <h2 className="text-2xl mb-2">✅ Phase 1-2 Components Complete</h2>
            <p className="text-text-secondary mb-4">12 core components implemented. Next: Pages, Backend API, AI Integration.</p>
            <ul className="list-disc pl-6 text-text-secondary space-y-1">
              <li>Phase 3: Landing, Dashboard, Upload, Library pages</li>
              <li>Phase 4: Three.js full implementation, shader effects</li>
              <li>Phase 7: FastAPI backend bootstrap</li>
              <li>Phase 8: AI/quantum neurologic UX hooks</li>
            </ul>
          </GlassPanel>
        </div>
      </section>
    </main>
  )
}
