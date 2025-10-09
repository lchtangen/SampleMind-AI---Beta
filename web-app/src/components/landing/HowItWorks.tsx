import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

/**
 * How It Works Section Component
 * 
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - 4-step process visualization
 * - Animated timeline with connecting lines
 * - Icon animations
 * - Scroll-triggered entrance
 * 
 * Steps:
 * 1. Upload - Import your audio files
 * 2. Analyze - AI processes your samples
 * 3. Organize - Smart tags and categorization
 * 4. Create - Start producing with insights
 */

interface StepProps {
  number: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  delay: number;
  isLast?: boolean;
}

function Step({ number, title, description, icon, delay, isLast }: StepProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  return (
    <div ref={ref} className="relative flex flex-col items-center">
      {/* Connecting Line */}
      {!isLast && (
        <motion.div
          className="hidden lg:block absolute top-20 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary via-accent-cyan to-transparent"
          initial={{ scaleX: 0, originX: 0 }}
          animate={isInView ? { scaleX: 1 } : { scaleX: 0 }}
          transition={{ delay: delay + 0.5, duration: 0.8 }}
        />
      )}

      {/* Step Content */}
      <motion.div
        className="relative z-10 flex flex-col items-center text-center max-w-xs"
        initial={{ opacity: 0, y: 50 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ delay, duration: 0.6 }}
      >
        {/* Icon Circle */}
        <motion.div
          className="w-40 h-40 rounded-full bg-gradient-purple flex items-center justify-center mb-6 shadow-glow-purple relative"
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          {/* Pulse Effect */}
          <motion.div
            className="absolute inset-0 rounded-full bg-primary opacity-30"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          
          {/* Number Badge */}
          <div className="absolute -top-2 -right-2 w-10 h-10 rounded-full bg-accent-cyan flex items-center justify-center shadow-glow-cyan">
            <span className="text-white font-bold text-lg">{number}</span>
          </div>

          {/* Icon */}
          <div className="relative z-10 text-white">
            {icon}
          </div>
        </motion.div>

        {/* Title */}
        <h3 className="text-2xl font-heading font-bold text-text-primary mb-3">
          {title}
        </h3>

        {/* Description */}
        <p className="text-text-secondary leading-relaxed">
          {description}
        </p>
      </motion.div>
    </div>
  );
}

export function HowItWorks() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  const steps = [
    {
      number: 1,
      title: 'Upload',
      description: 'Drag and drop your audio files or import entire folders. Supports all major formats.',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      ),
      delay: 0,
    },
    {
      number: 2,
      title: 'Analyze',
      description: 'Our AI processes your samples, extracting tempo, key, mood, and 30+ audio features automatically.',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      delay: 0.2,
    },
    {
      number: 3,
      title: 'Organize',
      description: 'Smart tags, categories, and collections are created automatically. Search and filter instantly.',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
      delay: 0.4,
    },
    {
      number: 4,
      title: 'Create',
      description: 'Start producing with AI-powered insights, recommendations, and tools to accelerate your workflow.',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
        </svg>
      ),
      delay: 0.6,
      isLast: true,
    },
  ];

  return (
    <section id="how-it-works" ref={ref} className="py-20 sm:py-32 bg-bg-secondary relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-gradient-to-r from-primary/5 via-accent-cyan/5 to-accent-pink/5 rounded-full blur-3xl"
          animate={{
            rotate: [0, 360],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-primary">
              Simple Process
            </span>
          </motion.div>

          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              How It Works
            </span>
          </motion.h2>

          <motion.p
            className="text-xl text-text-secondary max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Get started in minutes. Our intuitive workflow makes professional audio analysis accessible to everyone.
          </motion.p>
        </motion.div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 lg:gap-8">
          {steps.map((step, index) => (
            <Step key={index} {...step} />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ delay: 1.2, duration: 0.6 }}
        >
          <p className="text-text-secondary mb-6 text-lg">
            Ready to streamline your workflow?
          </p>
          <motion.button
            className="bg-gradient-purple px-8 py-4 rounded-lg font-semibold text-lg text-white shadow-glow-purple hover:shadow-glow-cyan transition-all duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start Your Free Trial
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
}
