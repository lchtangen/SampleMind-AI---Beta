"use client";

/**
 * THREE.JS 3D AUDIO VISUALIZER
 * GPU-accelerated particle system with audio-reactive animations
 * Features: Particle system, post-processing, audio reactivity, multiple presets
 */

import { useAudioReactive } from "@/hooks/useAudioReactive";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Bloom, Chromatic, EffectComposer } from "@react-three/postprocessing";
import React, { Suspense, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import LoadingSpinner from "../ui/LoadingSpinner";

export type VisualizerPreset = "particles" | "sphere" | "waves" | "ribbons";

interface ThreeJSAudioVisualizerProps {
  className?: string;
  preset?: VisualizerPreset;
  audioElement?: HTMLAudioElement;
  enabled?: boolean;
  qualityLevel?: "low" | "medium" | "high";
}

/**
 * GPU-Accelerated Particle System Component
 * Uses Three.js BufferGeometry and InstancedMesh for performance
 */
const ParticleSystem: React.FC<{
  audioData: any;
  count?: number;
  preset: VisualizerPreset;
}> = ({ audioData, count = 5000, preset }) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const particlesRef = useRef<
    {
      x: number;
      y: number;
      z: number;
      vx: number;
      vy: number;
      vz: number;
      life: number;
    }[]
  >([]);

  useEffect(() => {
    // Initialize particles
    const particles = [];
    for (let i = 0; i < count; i++) {
      particles.push({
        x: (Math.random() - 0.5) * 4,
        y: (Math.random() - 0.5) * 4,
        z: (Math.random() - 0.5) * 4,
        vx: (Math.random() - 0.5) * 0.02,
        vy: (Math.random() - 0.5) * 0.02,
        vz: (Math.random() - 0.5) * 0.02,
        life: Math.random(),
      });
    }
    particlesRef.current = particles;
  }, [count]);

  useFrame((_state, delta) => {
    if (!meshRef.current) return;

    const particles = particlesRef.current;
    const amplitude = audioData.amplitude || 0;
    const frequency = audioData.frequency || 0;

    // Update particles based on audio
    for (let i = 0; i < Math.min(particles.length, count); i++) {
      const p = particles[i];

      // Audio-reactive movement
      if (preset === "particles") {
        // Particles expand on beat
        const speed = 0.05 + amplitude * 0.1;
        p.x += p.vx * speed;
        p.y += p.vy * speed;
        p.z += p.vz * speed;
      } else if (preset === "sphere") {
        // Particles orbit in sphere
        const angle = (i / count) * Math.PI * 2 + frequency * 2;
        const radius = 2 + amplitude * 1;
        p.x = Math.cos(angle) * radius;
        p.y = Math.sin(angle) * radius * 0.7;
        p.z = Math.sin(angle * 0.5) * radius;
      } else if (preset === "waves") {
        // Particles form wave pattern
        p.x = ((i % Math.sqrt(count)) / Math.sqrt(count) - 0.5) * 4;
        p.z = (Math.floor(i / Math.sqrt(count)) / Math.sqrt(count) - 0.5) * 4;
        p.y = Math.sin((p.x + frequency * 4) * 5) * amplitude * 2;
      } else if (preset === "ribbons") {
        // Particles form ribbon trails
        const ribbon = i % 50;
        const index = Math.floor(i / 50);
        p.x = (ribbon / 50 - 0.5) * 4;
        p.z = (index / (count / 50) - 0.5) * 4;
        p.y = Math.sin((p.x + p.z + frequency * 3) * 3) * amplitude * 1.5;
      }

      // Reset particles that go too far
      if (
        Math.abs(p.x) > 5 ||
        Math.abs(p.y) > 5 ||
        Math.abs(p.z) > 5 ||
        p.life < 0
      ) {
        p.x = (Math.random() - 0.5) * 4;
        p.y = (Math.random() - 0.5) * 4;
        p.z = (Math.random() - 0.5) * 4;
        p.life = 1;
      }

      // Decay life
      p.life -= delta * 0.3;

      // Update instance matrix
      if (meshRef.current) {
        const matrix = new THREE.Matrix4();
        const scale = 1 + audioData.amplitude * 0.5;
        matrix.setPosition(p.x, p.y, p.z);
        matrix.scale(new THREE.Vector3(scale * 0.1, scale * 0.1, scale * 0.1));
        meshRef.current.setMatrixAt(i, matrix);
      }
    }

    if (meshRef.current) {
      meshRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  const geometry = new THREE.IcosahedronGeometry(0.05, 3);
  const material = new THREE.MeshPhongMaterial({
    color: new THREE.Color().setHSL(0.1 + audioData.frequency * 0.3, 0.9, 0.6),
    emissive: new THREE.Color().setHSL(
      0.05 + audioData.frequency * 0.2,
      1,
      0.3 + audioData.amplitude * 0.2,
    ),
    wireframe: false,
  });

  return (
    <instancedMesh
      ref={meshRef}
      geometry={geometry}
      material={material}
      args={[undefined, undefined, count]}
    />
  );
};

/**
 * Camera controller for smooth interaction
 */
const CameraController: React.FC<{ audioData: any }> = ({ audioData }) => {
  const { camera } = useThree();

  useFrame((_state, delta) => {
    // Subtle camera movement based on audio
    const amplitude = audioData.amplitude || 0;
    camera.position.y = 2 + amplitude * 0.5;
    camera.position.z = 5 + amplitude * 0.2;
    camera.lookAt(0, 0, 0);
  });

  return null;
};

/**
 * Lighting setup for 3D scene
 */
const Lighting: React.FC<{ audioData: any }> = ({ audioData }) => {
  return (
    <>
      {/* Ambient light */}
      <ambientLight
        intensity={0.4}
        color={new THREE.Color().setHSL(0.7, 0.8, 0.6)}
      />

      {/* Main directional light */}
      <directionalLight
        position={[5, 10, 7]}
        intensity={1}
        color={new THREE.Color().setHSL(0.2, 0.9, 0.7)}
        castShadow
      />

      {/* Audio-reactive point lights */}
      <pointLight
        position={[-4, 2, -4]}
        intensity={0.5 + (audioData.amplitude || 0) * 0.5}
        color={new THREE.Color().setHSL(0.6, 0.9, 0.5)} // Cyan
      />

      <pointLight
        position={[4, 2, 4]}
        intensity={0.5 + (audioData.frequency || 0) * 0.5}
        color={new THREE.Color().setHSL(0.8, 0.9, 0.5)} // Magenta
      />
    </>
  );
};

/**
 * Main visualizer canvas with all effects
 */
const VisualizerCanvas: React.FC<{
  audioData: any;
  preset: VisualizerPreset;
  qualityLevel: "low" | "medium" | "high";
}> = ({ audioData, preset, qualityLevel }) => {
  const particleCount = {
    low: 1000,
    medium: 3000,
    high: 5000,
  }[qualityLevel];

  const bloomIntensity = {
    low: 0.5,
    medium: 0.8,
    high: 1,
  }[qualityLevel];

  return (
    <Canvas
      camera={{ position: [0, 2, 5], fov: 75 }}
      gl={{
        antialias: qualityLevel === "high",
        powerPreference:
          qualityLevel === "low" ? "low-power" : "high-performance",
      }}
      dpr={qualityLevel === "low" ? 1 : window.devicePixelRatio}
    >
      {/* Background color */}
      <color attach="background" args={["#0a0e27"]} />

      {/* Lighting */}
      <Lighting audioData={audioData} />

      {/* Camera controller */}
      <CameraController audioData={audioData} />

      {/* Particle system */}
      <ParticleSystem
        audioData={audioData}
        count={particleCount}
        preset={preset}
      />

      {/* Effects */}
      <EffectComposer>
        <Bloom
          luminanceThreshold={0.5}
          luminanceSmoothing={0.9}
          intensity={bloomIntensity}
          height={512}
        />
        <Chromatic aberrationAmount={0.02} />
      </EffectComposer>
    </Canvas>
  );
};

/**
 * Main ThreeJS Audio Visualizer Component
 */
export const ThreeJSAudioVisualizer: React.FC<ThreeJSAudioVisualizerProps> = ({
  className = "",
  preset = "particles",
  audioElement,
  enabled = true,
  qualityLevel = "high",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [audioData, setAudioData] = useState({
    amplitude: 0,
    frequency: 0,
    frequencies: [],
    rms: 0,
    isPlaying: false,
  });

  // Use audio hook
  const audioReactive = useAudioReactive({
    enabled,
    smoothing: 0.8,
    fftSize: 256,
  });

  // Connect to audio element if provided
  useEffect(() => {
    if (audioElement) {
      audioReactive.connectToAudioElement(audioElement);
    }
  }, [audioElement, audioReactive]);

  // Update audio data
  useEffect(() => {
    setAudioData(audioReactive);
  }, [audioReactive]);

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-full rounded-2xl overflow-hidden bg-gradient-to-b from-slate-900 via-slate-950 to-black ${className}`}
      style={{
        minHeight: "400px",
        background:
          "linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%)",
      }}
    >
      {/* Canvas */}
      <Suspense
        fallback={
          <div className="flex items-center justify-center w-full h-full">
            <LoadingSpinner />
          </div>
        }
      >
        <VisualizerCanvas
          audioData={audioData}
          preset={preset}
          qualityLevel={qualityLevel}
        />
      </Suspense>

      {/* Overlay info */}
      <div className="absolute top-4 left-4 text-xs text-cyan-400/60 font-mono">
        <div>Amplitude: {(audioData.amplitude * 100).toFixed(0)}%</div>
        <div>Frequency: {(audioData.frequency * 100).toFixed(0)}%</div>
      </div>

      {/* Quality indicator */}
      <div className="absolute bottom-4 right-4 text-xs text-purple-400/60 font-mono">
        {qualityLevel === "low" && "📉 Low Quality"}
        {qualityLevel === "medium" && "📊 Medium Quality"}
        {qualityLevel === "high" && "📈 High Quality"}
      </div>
    </div>
  );
};

export default ThreeJSAudioVisualizer;
