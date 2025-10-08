/**
 * Component Showcase Page
 * Week 1 Component Preview - All 9 tested components
 */

import {
  AudioSpectrum,
  MusicProductionScene,
  VinylTurntable,
  WaveformDisplay,
} from "@/components/3d/MusicProductionShowcase";
import {
  AdvancedMusicProductionScene,
  ControlPanelScene,
  GalaxyWaveformScene,
  HolographicMixerScene,
} from "@/components/3d/Tier2AdvancedShowcase";
import CyberpunkInput from "@/components/atoms/CyberpunkInput/CyberpunkInput";
import GlowingBadge from "@/components/atoms/GlowingBadge/GlowingBadge";
import { NeonButton } from "@/components/atoms/NeonButton";
import NeonDivider from "@/components/atoms/NeonDivider/NeonDivider";
import { Skeleton } from "@/components/atoms/Skeleton/Skeleton";
import { CyberpunkBackground } from "@/components/effects/CyberpunkBackground";
import AnimatedCard from "@/components/molecules/AnimatedCard/AnimatedCard";
import CyberpunkModal from "@/components/molecules/CyberpunkModal/CyberpunkModal";
import WaveformVisualizer from "@/components/molecules/WaveformVisualizer/WaveformVisualizer";
import React, { useEffect, useState } from "react";

export const ComponentShowcase: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");

  // Diagnostic logging
  useEffect(() => {
    console.log("✅ ComponentShowcase mounted!");
    console.log("📦 CyberpunkBackground:", CyberpunkBackground);
    console.log("📦 NeonButton:", NeonButton);

    // Check if Tailwind classes are working
    const testElement = document.createElement("div");
    testElement.className = "bg-primary text-white p-4";
    document.body.appendChild(testElement);
    const computed = window.getComputedStyle(testElement);
    console.log(
      "🎨 Tailwind test - bg-primary background:",
      computed.backgroundColor
    );
    console.log("🎨 Tailwind test - text-white color:", computed.color);
    console.log("🎨 Tailwind test - p-4 padding:", computed.padding);
    document.body.removeChild(testElement);
  }, []);

  // Sample waveform data
  const waveformData = Array.from({ length: 64 }, () => Math.random() * 100);

  return (
    <>
      <CyberpunkBackground />

      <div className="min-h-screen p-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-12 text-center">
            <h1
              className="text-5xl font-heading font-bold mb-4"
              style={{ color: "#FFFFFF" }}
            >
              🎵 SampleMind AI Component Showcase
            </h1>
            <p className="text-xl mb-2" style={{ color: "#E2E8F0" }}>
              Week 1 Achievement: 328 E2E Tests Across 9 Components
            </p>
            <p style={{ color: "#CBD5E1" }}>
              100% Accessibility • 5 Browser Support • Cyberpunk Aesthetic
            </p>
          </div>

          {/* Diagnostic Box */}
          <div
            className="mb-8 p-6 rounded-lg"
            style={{
              backgroundColor: "#8b5cf6",
              color: "white",
              border: "2px solid #fbbf24",
            }}
          >
            <h2 className="text-2xl font-bold mb-2">🔍 Diagnostic Test</h2>
            <p className="text-lg">
              If this box has a purple background with YELLOW BORDER, Tailwind
              is working!
            </p>
            <p className="text-sm mt-2" style={{ color: "#E9D5FF" }}>
              Check browser console for detailed logs
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
            <div className="glass-card text-center p-6 rounded-xl">
              <div
                className="text-3xl font-bold mb-2"
                style={{ color: "#A78BFA" }}
              >
                328
              </div>
              <div className="text-sm" style={{ color: "#E2E8F0" }}>
                E2E Tests
              </div>
            </div>
            <div className="glass-card text-center p-6 rounded-xl">
              <div
                className="text-3xl font-bold mb-2"
                style={{ color: "#22D3EE" }}
              >
                4,548+
              </div>
              <div className="text-sm" style={{ color: "#E2E8F0" }}>
                Lines of Code
              </div>
            </div>
            <div className="glass-card text-center p-6 rounded-xl">
              <div
                className="text-3xl font-bold mb-2"
                style={{ color: "#F472B6" }}
              >
                9
              </div>
              <div className="text-sm" style={{ color: "#E2E8F0" }}>
                Components
              </div>
            </div>
            <div className="glass-card text-center p-6 rounded-xl">
              <div
                className="text-3xl font-bold mb-2"
                style={{ color: "#34D399" }}
              >
                100%
              </div>
              <div className="text-sm" style={{ color: "#E2E8F0" }}>
                Accessibility
              </div>
            </div>
          </div>

          <NeonDivider gradient="cyber" className="mb-12" />

          {/* � MUSIC PRODUCTION 3D SHOWCASE */}
          <section className="mb-12">
            <h2
              className="text-3xl font-heading font-bold mb-6"
              style={{ color: "#FFFFFF" }}
            >
              � Music Production 3D Visualizers{" "}
              <GlowingBadge variant="primary" size="lg">
                CUSTOM
              </GlowingBadge>
            </h2>

            <div className="glass-card p-6 rounded-xl mb-8 border-2 border-primary/30">
              <h3 className="text-xl font-semibold text-primary mb-3">
                ⚡ Complete Audio Visualization Scene
              </h3>
              <p className="text-text-secondary mb-4">
                Custom-built 3D music production visualizer with 32-band
                frequency analyzer, 128-point waveform ring, animated vinyl
                record, and pulsing beat indicator. No dependencies on heavy
                libraries - pure React Three Fiber.
              </p>
              <MusicProductionScene />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="glass-card p-4 rounded-xl">
                <h4 className="text-lg font-semibold text-accent-cyan mb-3">
                  ⚡ Audio Spectrum
                </h4>
                <AudioSpectrum />
              </div>

              <div className="glass-card p-4 rounded-xl">
                <h4 className="text-lg font-semibold text-accent-pink mb-3">
                  � Waveform Ring
                </h4>
                <WaveformDisplay />
              </div>

              <div className="glass-card p-4 rounded-xl">
                <h4 className="text-lg font-semibold text-primary mb-3">
                  💿 Vinyl Turntable
                </h4>
                <VinylTurntable />
              </div>
            </div>

            <div className="glass-card p-6 rounded-xl bg-gradient-to-r from-primary/10 to-accent-cyan/10 border border-primary/20">
              <h4 className="text-lg font-semibold text-white mb-3">
                🎨 Music Production Features:
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-primary">✓</span>
                  <span className="text-text-secondary">32-band Spectrum</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">✓</span>
                  <span className="text-text-secondary">
                    128-point Waveform
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-pink">✓</span>
                  <span className="text-text-secondary">Vinyl Animation</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-primary">✓</span>
                  <span className="text-text-secondary">Beat Pulsing</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">✓</span>
                  <span className="text-text-secondary">
                    Neon Glassmorphism
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-pink">✓</span>
                  <span className="text-text-secondary">
                    Frequency Reactive
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-primary">✓</span>
                  <span className="text-text-secondary">Cyberpunk Theme</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">✓</span>
                  <span className="text-text-secondary">60 FPS Smooth</span>
                </div>
              </div>
            </div>
          </section>

          <NeonDivider gradient="cyber" className="mb-12" />

          {/* TIER 2: Advanced Music Production 3D Visualizers */}
          <section className="mb-12">
            <h2 className="text-3xl font-heading font-bold mb-6 bg-gradient-purple bg-clip-text text-transparent">
              🚀 TIER 2: Advanced 3D Visualizers{" "}
              <GlowingBadge variant="cyan" size="md">
                Custom Shaders
              </GlowingBadge>{" "}
              <GlowingBadge variant="pink" size="md">
                10K+ Particles
              </GlowingBadge>
            </h2>

            <div className="mb-8">
              <h3 className="text-xl font-semibold text-text-primary mb-4">
                Main Advanced Scene - Combined Effects
              </h3>
              <AdvancedMusicProductionScene />
              <p className="text-text-secondary text-sm mt-4">
                Features: Audio Spectrum Tunnel (30 rings), 3D Beat Grid (256
                cubes), Particle Synthesizer (10,000 particles)
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">
                  Holographic Mixer
                </h3>
                <HolographicMixerScene />
                <p className="text-text-secondary text-sm mt-2">
                  8-channel mixer with holographic faders, rotating knobs,
                  custom shader effects
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">
                  Galaxy Waveform
                </h3>
                <GalaxyWaveformScene />
                <p className="text-text-secondary text-sm mt-2">
                  5,000 particles in spiral galaxy formation, RGB gradient,
                  vertical wave motion
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">
                  Neon Control Panel
                </h3>
                <ControlPanelScene />
                <p className="text-text-secondary text-sm mt-2">
                  16 interactive buttons with chromatic aberration shader, RGB
                  split effect
                </p>
              </div>
            </div>

            {/* Technical Specs */}
            <div className="mt-8 glass-card p-6 rounded-xl">
              <h3 className="text-xl font-semibold text-text-primary mb-4">
                Advanced Features & Performance
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-primary">⚡</span>
                  <span className="text-text-secondary">
                    Custom GLSL Shaders
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">⚡</span>
                  <span className="text-text-secondary">
                    Holographic Materials
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-pink">⚡</span>
                  <span className="text-text-secondary">Neon Glow Effects</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-primary">⚡</span>
                  <span className="text-text-secondary">
                    Chromatic Aberration
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">⚡</span>
                  <span className="text-text-secondary">
                    Fresnel Rim Lighting
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-pink">⚡</span>
                  <span className="text-text-secondary">
                    InstancedMesh (15K+)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-primary">⚡</span>
                  <span className="text-text-secondary">60 FPS Guaranteed</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-accent-cyan">⚡</span>
                  <span className="text-text-secondary">Additive Blending</span>
                </div>
              </div>
            </div>
          </section>

          <NeonDivider gradient="cyber" className="mb-12" />

          {/* 1. NeonButton */}
          <section className="mb-12">
            <h2
              className="text-2xl font-heading font-semibold mb-6"
              style={{ color: "#FFFFFF" }}
            >
              1. NeonButton Component{" "}
              <GlowingBadge variant="primary" size="sm">
                25 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="flex flex-wrap gap-4 items-center">
                <NeonButton variant="primary" size="sm">
                  Small Primary
                </NeonButton>
                <NeonButton variant="primary">Medium Primary</NeonButton>
                <NeonButton variant="primary" size="lg" pulse>
                  Large with Pulse
                </NeonButton>
                <NeonButton variant="secondary">Secondary</NeonButton>
                <NeonButton variant="ghost">Ghost</NeonButton>
                <NeonButton variant="danger">Danger</NeonButton>
                <NeonButton loading>Loading...</NeonButton>
                <NeonButton disabled>Disabled</NeonButton>
              </div>
            </div>
          </section>

          {/* 2. CyberpunkInput */}
          <section className="mb-12">
            <h2
              className="text-2xl font-heading font-semibold mb-6"
              style={{ color: "#FFFFFF" }}
            >
              2. CyberpunkInput Component{" "}
              <GlowingBadge variant="cyan" size="sm">
                38 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <CyberpunkInput
                  label="Default Input"
                  placeholder="Enter text..."
                  value={inputValue}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setInputValue(e.target.value)
                  }
                />
                <CyberpunkInput
                  label="Success State"
                  placeholder="Valid input"
                  state="success"
                />
                <CyberpunkInput
                  label="Error State"
                  placeholder="Invalid input"
                  state="error"
                />
                <CyberpunkInput
                  label="Disabled State"
                  placeholder="Can't type here"
                  disabled
                />
              </div>
            </div>
          </section>

          {/* 3. GlowingBadge */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              3. GlowingBadge Component{" "}
              <GlowingBadge variant="pink" size="sm">
                32 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="flex flex-wrap gap-4">
                <GlowingBadge variant="primary" pulse>
                  Primary
                </GlowingBadge>
                <GlowingBadge variant="success">Success</GlowingBadge>
                <GlowingBadge variant="warning">Warning</GlowingBadge>
                <GlowingBadge variant="error">Error</GlowingBadge>
                <GlowingBadge variant="info">Info</GlowingBadge>
                <GlowingBadge variant="cyan">Cyan</GlowingBadge>
                <GlowingBadge variant="pink">Pink</GlowingBadge>
                <GlowingBadge variant="primary" size="sm">
                  Small
                </GlowingBadge>
                <GlowingBadge variant="primary" size="lg">
                  Large
                </GlowingBadge>
              </div>
            </div>
          </section>

          {/* 4. NeonDivider */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              4. NeonDivider Component{" "}
              <GlowingBadge variant="success" size="sm">
                27 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="space-y-8">
                <div>
                  <p className="text-sm text-text-secondary mb-2">
                    Purple Gradient
                  </p>
                  <NeonDivider gradient="purple" />
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-2">
                    Cyber Gradient (Purple to Cyan)
                  </p>
                  <NeonDivider gradient="cyber" />
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-2">
                    Neon Gradient (Multi-color)
                  </p>
                  <NeonDivider gradient="neon" />
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-2">
                    Pink Gradient with High Glow
                  </p>
                  <NeonDivider gradient="pink" glowIntensity="high" />
                </div>
              </div>
            </div>
          </section>

          {/* 5. Skeleton */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              5. Skeleton Component{" "}
              <GlowingBadge variant="warning" size="sm">
                33 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Skeleton variant="rectangular" width="100%" height={100} />
                <Skeleton variant="circular" width={100} height={100} />
                <Skeleton variant="text" lines={3} />
                <div className="glass-card p-6">
                  <div className="flex items-start gap-4">
                    <Skeleton variant="circular" width={48} height={48} />
                    <div className="flex-1 space-y-2">
                      <Skeleton variant="text" width="60%" />
                      <Skeleton variant="text" width="80%" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* 6 & 7. AnimatedCard */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              6 & 7. GlassmorphicCard & AnimatedCard{" "}
              <GlowingBadge variant="info" size="sm">
                66 tests total
              </GlowingBadge>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <AnimatedCard
                index={0}
                title="Fade In"
                description="Smooth opacity transition animation"
              />
              <AnimatedCard
                index={1}
                title="Slide Up"
                description="Slides from bottom with Y transform"
                onClick={() => alert("Card clicked!")}
              />
              <AnimatedCard
                index={2}
                title="Scale"
                description="Grows from 95% to 100% scale"
              />
            </div>
          </section>

          {/* 8. CyberpunkModal */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              8. CyberpunkModal Component{" "}
              <GlowingBadge variant="error" size="sm">
                55 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="flex flex-wrap gap-4">
                <NeonButton onClick={() => setModalOpen(true)}>
                  Open Modal Demo
                </NeonButton>
              </div>
            </div>
          </section>

          {/* 9. WaveformVisualizer */}
          <section className="mb-12">
            <h2 className="text-2xl font-heading font-semibold text-text-primary mb-6">
              9. WaveformVisualizer Component{" "}
              <GlowingBadge variant="cyan" size="sm">
                52 tests
              </GlowingBadge>
            </h2>
            <div className="glass-card p-8 rounded-xl">
              <div className="space-y-6">
                <div>
                  <p className="text-sm text-text-secondary mb-4">
                    Purple Color Scheme
                  </p>
                  <WaveformVisualizer
                    data={waveformData}
                    colorScheme="purple"
                    height={120}
                    showLabels
                  />
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-4">
                    Cyber Color Scheme (Interactive)
                  </p>
                  <WaveformVisualizer
                    data={waveformData}
                    colorScheme="cyber"
                    height={120}
                    interactive
                    onBarClick={(index: number, value: number) =>
                      alert(`Bar ${index}: ${value.toFixed(1)}`)
                    }
                  />
                </div>
                <div>
                  <p className="text-sm text-text-secondary mb-4">
                    Neon Color Scheme
                  </p>
                  <WaveformVisualizer
                    data={waveformData}
                    colorScheme="neon"
                    height={120}
                    showLabels
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Footer */}
          <NeonDivider gradient="neon" className="my-12" />
          <div className="text-center py-8">
            <p className="text-text-secondary mb-4">
              All components tested with 328 comprehensive E2E tests
            </p>
            <div className="flex justify-center gap-2 flex-wrap">
              <GlowingBadge variant="primary">WCAG 2.1 AA</GlowingBadge>
              <GlowingBadge variant="cyan">5 Browsers</GlowingBadge>
              <GlowingBadge variant="pink">Responsive</GlowingBadge>
              <GlowingBadge variant="success">Accessible</GlowingBadge>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <CyberpunkModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="CyberpunkModal Demo"
        size="lg"
        footer={
          <div className="flex gap-4 justify-end">
            <NeonButton variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </NeonButton>
            <NeonButton variant="primary" onClick={() => setModalOpen(false)}>
              Confirm
            </NeonButton>
          </div>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            This is a comprehensive modal component with:
          </p>
          <ul className="list-disc list-inside space-y-2 text-text-secondary">
            <li>Focus trap (Tab cycles within modal)</li>
            <li>ESC key to close</li>
            <li>Backdrop click to close (optional)</li>
            <li>5 size variants (sm, md, lg, xl, full)</li>
            <li>Spring animations with Framer Motion</li>
            <li>Body scroll lock</li>
            <li>Glassmorphic styling with neon glow</li>
            <li>100% WCAG 2.1 AA compliant</li>
          </ul>
          <div className="mt-6">
            <CyberpunkInput
              label="Test Input in Modal"
              placeholder="Focus trap works!"
            />
          </div>
        </div>
      </CyberpunkModal>
    </>
  );
};

export default ComponentShowcase;
