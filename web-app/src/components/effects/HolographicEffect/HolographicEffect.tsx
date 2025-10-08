import React from 'react';
import { motion } from 'framer-motion';

interface HolographicEffectProps {
  children: React.ReactNode;
  className?: string;
}

export const HolographicEffect: React.FC<HolographicEffectProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`relative overflow-hidden rounded-lg ${className}`}>
      <motion.div
        className="absolute inset-0 holographic"
        animate={{
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        }}
        transition={{
          duration: 5,
          ease: 'linear',
          repeat: Infinity,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};
