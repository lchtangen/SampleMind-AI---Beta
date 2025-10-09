import { motion, useInView } from 'framer-motion';
import { useRef, useState } from 'react';

/**
 * Pricing Section Component
 * 
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - 3-tier pricing (Free, Pro, Enterprise)
 * - Monthly/Annual toggle
 * - Feature comparison lists
 * - "Most Popular" badge on Pro tier
 * - Glassmorphic cards with hover effects
 * - Gradient pricing text
 * 
 * Pricing Tiers:
 * - Free: $0/month - Perfect for getting started
 * - Pro: $29/month - For professional producers
 * - Enterprise: Custom - For teams and studios
 */

interface PricingTierProps {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  popular?: boolean;
  gradient: string;
  delay: number;
}

function PricingTier({
  name,
  price,
  period,
  description,
  features,
  cta,
  popular = false,
  gradient,
  delay,
}: PricingTierProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  return (
    <motion.div
      ref={ref}
      className={`relative glass-card rounded-2xl p-8 ${
        popular ? 'border-2 border-primary shadow-glow-purple' : 'border border-primary/20'
      } hover:shadow-glow-cyan transition-all duration-500 group`}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ delay, duration: 0.6, ease: 'easeOut' }}
      whileHover={{ scale: 1.03, y: -10 }}
    >
      {/* Popular Badge */}
      {popular && (
        <motion.div
          className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-purple px-6 py-2 rounded-full shadow-glow-purple"
          initial={{ opacity: 0, scale: 0.8, y: -10 }}
          animate={isInView ? { opacity: 1, scale: 1, y: 0 } : { opacity: 0, scale: 0.8, y: -10 }}
          transition={{ delay: delay + 0.2, duration: 0.4 }}
        >
          <span className="text-white font-bold text-sm">Most Popular</span>
        </motion.div>
      )}

      {/* Tier Name */}
      <h3 className="text-2xl font-heading font-bold text-text-primary mb-2">
        {name}
      </h3>

      {/* Description */}
      <p className="text-text-secondary mb-6">
        {description}
      </p>

      {/* Price */}
      <div className="mb-8">
        <div className="flex items-baseline gap-2">
          <span className={`text-5xl font-bold ${gradient} bg-clip-text text-transparent`}>
            {price}
          </span>
          {period && (
            <span className="text-text-muted">
              / {period}
            </span>
          )}
        </div>
      </div>

      {/* CTA Button */}
      <motion.button
        className={`w-full py-4 rounded-lg font-semibold text-lg mb-8 transition-all duration-300 ${
          popular
            ? 'bg-gradient-purple text-white shadow-glow-purple hover:shadow-glow-cyan'
            : 'bg-bg-tertiary text-text-primary hover:bg-primary/20 border-2 border-primary/30'
        }`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {cta}
      </motion.button>

      {/* Features List */}
      <div className="space-y-4">
        <p className="text-sm font-semibold text-text-muted uppercase tracking-wide mb-4">
          What's Included:
        </p>
        {features.map((feature, index) => (
          <motion.div
            key={index}
            className="flex items-start gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
            transition={{ delay: delay + 0.1 * index, duration: 0.3 }}
          >
            <svg
              className="w-5 h-5 text-primary flex-shrink-0 mt-0.5"
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
            <span className="text-text-secondary group-hover:text-text-primary transition-colors">
              {feature}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export function Pricing() {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [isAnnual, setIsAnnual] = useState(false);

  const pricingTiers = [
    {
      name: 'Free',
      price: '$0',
      period: 'month',
      description: 'Perfect for getting started and exploring features',
      features: [
        '100 samples per month',
        'Basic audio analysis',
        'Standard support',
        'Web access only',
        'Public projects',
        '1 GB storage',
        'Community features',
      ],
      cta: 'Get Started Free',
      popular: false,
      gradient: 'bg-gradient-to-r from-text-primary to-text-secondary',
      delay: 0,
    },
    {
      name: 'Pro',
      price: isAnnual ? '$290' : '$29',
      period: isAnnual ? 'year' : 'month',
      description: 'For professional producers and serious creators',
      features: [
        'Unlimited samples',
        'Advanced AI analysis',
        'Priority support',
        'All platforms (Web, Mobile, DAW)',
        'Private projects',
        '100 GB storage',
        'Batch processing',
        'API access',
        'Custom tags',
        'Export to all formats',
        'Real-time collaboration',
      ],
      cta: 'Start Pro Trial',
      popular: true,
      gradient: 'bg-gradient-purple',
      delay: 0.15,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For teams, studios, and large organizations',
      features: [
        'Everything in Pro',
        'Dedicated support',
        'Custom integrations',
        'Unlimited storage',
        'Team management',
        'SSO authentication',
        'Advanced analytics',
        'SLA guarantee',
        'On-premise deployment',
        'Custom AI models',
        'White-label options',
      ],
      cta: 'Contact Sales',
      popular: false,
      gradient: 'bg-gradient-to-r from-accent-cyan to-accent-pink',
      delay: 0.3,
    },
  ];

  return (
    <section id="pricing" ref={ref} className="py-20 sm:py-32 bg-bg-primary relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-accent-cyan/5 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 15,
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
          <motion.div
            className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-primary">
              Simple Pricing
            </span>
          </motion.div>

          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <span className="bg-gradient-purple bg-clip-text text-transparent">
              Choose Your Plan
            </span>
          </motion.h2>

          <motion.p
            className="text-xl text-text-secondary max-w-3xl mx-auto mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Start free and upgrade as you grow. All plans include a 14-day free trial.
          </motion.p>

          {/* Billing Toggle */}
          <motion.div
            className="flex items-center justify-center gap-4"
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <span className={`font-semibold ${!isAnnual ? 'text-primary' : 'text-text-muted'}`}>
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className={`relative w-16 h-8 rounded-full transition-colors duration-300 ${
                isAnnual ? 'bg-gradient-purple' : 'bg-bg-tertiary'
              }`}
              aria-label="Toggle billing period"
            >
              <motion.div
                className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg"
                animate={{
                  left: isAnnual ? 'calc(100% - 28px)' : '4px',
                }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            </button>
            <span className={`font-semibold ${isAnnual ? 'text-primary' : 'text-text-muted'}`}>
              Annual
              <span className="ml-2 text-xs bg-accent-cyan/20 text-accent-cyan px-2 py-1 rounded">
                Save 17%
              </span>
            </span>
          </motion.div>
        </motion.div>

        {/* Pricing Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {pricingTiers.map((tier, index) => (
            <PricingTier key={index} {...tier} />
          ))}
        </div>

        {/* Bottom Info */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 1, duration: 0.8 }}
        >
          <p className="text-text-muted mb-4">
            All plans include 14-day free trial • No credit card required • Cancel anytime
          </p>
          <p className="text-sm text-text-muted">
            Questions? Check our{' '}
            <a href="#" className="text-primary hover:text-accent-cyan transition-colors">
              FAQ
            </a>
            {' '}or{' '}
            <a href="#" className="text-accent-cyan hover:text-accent-pink transition-colors">
              contact us
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
