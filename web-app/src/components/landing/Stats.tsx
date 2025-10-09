import { motion, useInView } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

/**
 * Stats Section Component
 * 
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - Animated counters with gradient text
 * - Glassmorphic cards with neon glow
 * - Key metrics showcase
 * - Scroll-triggered animations
 * 
 * Metrics:
 * - 50,000+ Samples Analyzed
 * - 10,000+ Active Users
 * - 99.9% Accuracy Rate
 * - 115+ AI Technologies
 */

interface StatCardProps {
  value: number;
  suffix?: string;
  label: string;
  gradient: string;
  delay: number;
}

function StatCard({ value, suffix = '', label, gradient, delay }: StatCardProps) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  useEffect(() => {
    if (!isInView) return;

    const duration = 2000; // 2 seconds
    const steps = 60;
    const increment = value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <motion.div
      ref={ref}
      className="glass-card rounded-2xl p-8 text-center shadow-glow-purple hover:shadow-glow-cyan transition-all duration-500 group"
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ delay, duration: 0.6, ease: 'easeOut' }}
      whileHover={{ scale: 1.05, y: -5 }}
    >
      {/* Counter */}
      <motion.div
        className={`text-5xl sm:text-6xl font-bold mb-4 ${gradient} bg-clip-text text-transparent`}
        initial={{ scale: 0.5 }}
        animate={isInView ? { scale: 1 } : { scale: 0.5 }}
        transition={{ delay: delay + 0.2, duration: 0.5, ease: 'backOut' }}
      >
        {count.toLocaleString()}{suffix}
      </motion.div>

      {/* Label */}
      <p className="text-lg text-text-secondary font-medium group-hover:text-text-primary transition-colors duration-300">
        {label}
      </p>

      {/* Decorative Line */}
      <div className="mt-4 h-1 w-16 mx-auto rounded-full bg-gradient-purple opacity-50 group-hover:opacity-100 group-hover:w-24 transition-all duration-300" />
    </motion.div>
  );
}

export function Stats() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  const stats = [
    {
      value: 50000,
      suffix: '+',
      label: 'Samples Analyzed',
      gradient: 'bg-gradient-purple',
      delay: 0,
    },
    {
      value: 10000,
      suffix: '+',
      label: 'Active Users',
      gradient: 'bg-gradient-to-r from-accent-cyan to-primary',
      delay: 0.15,
    },
    {
      value: 99.9,
      suffix: '%',
      label: 'Accuracy Rate',
      gradient: 'bg-gradient-to-r from-accent-pink to-accent-cyan',
      delay: 0.3,
    },
    {
      value: 115,
      suffix: '+',
      label: 'AI Technologies',
      gradient: 'bg-gradient-to-r from-primary to-accent-pink',
      delay: 0.45,
    },
  ];

  return (
    <section ref={ref} className="py-20 sm:py-32 bg-bg-primary relative overflow-hidden">
      {/* Background Glow Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6 }}
        >
          <motion.h2
            className="text-4xl sm:text-5xl font-heading font-bold mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              Trusted by Thousands
            </span>
          </motion.h2>
          <motion.p
            className="text-xl text-text-secondary max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            Join the growing community of music producers leveraging AI-powered tools
          </motion.p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {stats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        {/* Additional Info */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 1, duration: 0.8 }}
        >
          <p className="text-text-muted">
            Processing over{' '}
            <span className="text-primary font-semibold">1M+ audio files</span>{' '}
            monthly with{' '}
            <span className="text-accent-cyan font-semibold">5 AI models</span>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
