import React from 'react';
import { motion } from 'framer-motion';

export interface HolographicTextProps {
  /**
   * Text content to display
   */
  children: React.ReactNode;
  
  /**
   * Enable/disable glitch effect on hover
   * @default true
   */
  enableGlitch?: boolean;
  
  /**
   * Animation speed in seconds
   * @default 3
   */
  speed?: number;
  
  /**
   * Text size class
   * @default 'text-4xl'
   */
  size?: string;
  
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * HTML tag to render as
   * @default 'h1'
   */
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span';
}

/**
 * HolographicText Component
 * 
 * Displays text with an animated holographic rainbow gradient effect.
 * Optionally includes glitch animation on hover for enhanced cyberpunk aesthetic.
 * 
 * @example
 * ```tsx
 * <HolographicText as="h1" enableGlitch={true}>
 *   SampleMind AI
 * </HolographicText>
 * ```
 */
export const HolographicText: React.FC<HolographicTextProps> = ({
  children,
  enableGlitch = true,
  speed = 3,
  size = 'text-4xl',
  className = '',
  as: Component = 'h1',
}) => {
  const [isGlitching, setIsGlitching] = React.useState(false);

  const holographicStyle = {
    background: 'linear-gradient(45deg, #EC4899 0%, #8B5CF6 33%, #06B6D4 66%, #EC4899 100%)',
    backgroundSize: '200% 200%',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  };

  const glitchVariants = {
    normal: {
      x: 0,
      y: 0,
      textShadow: 'none',
    },
    glitch: {
      x: [0, -2, 2, -2, 2, 0],
      y: [0, 2, -2, 2, -2, 0],
      textShadow: [
        'none',
        '2px 2px #FF0055, -2px -2px #00FFFF',
        '-2px 2px #FF0055, 2px -2px #00FFFF',
        '2px -2px #FF0055, -2px 2px #00FFFF',
        'none',
      ],
      transition: {
        duration: 0.3,
        times: [0, 0.2, 0.4, 0.6, 0.8, 1],
      },
    },
  };

  return (
    <motion.div
      className={`font-cyber ${size} ${className}`}
      style={holographicStyle}
      animate={{
        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
      }}
      transition={{
        duration: speed,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      onMouseEnter={() => enableGlitch && setIsGlitching(true)}
      onMouseLeave={() => setIsGlitching(false)}
    >
      <motion.div
        as={Component}
        variants={glitchVariants}
        animate={isGlitching ? 'glitch' : 'normal'}
      >
        {children}
      </motion.div>
    </motion.div>
  );
};

export default HolographicText;
