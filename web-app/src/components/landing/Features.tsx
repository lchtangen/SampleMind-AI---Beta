import { motion, useInView } from "framer-motion";
import { useRef } from "react";

/**
 * Features Section Component
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - 8 feature cards in responsive grid
 * - Hover animations with glow effects
 * - Gradient icons and text
 * - Scroll-triggered entrance animations
 *
 * Features Showcased:
 * - AI-Powered Analysis
 * - Advanced Audio Processing
 * - Multi-Platform Support
 * - Real-Time Collaboration
 * - Batch Processing
 * - Smart Tagging
 * - Flexible Export
 * - Developer API
 */

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
  delay: number;
}

function FeatureCard({
  icon,
  title,
  description,
  gradient,
  delay,
}: FeatureCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div
      ref={ref}
      className="group glass-card rounded-2xl p-8 hover:shadow-glow-purple transition-all duration-500 relative overflow-hidden"
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ delay, duration: 0.6, ease: "easeOut" }}
      whileHover={{ scale: 1.03, y: -5 }}
    >
      {/* Background Glow on Hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent-cyan/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      {/* Content */}
      <div className="relative z-10">
        {/* Icon */}
        <motion.div
          className={`w-16 h-16 rounded-xl ${gradient} flex items-center justify-center mb-6 shadow-glow-purple group-hover:shadow-glow-cyan transition-all duration-300`}
          whileHover={{ rotate: [0, -10, 10, -10, 0], scale: 1.1 }}
          transition={{ duration: 0.5 }}
        >
          {icon}
        </motion.div>

        {/* Title */}
        <h3 className="text-2xl font-heading font-bold text-text-primary mb-4 group-hover:text-transparent group-hover:bg-gradient-purple group-hover:bg-clip-text transition-all duration-300">
          {title}
        </h3>

        {/* Description */}
        <p className="text-text-secondary leading-relaxed group-hover:text-text-primary transition-colors duration-300">
          {description}
        </p>

        {/* Decorative Arrow */}
        <motion.div
          className="mt-6 flex items-center gap-2 text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          initial={{ x: -10 }}
          whileHover={{ x: 0 }}
        >
          <span className="text-sm font-semibold">Learn more</span>
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </motion.div>
      </div>
    </motion.div>
  );
}

export function Features() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const features = [
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      ),
      title: "AI-Powered Analysis",
      description:
        "Advanced machine learning models analyze your audio files to extract tempo, key, mood, genre, and 30+ other features with 99.9% accuracy.",
      gradient: "bg-gradient-purple",
      delay: 0,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
          />
        </svg>
      ),
      title: "Advanced Audio Processing",
      description:
        "Industry-leading algorithms powered by librosa, essentia, and madmom extract spectral features, harmonic content, and rhythmic patterns.",
      gradient: "bg-gradient-to-br from-accent-cyan to-accent-cyan/50",
      delay: 0.1,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
          />
        </svg>
      ),
      title: "Multi-Platform Support",
      description:
        "Access SampleMind AI from web, mobile, desktop, or directly in your DAW with FL Studio, Ableton, and Logic Pro plugins.",
      gradient: "bg-gradient-to-br from-accent-pink to-accent-pink/50",
      delay: 0.2,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      ),
      title: "Real-Time Collaboration",
      description:
        "Share projects with your team, collaborate on sample libraries, and get instant feedback with real-time syncing across all devices.",
      gradient: "bg-gradient-to-br from-primary to-accent-cyan",
      delay: 0.3,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
          />
        </svg>
      ),
      title: "Batch Processing",
      description:
        "Analyze thousands of samples simultaneously with our distributed processing engine. Perfect for large sample libraries and production workflows.",
      gradient: "bg-gradient-to-br from-accent-pink to-primary",
      delay: 0.4,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
          />
        </svg>
      ),
      title: "Smart Tagging",
      description:
        "AI automatically tags your samples with genre, mood, instruments, and custom categories. Search and filter your library instantly.",
      gradient: "bg-gradient-to-br from-accent-cyan to-primary",
      delay: 0.5,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
          />
        </svg>
      ),
      title: "Flexible Export",
      description:
        "Export analysis data in JSON, CSV, or XML formats. Integrate seamlessly with your existing workflow and third-party tools.",
      gradient: "bg-gradient-to-br from-primary to-accent-pink",
      delay: 0.6,
    },
    {
      icon: (
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
          />
        </svg>
      ),
      title: "Developer API",
      description:
        "RESTful API with comprehensive documentation. Build custom integrations, automate workflows, and extend functionality with webhooks.",
      gradient: "bg-gradient-to-br from-accent-cyan to-accent-pink",
      delay: 0.7,
    },
  ];

  return (
    <section
      id="features"
      ref={ref}
      className="py-20 sm:py-32 bg-bg-secondary relative overflow-hidden"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-cyan/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -50, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut",
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
          <motion.div
            className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={
              isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }
            }
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-primary">
              Powerful Features
            </span>
          </motion.div>

          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              Everything You Need
            </span>
            <br />
            <span className="text-text-primary">To Create Amazing Music</span>
          </motion.h2>

          <motion.p
            className="text-xl text-text-secondary max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Professional-grade tools powered by cutting-edge AI technology. From
            analysis to organization, we've got you covered.
          </motion.p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 1.5, duration: 0.8 }}
        >
          <p className="text-text-muted mb-6">
            Want to see more? Check out our{" "}
            <a
              href="#pricing"
              className="text-primary hover:text-accent-cyan transition-colors font-semibold"
            >
              pricing plans
            </a>{" "}
            or{" "}
            <a
              href="#"
              className="text-accent-cyan hover:text-accent-pink transition-colors font-semibold"
            >
              read the docs
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
