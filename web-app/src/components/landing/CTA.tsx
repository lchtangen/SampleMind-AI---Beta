import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";

/**
 * CTA (Call-to-Action) Section Component
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - Eye-catching gradient background
 * - Email signup form
 * - Large headline with gradient text
 * - Feature highlights
 * - Primary CTA button
 * - Trust indicators
 *
 * Purpose: Final conversion point before footer
 */

export function CTA() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle email signup
    console.log("Email signup:", email);
    setEmail("");
  };

  return (
    <section
      id="cta"
      ref={ref}
      className="py-20 sm:py-32 bg-bg-secondary relative overflow-hidden"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-primary/20 via-accent-cyan/10 to-accent-pink/20"
          animate={{
            backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
        />

        {/* Floating Orbs */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-accent-cyan/20 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          className="max-w-5xl mx-auto glass-card rounded-3xl p-8 sm:p-12 lg:p-16 shadow-glow-purple"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={
            isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }
          }
          transition={{ duration: 0.8 }}
        >
          {/* Headline */}
          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-center mb-6"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              Ready to Transform
            </span>
            <br />
            <span className="text-text-primary">Your Music Production?</span>
          </motion.h2>

          {/* Subheadline */}
          <motion.p
            className="text-xl sm:text-2xl text-text-secondary text-center mb-12 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            Join 10,000+ producers already using AI to create better music
            faster
          </motion.p>

          {/* Feature Highlights */}
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-12"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <div className="flex items-center gap-3 justify-center sm:justify-start">
              <svg
                className="w-6 h-6 text-primary flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-text-primary font-semibold">
                14-day free trial
              </span>
            </div>
            <div className="flex items-center gap-3 justify-center sm:justify-start">
              <svg
                className="w-6 h-6 text-primary flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-text-primary font-semibold">
                No credit card required
              </span>
            </div>
            <div className="flex items-center gap-3 justify-center sm:justify-start">
              <svg
                className="w-6 h-6 text-primary flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-text-primary font-semibold">
                Cancel anytime
              </span>
            </div>
          </motion.div>

          {/* Email Signup Form */}
          <motion.form
            onSubmit={handleSubmit}
            className="max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Email Input */}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                required
                className="flex-1 px-6 py-4 rounded-lg bg-bg-tertiary border-2 border-primary/30 text-text-primary placeholder-text-muted focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />

              {/* Submit Button */}
              <motion.button
                type="submit"
                className="px-8 py-4 bg-gradient-purple rounded-lg font-semibold text-lg text-white shadow-glow-purple hover:shadow-glow-cyan transition-all duration-300 whitespace-nowrap"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Get Started Free
              </motion.button>
            </div>

            {/* Privacy Note */}
            <p className="text-sm text-text-muted text-center mt-4">
              By signing up, you agree to our{" "}
              <a
                href="#"
                className="text-primary hover:text-accent-cyan transition-colors"
              >
                Terms of Service
              </a>{" "}
              and{" "}
              <a
                href="#"
                className="text-primary hover:text-accent-cyan transition-colors"
              >
                Privacy Policy
              </a>
            </p>
          </motion.form>

          {/* Trust Indicators */}
          <motion.div
            className="mt-12 pt-8 border-t border-primary/10"
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            <div className="flex flex-wrap items-center justify-center gap-8 text-text-muted text-sm">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-primary"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>SSL Secure</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-primary"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>GDPR Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-primary"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>99.9% Uptime SLA</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
