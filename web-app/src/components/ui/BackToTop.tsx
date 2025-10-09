import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";

/**
 * BackToTop Component
 * 
 * Design: Floating action button with smooth scroll
 * Features:
 * - Appears after scrolling down 300px
 * - Smooth scroll to top on click
 * - Glassmorphic design with neon glow
 * - Pulsing animation to attract attention
 * 
 * Position: Fixed bottom-right corner
 */
export function BackToTop() {
  const [isVisible, setIsVisible] = useState(false);

  // Show button when page is scrolled down 300px
  useEffect(() => {
    const toggleVisibility = () => {
      if (window.scrollY > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);
    toggleVisibility(); // Initial check

    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-40 w-14 h-14 rounded-full bg-gradient-purple shadow-glow-purple hover:shadow-glow-cyan flex items-center justify-center group"
          initial={{ opacity: 0, scale: 0, y: 100 }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            y: 0,
          }}
          exit={{ opacity: 0, scale: 0, y: 100 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          aria-label="Back to top"
        >
          {/* Arrow Icon */}
          <motion.svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            animate={{ y: [0, -4, 0] }}
            transition={{ 
              duration: 1.5, 
              repeat: Infinity, 
              ease: "easeInOut" 
            }}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </motion.svg>

          {/* Pulse Ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-primary"
            initial={{ scale: 1, opacity: 0.8 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              ease: "easeOut" 
            }}
          />
        </motion.button>
      )}
    </AnimatePresence>
  );
}
