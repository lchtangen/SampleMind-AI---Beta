import { motion } from 'framer-motion';
import { designTokens } from '@/design-system/tokens';

/**
 * Hero Component - Landing Page Main Section
 * 
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - Animated gradient background
 * - Glassmorphic card with neon glow
 * - Gradient text effects
 * - Animated CTA buttons
 * - Audio waveform visualization (placeholder)
 * 
 * Responsive: Mobile-first, adapts to tablet/desktop
 */
export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-bg-primary">
      {/* Animated Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-bg-primary to-accent-cyan/20">
        <motion.div
          className="absolute inset-0 bg-gradient-to-tr from-accent-pink/10 via-transparent to-primary/10"
          animate={{
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      {/* Floating Particles (Optional Enhancement) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="glass-card rounded-2xl p-8 sm:p-12 lg:p-16 max-w-5xl mx-auto shadow-glow-purple"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          {/* Badge */}
          <motion.div
            className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-primary">
              v2.0.0 Phoenix Beta - AI-Powered Music Production
            </span>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            className="font-heading text-4xl sm:text-5xl lg:text-7xl font-bold mb-6 leading-tight"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              Intelligent Music
            </span>
            <br />
            <span className="text-text-primary">
              Production Platform
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            className="text-xl sm:text-2xl text-text-secondary mb-8 max-w-3xl"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.8 }}
          >
            Analyze, organize, and create music with cutting-edge AI.
            Multi-model intelligence powered by{' '}
            <span className="text-primary font-semibold">Gemini 2.5 Pro</span>,{' '}
            <span className="text-accent-cyan font-semibold">Claude Sonnet 4.5</span>, and{' '}
            <span className="text-accent-pink font-semibold">GPT-5</span>.
          </motion.p>

          {/* Feature Highlights */}
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-purple flex items-center justify-center shadow-glow-purple">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-text-primary">Audio Analysis</p>
                <p className="text-sm text-text-muted">30+ features extracted</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-cyan/50 flex items-center justify-center shadow-glow-cyan">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-text-primary">AI-Powered</p>
                <p className="text-sm text-text-muted">Multi-model intelligence</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-pink to-accent-pink/50 flex items-center justify-center shadow-glow-pink">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-text-primary">Multi-Platform</p>
                <p className="text-sm text-text-muted">Web, Mobile, DAW</p>
              </div>
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-4"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.8 }}
          >
            {/* Primary CTA */}
            <motion.button
              className="group relative bg-gradient-purple px-8 py-4 rounded-lg font-semibold text-lg shadow-glow-purple hover:shadow-glow-cyan transition-all duration-300 overflow-hidden"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="relative z-10 text-white">Get Started Free</span>
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-accent-cyan to-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                initial={false}
              />
            </motion.button>

            {/* Secondary CTA */}
            <motion.button
              className="group relative bg-bg-tertiary hover:bg-bg-secondary px-8 py-4 rounded-lg font-semibold text-lg border-2 border-primary/30 hover:border-primary transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="text-text-primary flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Watch Demo
              </span>
            </motion.button>

            {/* GitHub Star Button */}
            <motion.a
              href="https://github.com/lchtangen/SampleMind-AI---Beta"
              target="_blank"
              rel="noopener noreferrer"
              className="group relative bg-bg-tertiary hover:bg-bg-secondary px-6 py-4 rounded-lg font-semibold text-lg border-2 border-text-muted/20 hover:border-text-muted transition-all duration-300 flex items-center gap-2 justify-center"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-5 h-5 text-text-secondary" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
              <span className="text-text-secondary">Star on GitHub</span>
            </motion.a>
          </motion.div>

          {/* Stats */}
          <motion.div
            className="mt-12 pt-8 border-t border-text-muted/10 grid grid-cols-2 sm:grid-cols-4 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.3, duration: 0.8 }}
          >
            <div className="text-center">
              <p className="text-3xl font-bold bg-gradient-purple bg-clip-text text-transparent">115+</p>
              <p className="text-sm text-text-muted mt-1">AI Technologies</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold bg-gradient-to-r from-accent-cyan to-primary bg-clip-text text-transparent">30+</p>
              <p className="text-sm text-text-muted mt-1">Audio Features</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold bg-gradient-to-r from-accent-pink to-accent-cyan bg-clip-text text-transparent">5</p>
              <p className="text-sm text-text-muted mt-1">AI Models</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-text-primary">100%</p>
              <p className="text-sm text-text-muted mt-1">Open Source</p>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
        animate={{
          y: [0, 10, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <div className="w-6 h-10 border-2 border-primary/50 rounded-full flex items-start justify-center p-2">
          <motion.div
            className="w-1 h-2 bg-primary rounded-full"
            animate={{
              y: [0, 12, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </div>
      </motion.div>
    </section>
  );
}
