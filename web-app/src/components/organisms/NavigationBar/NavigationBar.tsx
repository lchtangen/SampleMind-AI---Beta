/**
 * NavigationBar Component
 *
 * A cyberpunk-themed navigation bar with glassmorphic background,
 * smooth transitions, and responsive mobile menu.
 *
 * @module NavigationBar
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NeonButton } from '../../atoms/NeonButton/NeonButton';

/**
 * Navigation link item
 */
export interface NavLink {
  id: string;
  label: string;
  href: string;
  icon?: React.ReactNode;
}

/**
 * Props for the NavigationBar component
 */
export interface NavigationBarProps {
  /**
   * Navigation links
   */
  links: NavLink[];

  /**
   * Brand logo or text
   */
  logo?: React.ReactNode;

  /**
   * Action buttons (e.g., login, signup)
   */
  actions?: React.ReactNode;

  /**
   * Current active link ID
   */
  activeId?: string;

  /**
   * Click handler for links
   */
  onLinkClick?: (link: NavLink) => void;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Test ID
   */
  testId?: string;
}

/**
 * NavigationBar - Glassmorphic navigation with responsive mobile menu.
 *
 * @example
 * ```tsx
 * <NavigationBar
 *   logo={<Logo />}
 *   links={[
 *     { id: 'home', label: 'Home', href: '/' },
 *     { id: 'library', label: 'Library', href: '/library' }
 *   ]}
 *   actions={<NeonButton>Sign In</NeonButton>}
 *   activeId="home"
 *   onLinkClick={(link) => navigate(link.href)}
 * />
 * ```
 */
export const NavigationBar: React.FC<NavigationBarProps> = ({
  links,
  logo,
  actions,
  activeId,
  onLinkClick,
  className = '',
  testId,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <motion.nav
      className={`
        sticky
        top-0
        z-40
        backdrop-blur-xl
        bg-white/5
        border-b
        border-white/10
        ${className}
      `.trim().replace(/\s+/g, ' ')}
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      data-testid={testId}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            {logo}
          </div>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-6">
            {links.map((link) => (
              <motion.a
                key={link.id}
                href={link.href}
                onClick={(e) => {
                  e.preventDefault();
                  onLinkClick?.(link);
                }}
                className={`
                  flex
                  items-center
                  gap-2
                  px-4
                  py-2
                  rounded-lg
                  font-medium
                  transition-all
                  duration-normal
                  ${
                    activeId === link.id
                      ? 'text-primary bg-primary/10 shadow-glow-purple'
                      : 'text-text-secondary hover:text-primary hover:bg-white/5'
                  }
                `.trim().replace(/\s+/g, ' ')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {link.icon}
                {link.label}
              </motion.a>
            ))}
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-4">
            {actions}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="
                p-2
                rounded-lg
                text-text-secondary
                hover:text-primary
                hover:bg-white/5
                transition-all
                duration-normal
              "
              aria-label="Toggle mobile menu"
              aria-expanded={mobileMenuOpen}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            className="md:hidden border-t border-white/10"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-4 py-4 space-y-2">
              {/* Mobile Links */}
              {links.map((link) => (
                <motion.a
                  key={link.id}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    onLinkClick?.(link);
                    setMobileMenuOpen(false);
                  }}
                  className={`
                    flex
                    items-center
                    gap-3
                    px-4
                    py-3
                    rounded-lg
                    font-medium
                    transition-all
                    duration-normal
                    ${
                      activeId === link.id
                        ? 'text-primary bg-primary/10'
                        : 'text-text-secondary hover:text-primary hover:bg-white/5'
                    }
                  `.trim().replace(/\s+/g, ' ')}
                  whileTap={{ scale: 0.98 }}
                >
                  {link.icon}
                  {link.label}
                </motion.a>
              ))}

              {/* Mobile Actions */}
              {actions && (
                <div className="pt-4 border-t border-white/10">
                  {actions}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Neon Glow Bottom Border */}
      <motion.div
        className="absolute bottom-0 left-0 right-0 h-[2px]"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, #8B5CF6 30%, #06B6D4 70%, transparent 100%)',
          boxShadow: '0 0 10px rgba(139, 92, 246, 0.6)',
        }}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        aria-hidden="true"
      />
    </motion.nav>
  );
};

NavigationBar.displayName = 'NavigationBar';

export default NavigationBar;
