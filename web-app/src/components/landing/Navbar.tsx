import { motion } from "framer-motion";
import { useState, useEffect } from "react";

/**
 * Navbar Component - Landing Page Header with Smooth Scroll
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Features:
 * - Logo with neon glow effect
 * - Smooth scroll navigation with active section highlighting
 * - Desktop navigation links (Features, How It Works, Pricing, Testimonials)
 * - CTA buttons (Sign In, Get Started)
 * - Mobile hamburger menu
 * - Sticky positioning with glassmorphic background
 *
 * Responsive: Mobile hamburger menu → Desktop inline navigation
 */
export function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("");

  const navLinks = [
    { name: "Features", href: "#features" },
    { name: "How It Works", href: "#how-it-works" },
    { name: "Pricing", href: "#pricing" },
    { name: "Testimonials", href: "#testimonials" },
  ];

  // Smooth scroll handler
  const handleSmoothScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    
    const targetId = href.replace("#", "");
    const targetElement = document.getElementById(targetId);
    
    if (targetElement) {
      const navbarHeight = 80; // Navbar height offset
      const targetPosition = targetElement.offsetTop - navbarHeight;
      
      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      });
      
      // Update URL without page jump
      window.history.pushState(null, "", href);
      
      // Close mobile menu after navigation
      setIsMobileMenuOpen(false);
    }
  };

  // Track active section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const sections = navLinks.map((link) => link.href.replace("#", ""));
      const scrollPosition = window.scrollY + 100; // Offset for navbar

      for (const sectionId of sections) {
        const section = document.getElementById(sectionId);
        if (section) {
          const sectionTop = section.offsetTop;
          const sectionBottom = sectionTop + section.offsetHeight;

          if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
            setActiveSection(`#${sectionId}`);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Initial check

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isLinkActive = (href: string) => activeSection === href;

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-primary/20"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo */}
          <motion.a
            href="/"
            className="flex items-center gap-3 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {/* Logo Icon with Glow */}
            <div className="relative">
              <div className="absolute inset-0 bg-primary/50 blur-xl rounded-full group-hover:bg-accent-cyan/50 transition-colors duration-300" />
              <div className="relative w-10 h-10 sm:w-12 sm:h-12 bg-gradient-purple rounded-xl flex items-center justify-center shadow-glow-purple group-hover:shadow-glow-cyan transition-all duration-300">
                <svg
                  className="w-6 h-6 sm:w-7 sm:h-7 text-white"
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
              </div>
            </div>

            {/* Logo Text */}
            <div className="hidden sm:block">
              <h1 className="font-heading text-xl font-bold">
                <span className="bg-gradient-purple bg-clip-text text-transparent">
                  SampleMind
                </span>
                <span className="text-text-primary"> AI</span>
              </h1>
              <p className="text-xs text-text-muted -mt-1">Phoenix Beta</p>
            </div>
          </motion.a>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-8">
            {navLinks.map((link, index) => (
              <motion.a
                key={link.name}
                href={link.href}
                onClick={(e) => handleSmoothScroll(e, link.href)}
                className={`font-medium transition-colors duration-200 relative group ${
                  isLinkActive(link.href)
                    ? "text-primary"
                    : "text-text-secondary hover:text-primary"
                }`}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.4 }}
              >
                {link.name}
                <span
                  className={`absolute bottom-0 left-0 h-0.5 bg-gradient-purple transition-all duration-300 ${
                    isLinkActive(link.href) ? "w-full" : "w-0 group-hover:w-full"
                  }`}
                />
              </motion.a>
            ))}
          </div>

          {/* Desktop CTA Buttons */}
          <div className="hidden md:flex items-center gap-4">
            {/* Sign In Button */}
            <motion.button
              className="px-6 py-2 rounded-lg font-semibold text-text-primary hover:bg-bg-tertiary transition-all duration-200"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.4 }}
            >
              Sign In
            </motion.button>

            {/* Get Started Button */}
            <motion.button
              className="px-6 py-2 bg-gradient-purple rounded-lg font-semibold text-white shadow-glow-purple hover:shadow-glow-cyan transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.4 }}
            >
              Get Started
            </motion.button>
          </div>

          {/* Mobile Menu Button */}
          <motion.button
            className="md:hidden p-2 rounded-lg hover:bg-bg-tertiary transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
            whileTap={{ scale: 0.9 }}
          >
            <svg
              className="w-6 h-6 text-text-primary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
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
          </motion.button>
        </div>

        {/* Mobile Menu */}
        <motion.div
          className="md:hidden overflow-hidden"
          initial={false}
          animate={{
            height: isMobileMenuOpen ? "auto" : 0,
            opacity: isMobileMenuOpen ? 1 : 0,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <div className="py-4 space-y-4">
            {/* Mobile Navigation Links */}
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleSmoothScroll(e, link.href)}
                className={`block px-4 py-2 rounded-lg transition-colors duration-200 ${
                  isLinkActive(link.href)
                    ? "text-primary bg-primary/10"
                    : "text-text-secondary hover:text-primary hover:bg-bg-tertiary"
                }`}
              >
                {link.name}
              </a>
            ))}

            {/* Mobile CTA Buttons */}
            <div className="pt-4 space-y-3 border-t border-primary/10">
              <button className="w-full px-6 py-3 rounded-lg font-semibold text-text-primary hover:bg-bg-tertiary transition-all duration-200">
                Sign In
              </button>
              <button className="w-full px-6 py-3 bg-gradient-purple rounded-lg font-semibold text-white shadow-glow-purple">
                Get Started
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.nav>
  );
}
