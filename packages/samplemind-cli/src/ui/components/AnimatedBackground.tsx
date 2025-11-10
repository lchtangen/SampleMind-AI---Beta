import React, { useEffect, useState } from 'react';
import { Box, Text } from 'ink';

const FRAMES = [
  '🌌    ✨      ·   ✨      ·   ✨      ·   ✨',
  '✨ 🌌    ✨      ·   ✨      ·   ✨      ·',
  '·   ✨ 🌌    ✨      ·   ✨      ·   ✨',
  '✨      ·   ✨ 🌌    ✨      ·   ✨      ·',
  '·   ✨      ·   ✨ 🌌    ✨      ·   ✨'
];

interface AnimatedBackgroundProps {
  width?: number;
}

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ width = 60 }) => {
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrame((value) => (value + 1) % FRAMES.length);
    }, 180);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box width={width} justifyContent="center">
      <Text color="#1f2937">{FRAMES[frame % FRAMES.length]}</Text>
    </Box>
  );
};
