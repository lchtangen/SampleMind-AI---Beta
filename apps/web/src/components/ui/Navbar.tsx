/**
 * GLASS NAVBAR COMPONENT
 * Sticky navbar with blur-on-scroll effect
 */

import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { cn } from '@/lib/utils';

interface NavbarProps {
  children: React.ReactNode;
  className?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ children, className }) => {
  const { scrollY } = useScroll();
  const [isScrolled, setIsScrolled] = React.useState(false);

  React.useEffect(() => {
    return scrollY.on('change', (latest) => {
      setIsScrolled(latest > 50);
    });
  }, [scrollY]);

  const backdropBlur = useTransform(
    scrollY,
    [0, 50],
    ['blur(0px)', 'blur(10px)']
  );

  const opacity = useTransform(
    scrollY,
    [0, 50],
    [0, 1]
  );

  return (
    <motion.nav
      className={cn(
        'fixed top-0 left-0 right-0 z-[1200]',
        'transition-all duration-normal',
        className
      )}
      style={{ backdropFilter: backdropBlur }}
    >
      <motion.div
        className="absolute inset-0 bg-dark-500/80"
        style={{ opacity }}
      />
      
      <div className={cn(
        'relative border-b transition-colors duration-normal',
        isScrolled ? 'border-glass-border' : 'border-transparent'
      )}>
        <div className="container-glass">
          <div className="flex items-center justify-between h-16">
            {children}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};
