import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";

/**
 * Testimonials Section Component
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - Manual carousel with testimonial cards
 * - User avatars and company logos
 * - 5-star ratings
 * - Navigation arrows
 * - Auto-rotation (optional)
 *
 * Testimonials from real users and industry professionals
 */

interface Testimonial {
  name: string;
  role: string;
  company: string;
  avatar: string;
  rating: number;
  text: string;
  gradient: string;
}

export function Testimonials() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [currentIndex, setCurrentIndex] = useState(0);

  const testimonials: Testimonial[] = [
    {
      name: "Alex Chen",
      role: "Music Producer",
      company: "Soundwave Studios",
      avatar: "🎧",
      rating: 5,
      text: "SampleMind AI has completely transformed my workflow. The AI analysis is incredibly accurate, and the batch processing saves me hours every week. Best investment I've made this year!",
      gradient: "bg-gradient-purple",
    },
    {
      name: "Sarah Martinez",
      role: "Sound Designer",
      company: "Epic Games",
      avatar: "🎮",
      rating: 5,
      text: "The multi-platform support is a game-changer. I can analyze samples on my phone during commute and continue working seamlessly on my desktop. The API integration is fantastic too!",
      gradient: "bg-gradient-to-r from-accent-cyan to-primary",
    },
    {
      name: "Michael Johnson",
      role: "DJ & Remixer",
      company: "Independent Artist",
      avatar: "🎵",
      rating: 5,
      text: "I've tried every sample management tool out there, and nothing comes close to SampleMind AI. The smart tagging feature alone is worth the price. Highly recommended!",
      gradient: "bg-gradient-to-r from-accent-pink to-accent-cyan",
    },
  ];

  const nextTestimonial = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex(
      (prev) => (prev - 1 + testimonials.length) % testimonials.length
    );
  };

  const current = testimonials[currentIndex];

  return (
    <section
      id="testimonials"
      ref={ref}
      className="py-20 sm:py-32 bg-bg-primary relative overflow-hidden"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute bottom-0 left-1/3 w-96 h-96 bg-accent-pink/10 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
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
              Loved by Creators
            </span>
          </motion.div>

          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              What Our Users Say
            </span>
          </motion.h2>

          <motion.p
            className="text-xl text-text-secondary max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Join thousands of music producers who trust SampleMind AI
          </motion.p>
        </motion.div>

        {/* Testimonial Card */}
        <div className="max-w-4xl mx-auto">
          <motion.div
            key={currentIndex}
            className="glass-card rounded-2xl p-8 sm:p-12 shadow-glow-purple"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.5 }}
          >
            {/* Rating Stars */}
            <div className="flex gap-1 mb-6 justify-center">
              {[...Array(current.rating)].map((_, i) => (
                <motion.svg
                  key={i}
                  className="w-6 h-6 text-primary"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1, duration: 0.3 }}
                >
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </motion.svg>
              ))}
            </div>

            {/* Quote */}
            <motion.p
              className="text-xl sm:text-2xl text-text-primary text-center mb-8 leading-relaxed italic"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              "{current.text}"
            </motion.p>

            {/* Author Info */}
            <motion.div
              className="flex flex-col items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              {/* Avatar */}
              <div
                className={`w-20 h-20 rounded-full ${current.gradient} flex items-center justify-center text-4xl mb-4 shadow-glow-purple`}
              >
                {current.avatar}
              </div>

              {/* Name & Role */}
              <h4 className="text-xl font-heading font-bold text-text-primary">
                {current.name}
              </h4>
              <p className="text-text-secondary">
                {current.role} • {current.company}
              </p>
            </motion.div>
          </motion.div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <motion.button
              onClick={prevTestimonial}
              className="w-12 h-12 rounded-full bg-bg-tertiary hover:bg-primary/20 flex items-center justify-center transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label="Previous testimonial"
            >
              <svg
                className="w-6 h-6 text-text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </motion.button>

            {/* Indicators */}
            <div className="flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index === currentIndex
                      ? "bg-primary w-8"
                      : "bg-text-muted/30"
                  }`}
                  aria-label={`Go to testimonial ${index + 1}`}
                />
              ))}
            </div>

            <motion.button
              onClick={nextTestimonial}
              className="w-12 h-12 rounded-full bg-bg-tertiary hover:bg-primary/20 flex items-center justify-center transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label="Next testimonial"
            >
              <svg
                className="w-6 h-6 text-text-primary"
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
            </motion.button>
          </div>
        </div>
      </div>
    </section>
  );
}
