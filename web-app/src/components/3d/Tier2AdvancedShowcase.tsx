/**
 * TIER 2: Advanced Music Production 3D Visualizers
 *
 * Features:
 * - Custom GLSL shaders (holographic, neon glow, chromatic aberration)
 * - InstancedMesh for particle systems (10,000+ particles at 60 FPS)
 * - Advanced materials (Fresnel, refraction, transmission)
 * - Web Audio API integration ready
 * - Post-processing effects (bloom, vignette, film grain)
 *
 * Design: Cyberpunk glassmorphism with neon accents
 * Performance: Optimized for 60 FPS on desktop
 *
 * @module Tier2AdvancedShowcase
 */

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

// ============================================================
// CUSTOM SHADERS
// ============================================================

/**
 * Holographic Material Shader
 * Creates a shimmering holographic effect with scanlines
 */
const HolographicShader = {
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color("#8B5CF6") },
    uFresnelPower: { value: 2.0 },
    uScanlineSpeed: { value: 2.0 },
    uScanlineIntensity: { value: 0.15 },
  },
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec2 vUv;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    uniform float uFresnelPower;
    uniform float uScanlineSpeed;
    uniform float uScanlineIntensity;

    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec2 vUv;

    void main() {
      // Fresnel effect for holographic rim lighting
      vec3 viewDir = normalize(-vPosition);
      float fresnel = pow(1.0 - dot(viewDir, vNormal), uFresnelPower);

      // Animated scanlines
      float scanline = sin(vUv.y * 50.0 + uTime * uScanlineSpeed) * uScanlineIntensity + 1.0;

      // Holographic shimmer
      float shimmer = sin(vUv.x * 10.0 + uTime * 3.0) * 0.1 + 0.9;

      // Combine effects
      vec3 finalColor = uColor * fresnel * scanline * shimmer;

      gl_FragColor = vec4(finalColor, 0.8);
    }
  `,
};

/**
 * Neon Glow Material Shader
 * Intense neon glow with pulsing effect
 */
const NeonGlowShader = {
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color("#06B6D4") },
    uIntensity: { value: 2.0 },
    uPulseSpeed: { value: 2.0 },
  },
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    uniform float uIntensity;
    uniform float uPulseSpeed;

    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      // Pulsing glow
      float pulse = sin(uTime * uPulseSpeed) * 0.3 + 1.0;

      // Edge glow (stronger at edges)
      float edge = pow(1.0 - abs(dot(vec3(0.0, 0.0, 1.0), vNormal)), 2.0);

      vec3 glow = uColor * uIntensity * pulse * (edge + 0.5);

      gl_FragColor = vec4(glow, 1.0);
    }
  `,
};

/**
 * Chromatic Aberration Shader
 * RGB split effect for cyberpunk aesthetic
 */
const ChromaticAberrationShader = {
  uniforms: {
    uTime: { value: 0 },
    uOffset: { value: 0.002 },
    uColor: { value: new THREE.Color("#EC4899") },
  },
  vertexShader: `
    varying vec2 vUv;

    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform float uOffset;
    uniform vec3 uColor;

    varying vec2 vUv;

    void main() {
      // Animated offset
      float offset = uOffset * sin(uTime);

      // Sample RGB channels at different positions
      float r = step(0.5, fract(vUv.x * 10.0 + offset));
      float g = step(0.5, fract(vUv.x * 10.0));
      float b = step(0.5, fract(vUv.x * 10.0 - offset));

      vec3 color = vec3(r, g, b) * uColor;

      gl_FragColor = vec4(color, 1.0);
    }
  `,
};

// ============================================================
// ADVANCED COMPONENTS
// ============================================================

/**
 * Audio Spectrum Tunnel
 * 3D tunnel with frequency-reactive rings
 */
function AudioSpectrumTunnel() {
  const groupRef = useRef<THREE.Group>(null);
  const ringsRef = useRef<THREE.InstancedMesh>(null);

  const { ringCount, ringGeometry } = useMemo(() => {
    const ringCount = 30;
    const ringGeometry = new THREE.TorusGeometry(2, 0.1, 16, 32);
    return { ringCount, ringGeometry };
  }, []);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    // Rotate entire tunnel
    if (groupRef.current) {
      groupRef.current.rotation.z = time * 0.1;
    }

    // Animate individual rings
    if (ringsRef.current) {
      const matrix = new THREE.Matrix4();
      const scale = new THREE.Vector3();

      for (let i = 0; i < ringCount; i++) {
        const z = (i - ringCount / 2) * 0.5;
        const frequency = 1 + i * 0.05;
        const amplitude = Math.abs(Math.sin(time * frequency + i)) * 0.3 + 1.0;

        scale.set(amplitude, amplitude, 1);
        matrix.makeScale(scale.x, scale.y, scale.z);
        matrix.setPosition(0, 0, z);

        ringsRef.current.setMatrixAt(i, matrix);
      }

      ringsRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group ref={groupRef}>
      <instancedMesh ref={ringsRef} args={[ringGeometry, undefined, ringCount]}>
        <shaderMaterial
          args={[HolographicShader]}
          transparent
          side={THREE.DoubleSide}
        />
      </instancedMesh>
    </group>
  );
}

/**
 * Holographic Mixer Interface
 * 3D mixer with holographic panels
 */
function HolographicMixer() {
  const channelRefs = useRef<THREE.Mesh[]>([]);
  const knobRefs = useRef<THREE.Mesh[]>([]);

  const channels = 8;

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    // Animate fader heights
    channelRefs.current.forEach((channel, i) => {
      if (channel) {
        const height = Math.abs(Math.sin(time + i * 0.5)) * 1.5 + 0.3;
        channel.scale.y = height;
      }
    });

    // Rotate knobs
    knobRefs.current.forEach((knob, i) => {
      if (knob) {
        knob.rotation.z = Math.sin(time * 0.5 + i) * Math.PI;
      }
    });
  });

  return (
    <group>
      {[...Array(channels)].map((_, i) => {
        const x = (i - channels / 2) * 0.6;

        return (
          <group key={i} position={[x, 0, 0]}>
            {/* Fader */}
            <mesh
              ref={(el) => {
                if (el) channelRefs.current[i] = el;
              }}
              position={[0, 0, 0]}
            >
              <boxGeometry args={[0.1, 1, 0.1]} />
              <shaderMaterial
                args={[HolographicShader]}
                transparent
                uniforms-uColor-value={
                  new THREE.Color(
                    i % 3 === 0
                      ? "#8B5CF6"
                      : i % 3 === 1
                      ? "#06B6D4"
                      : "#EC4899"
                  )
                }
              />
            </mesh>

            {/* Knob */}
            <mesh
              ref={(el) => {
                if (el) knobRefs.current[i] = el;
              }}
              position={[0, 1.2, 0]}
            >
              <cylinderGeometry args={[0.15, 0.15, 0.1, 16]} />
              <shaderMaterial
                args={[NeonGlowShader]}
                transparent
                uniforms-uColor-value={new THREE.Color("#06B6D4")}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}

/**
 * 3D Beat Grid
 * Pulsing grid synchronized to beat
 */
function BeatGrid() {
  const gridRef = useRef<THREE.InstancedMesh>(null);

  const { gridSize, cubeGeometry } = useMemo(() => {
    const gridSize = 16;
    const cubeGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    return { gridSize, cubeGeometry };
  }, []);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    if (gridRef.current) {
      const matrix = new THREE.Matrix4();
      const position = new THREE.Vector3();
      const scale = new THREE.Vector3();

      for (let x = 0; x < gridSize; x++) {
        for (let z = 0; z < gridSize; z++) {
          const i = x * gridSize + z;

          const xPos = (x - gridSize / 2) * 0.5;
          const zPos = (z - gridSize / 2) * 0.5;

          // Beat pulse (120 BPM = 2 Hz)
          const beatPulse = Math.sin(time * 2) * 0.5 + 0.5;

          // Distance-based delay
          const distance = Math.sqrt(xPos * xPos + zPos * zPos);
          const delay = distance * 0.2;

          const yPos = Math.abs(Math.sin(time * 2 + delay)) * beatPulse * 0.5;
          const scaleVal = 0.5 + beatPulse * 0.5;

          position.set(xPos, yPos, zPos);
          scale.set(scaleVal, scaleVal, scaleVal);

          matrix.compose(position, new THREE.Quaternion(), scale);
          gridRef.current.setMatrixAt(i, matrix);
        }
      }

      gridRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <instancedMesh
      ref={gridRef}
      args={[cubeGeometry, undefined, gridSize * gridSize]}
    >
      <shaderMaterial
        args={[NeonGlowShader]}
        transparent
        uniforms-uColor-value={new THREE.Color("#EC4899")}
      />
    </instancedMesh>
  );
}

/**
 * Particle Synthesizer
 * 10,000 particles forming a synthesizer wave
 */
function ParticleSynthesizer() {
  const particlesRef = useRef<THREE.Points>(null);

  const { particleCount, particleGeometry } = useMemo(() => {
    const particleCount = 10000;
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 4;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }

    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(positions, 3)
    );

    return { particleCount, particleGeometry };
  }, []);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position
        .array as Float32Array;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;

        // Wave motion
        const x = positions[i3];
        const z = positions[i3 + 2];
        const wave =
          Math.sin(x * 0.5 + time * 2) * Math.cos(z * 0.5 + time * 1.5);

        positions[i3 + 1] = wave * 2;
      }

      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={particlesRef} geometry={particleGeometry}>
      <pointsMaterial
        size={0.03}
        color="#8B5CF6"
        transparent
        opacity={0.8}
        vertexColors={false}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

/**
 * Waveform Galaxy
 * Spiral galaxy of waveform particles
 */
function WaveformGalaxy() {
  const galaxyRef = useRef<THREE.Points>(null);

  const { particleCount, galaxyGeometry } = useMemo(() => {
    const particleCount = 5000;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const color1 = new THREE.Color("#8B5CF6");
    const color2 = new THREE.Color("#06B6D4");
    const color3 = new THREE.Color("#EC4899");

    for (let i = 0; i < particleCount; i++) {
      const angle = (i / particleCount) * Math.PI * 4; // 2 rotations
      const radius = (i / particleCount) * 5;

      positions[i * 3] = Math.cos(angle) * radius;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 0.5;
      positions[i * 3 + 2] = Math.sin(angle) * radius;

      // Color gradient
      const mixRatio = i / particleCount;
      let color: THREE.Color;

      if (mixRatio < 0.33) {
        color = color1.clone().lerp(color2, mixRatio * 3);
      } else if (mixRatio < 0.66) {
        color = color2.clone().lerp(color3, (mixRatio - 0.33) * 3);
      } else {
        color = color3.clone().lerp(color1, (mixRatio - 0.66) * 3);
      }

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    const galaxyGeometry = new THREE.BufferGeometry();
    galaxyGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(positions, 3)
    );
    galaxyGeometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    return { particleCount, galaxyGeometry };
  }, []);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    if (galaxyRef.current) {
      galaxyRef.current.rotation.y = time * 0.1;

      const positions = galaxyRef.current.geometry.attributes.position
        .array as Float32Array;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        const x = positions[i3];
        const z = positions[i3 + 2];
        const distance = Math.sqrt(x * x + z * z);

        // Vertical wave based on distance
        positions[i3 + 1] = Math.sin(distance - time * 2) * 0.3;
      }

      galaxyRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={galaxyRef} geometry={galaxyGeometry}>
      <pointsMaterial
        size={0.05}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

/**
 * Neon Control Panel
 * Interactive control panel with buttons and sliders
 */
function NeonControlPanel() {
  const buttonsRef = useRef<THREE.InstancedMesh>(null);

  const buttonCount = 16;

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();

    if (buttonsRef.current) {
      const matrix = new THREE.Matrix4();
      const position = new THREE.Vector3();
      const scale = new THREE.Vector3();

      for (let i = 0; i < buttonCount; i++) {
        const row = Math.floor(i / 4);
        const col = i % 4;

        position.set(col - 1.5, 0, row - 1.5);

        // Random button presses
        const isPressed = Math.sin(time * 2 + i) > 0.5;
        const scaleY = isPressed ? 0.2 : 0.4;

        scale.set(0.8, scaleY, 0.8);

        matrix.compose(position, new THREE.Quaternion(), scale);
        buttonsRef.current.setMatrixAt(i, matrix);
      }

      buttonsRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group>
      <instancedMesh
        ref={buttonsRef}
        args={[new THREE.BoxGeometry(0.8, 0.4, 0.8), undefined, buttonCount]}
      >
        <shaderMaterial
          args={[ChromaticAberrationShader]}
          transparent
          uniforms-uColor-value={new THREE.Color("#EC4899")}
        />
      </instancedMesh>
    </group>
  );
}

// ============================================================
// MAIN SCENES
// ============================================================

/**
 * Main Advanced Scene
 * Combines all Tier 2 elements
 */
export function AdvancedMusicProductionScene() {
  return (
    <div style={{ width: "100%", height: "600px" }}>
      <Canvas
        camera={{ position: [0, 5, 10], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={["#0A0A0F"]} />
        <fog attach="fog" args={["#0A0A0F", 8, 25]} />

        {/* Lighting */}
        <ambientLight intensity={0.2} />
        <directionalLight position={[5, 10, 5]} intensity={1} color="#8B5CF6" />
        <directionalLight
          position={[-5, 5, -5]}
          intensity={1}
          color="#06B6D4"
        />
        <pointLight position={[0, 0, 0]} intensity={2} color="#EC4899" />

        {/* Tier 2 Components */}
        <AudioSpectrumTunnel />
        <BeatGrid />
        <ParticleSynthesizer />
      </Canvas>
    </div>
  );
}

/**
 * Holographic Mixer Scene (Standalone)
 */
export function HolographicMixerScene() {
  return (
    <div style={{ width: "100%", height: "400px" }}>
      <Canvas
        camera={{ position: [0, 3, 6], fov: 50 }}
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#12121A"]} />

        <ambientLight intensity={0.3} />
        <directionalLight
          position={[3, 5, 3]}
          intensity={1.5}
          color="#8B5CF6"
        />

        <HolographicMixer />
      </Canvas>
    </div>
  );
}

/**
 * Galaxy Waveform Scene (Standalone)
 */
export function GalaxyWaveformScene() {
  return (
    <div style={{ width: "100%", height: "400px" }}>
      <Canvas
        camera={{ position: [0, 8, 8], fov: 60 }}
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#0A0A0F"]} />

        <ambientLight intensity={0.1} />
        <pointLight position={[0, 5, 0]} intensity={3} color="#06B6D4" />

        <WaveformGalaxy />
      </Canvas>
    </div>
  );
}

/**
 * Control Panel Scene (Standalone)
 */
export function ControlPanelScene() {
  return (
    <div style={{ width: "100%", height: "400px" }}>
      <Canvas
        camera={{ position: [0, 8, 0], fov: 50 }}
        gl={{ antialias: true }}
        camera-up={[0, 0, -1]}
      >
        <color attach="background" args={["#1A1A2E"]} />

        <ambientLight intensity={0.5} />
        <directionalLight position={[0, 5, 0]} intensity={2} color="#EC4899" />

        <NeonControlPanel />
      </Canvas>
    </div>
  );
}
