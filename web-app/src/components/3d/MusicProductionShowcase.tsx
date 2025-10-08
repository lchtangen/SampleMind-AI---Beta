/**
 * Music Production 3D Showcase
 * Cyberpunk-themed audio visualizations with glassmorphism
 * Custom-built for SampleMind AI (No Drei dependency)
 */

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef, useState } from "react";
import * as THREE from "three";

// ============================================================================
// AUDIO FREQUENCY VISUALIZER - 3D Bars
// ============================================================================
interface FrequencyBarProps {
  position: [number, number, number];
  index: number;
  color: string;
  emissiveColor: string;
}

function FrequencyBar({
  position,
  index,
  color,
  emissiveColor,
}: FrequencyBarProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Simulate audio frequency response with sine waves
      const time = state.clock.elapsedTime;
      const frequency = 2 + index * 0.2;
      const amplitude =
        Math.abs(Math.sin(time * frequency + index * 0.5)) * 2 + 0.3;

      meshRef.current.scale.y = amplitude;

      // Pulsing emissive glow based on amplitude
      const material = meshRef.current.material as THREE.MeshStandardMaterial;
      material.emissiveIntensity = amplitude * 0.8;

      // Subtle rotation for visual interest
      meshRef.current.rotation.y = Math.sin(time * 0.5 + index) * 0.1;
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      scale={hovered ? [1.2, 1, 1.2] : [1, 1, 1]}
    >
      <boxGeometry args={[0.12, 1, 0.12]} />
      <meshStandardMaterial
        color={color}
        emissive={emissiveColor}
        emissiveIntensity={0.5}
        metalness={0.8}
        roughness={0.2}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

// ============================================================================
// WAVEFORM VISUALIZER - Animated Audio Wave
// ============================================================================
function WaveformRing() {
  const groupRef = useRef<THREE.Group>(null);
  const pointsRef = useRef<THREE.Points>(null);

  const particleCount = 128;

  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const radius = 2.5;
    for (let i = 0; i < particleCount; i++) {
      const angle = (i / particleCount) * Math.PI * 2;
      positions[i * 3] = Math.cos(angle) * radius;
      positions[i * 3 + 1] = 0;
      positions[i * 3 + 2] = Math.sin(angle) * radius;

      // Gradient from purple to cyan
      const t = i / particleCount;
      colors[i * 3] = 0.54 + t * 0.02; // R
      colors[i * 3 + 1] = 0.36 + t * 0.35; // G
      colors[i * 3 + 2] = 0.96 - t * 0.09; // B
    }

    return { positions, colors };
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
    }

    if (pointsRef.current) {
      const positionAttribute = pointsRef.current.geometry.attributes.position;
      const positions = positionAttribute.array as Float32Array;

      const time = state.clock.elapsedTime;
      const radius = 2.5;

      for (let i = 0; i < particleCount; i++) {
        const angle = (i / particleCount) * Math.PI * 2;
        const waveOffset = Math.sin(time * 2 + i * 0.1) * 0.3;
        const currentRadius = radius + waveOffset;

        positions[i * 3] = Math.cos(angle) * currentRadius;
        positions[i * 3 + 1] = Math.sin(time * 3 + i * 0.2) * 0.5;
        positions[i * 3 + 2] = Math.sin(angle) * currentRadius;
      }

      positionAttribute.needsUpdate = true;
    }
  });

  return (
    <group ref={groupRef}>
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={positions}
            itemSize={3}
            args={[positions, 3]}
          />
          <bufferAttribute
            attach="attributes-color"
            count={particleCount}
            array={colors}
            itemSize={3}
            args={[colors, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.08}
          vertexColors
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}

// ============================================================================
// GLASSMORPHIC VINYL RECORD - Spinning with Neon Grooves
// ============================================================================
function NeonVinyl() {
  const vinylRef = useRef<THREE.Mesh>(null);
  const groovesRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (vinylRef.current) {
      vinylRef.current.rotation.z = state.clock.elapsedTime * 0.5;
    }
    if (groovesRef.current) {
      groovesRef.current.rotation.z = state.clock.elapsedTime * 0.5;
    }
  });

  return (
    <group position={[0, 0, -1]}>
      {/* Main vinyl disc */}
      <mesh ref={vinylRef}>
        <cylinderGeometry args={[1.5, 1.5, 0.05, 64]} />
        <meshStandardMaterial
          color="#1a1a2e"
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Neon grooves */}
      <group ref={groovesRef}>
        {Array.from({ length: 12 }).map((_, i) => {
          const radius = 0.5 + i * 0.08;
          return (
            <mesh key={i} rotation={[Math.PI / 2, 0, 0]}>
              <torusGeometry args={[radius, 0.01, 8, 64]} />
              <meshStandardMaterial
                color={i % 2 === 0 ? "#8B5CF6" : "#06B6D4"}
                emissive={i % 2 === 0 ? "#8B5CF6" : "#06B6D4"}
                emissiveIntensity={0.5}
                transparent
                opacity={0.6}
              />
            </mesh>
          );
        })}
      </group>

      {/* Center label */}
      <mesh position={[0, 0.03, 0]}>
        <cylinderGeometry args={[0.3, 0.3, 0.06, 32]} />
        <meshStandardMaterial
          color="#EC4899"
          emissive="#EC4899"
          emissiveIntensity={0.8}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>
    </group>
  );
}

// ============================================================================
// GLOWING SPHERE - Pulsing to "Beat"
// ============================================================================
function PulsingSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.2 + 1;
      meshRef.current.scale.setScalar(pulse);

      const material = meshRef.current.material as THREE.MeshStandardMaterial;
      material.emissiveIntensity = pulse * 0.5;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial
        color="#06B6D4"
        emissive="#06B6D4"
        emissiveIntensity={0.5}
        transparent
        opacity={0.4}
        metalness={0.8}
        roughness={0.2}
      />
    </mesh>
  );
}

// ============================================================================
// MAIN MUSIC PRODUCTION SCENE
// ============================================================================
export function MusicProductionScene() {
  return (
    <div className="relative w-full h-[600px] rounded-xl overflow-hidden glass-card">
      <Canvas
        camera={{ position: [0, 3, 8], fov: 50 }}
        className="bg-gradient-to-b from-bg-primary via-bg-secondary to-bg-tertiary"
      >
        {/* Lighting Setup */}
        <ambientLight intensity={0.2} />
        <directionalLight position={[5, 5, 5]} intensity={1} color="#8B5CF6" />
        <directionalLight
          position={[-5, 5, -5]}
          intensity={1}
          color="#06B6D4"
        />
        <pointLight position={[0, 0, 0]} intensity={2} color="#EC4899" />

        {/* Frequency Bars - Music Spectrum */}
        <group position={[0, -1, 0]}>
          {Array.from({ length: 32 }).map((_, i) => (
            <FrequencyBar
              key={i}
              position={[(i - 15.5) * 0.22, 0, 0]}
              index={i}
              color={i < 16 ? "#8B5CF6" : "#06B6D4"}
              emissiveColor={i < 16 ? "#EC4899" : "#8B5CF6"}
            />
          ))}
        </group>

        {/* Waveform Ring */}
        <WaveformRing />

        {/* Vinyl Record */}
        <NeonVinyl />

        {/* Pulsing Center Sphere */}
        <PulsingSphere />

        {/* Fog for atmosphere */}
        <fog attach="fog" args={["#0A0A0F", 5, 20]} />
      </Canvas>

      {/* Info Overlay */}
      <div className="absolute bottom-4 left-4 right-4 glass-card p-4 rounded-lg border border-primary/30">
        <h3 className="text-sm font-semibold text-primary mb-2">
          🎵 Music Production Visualizer
        </h3>
        <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary">
          <div>• 32-band frequency analyzer</div>
          <div>• 128-point waveform ring</div>
          <div>• Animated vinyl record</div>
          <div>• Pulsing beat indicator</div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// COMPACT AUDIO SPECTRUM - For Smaller Cards
// ============================================================================
export function AudioSpectrum() {
  return (
    <div className="relative w-full h-[300px] rounded-xl overflow-hidden glass-card">
      <Canvas
        camera={{ position: [0, 2, 6], fov: 45 }}
        className="bg-gradient-to-br from-primary/10 to-accent-cyan/10"
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[0, 5, 0]} intensity={2} color="#8B5CF6" />

        <group>
          {Array.from({ length: 24 }).map((_, i) => (
            <FrequencyBar
              key={i}
              position={[(i - 11.5) * 0.25, 0, 0]}
              index={i}
              color="#06B6D4"
              emissiveColor="#8B5CF6"
            />
          ))}
        </group>
      </Canvas>

      <div className="absolute bottom-3 left-3 right-3 glass-card p-2 rounded">
        <p className="text-xs text-accent-cyan font-semibold">
          ⚡ Real-time Audio Spectrum
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// WAVEFORM DISPLAY - Oscilloscope Style
// ============================================================================
export function WaveformDisplay() {
  return (
    <div className="relative w-full h-[300px] rounded-xl overflow-hidden glass-card">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        className="bg-gradient-to-br from-accent-pink/10 to-primary/10"
      >
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[0, 0, 5]}
          intensity={1.5}
          color="#EC4899"
        />

        <WaveformRing />
      </Canvas>

      <div className="absolute bottom-3 left-3 right-3 glass-card p-2 rounded">
        <p className="text-xs text-accent-pink font-semibold">
          🌊 Waveform Oscilloscope
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// VINYL TURNTABLE - Standalone Component
// ============================================================================
export function VinylTurntable() {
  return (
    <div className="relative w-full h-[300px] rounded-xl overflow-hidden glass-card">
      <Canvas
        camera={{ position: [0, 2, 4], fov: 50 }}
        className="bg-gradient-to-br from-bg-secondary to-bg-tertiary"
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[3, 3, 3]} intensity={1} color="#8B5CF6" />
        <directionalLight
          position={[-3, 3, -3]}
          intensity={1}
          color="#06B6D4"
        />

        <NeonVinyl />
        <PulsingSphere />
      </Canvas>

      <div className="absolute bottom-3 left-3 right-3 glass-card p-2 rounded">
        <p className="text-xs text-primary font-semibold">
          💿 Neon Vinyl Player
        </p>
      </div>
    </div>
  );
}
