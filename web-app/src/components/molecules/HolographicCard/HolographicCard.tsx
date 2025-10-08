import { FC, ReactNode } from 'react';
import { motion } from 'framer-motion';
import './HolographicCard.css';

interface HolographicCardProps {
  children: ReactNode;
  className?: string;
}

export const HolographicCard: FC<HolographicCardProps> = ({ children, className }) => {
  return (
    <motion.div
      className={`relative p-8 rounded-2xl overflow-hidden ${className}`}
      whileHover={{ scale: 1.02 }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent-cyan/20 opacity-50" />
      <div className="absolute inset-0 holographic-gradient" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
};
