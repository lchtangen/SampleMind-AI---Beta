import { CTA } from "@/components/landing/CTA";
import { Features } from "@/components/landing/Features";
import { Footer } from "@/components/landing/Footer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Navbar } from "@/components/landing/Navbar";
import { Pricing } from "@/components/landing/Pricing";
import { Stats } from "@/components/landing/Stats";
import { Testimonials } from "@/components/landing/Testimonials";
import { BackToTop } from "@/components/ui/BackToTop";

/**
 * Landing Page - SampleMind AI Beta Website (Complete)
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Structure:
 * 1. Navbar - Fixed header with smooth scroll navigation
 * 2. Hero - Full-screen welcome with waveform
 * 3. Features - 8 key product features
 * 4. How It Works - 4-step user journey
 * 5. Stats - Animated metrics showcase
 * 6. Pricing - 3-tier pricing with toggle
 * 7. Testimonials - Social proof carousel
 * 8. CTA - Email signup conversion
 * 9. Footer - Comprehensive site map
 *
 * Features:
 * - Smooth scroll navigation with active section highlighting
 * - Back to top button (appears after 300px scroll)
 * - Responsive design (mobile → tablet → desktop)
 * 
 * Version: 2.0.0 Phoenix Beta
 * Status: Production Ready
 */
export function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />

      <main>
        <Hero />

        <section id="features">
          <Features />
        </section>

        <section id="how-it-works">
          <HowItWorks />
        </section>

        <Stats />

        <section id="pricing">
          <Pricing />
        </section>

        <section id="testimonials">
          <Testimonials />
        </section>

        <section id="cta">
          <CTA />
        </section>
      </main>

      <Footer />
      
      {/* Back to Top Button */}
      <BackToTop />
    </div>
  );
}
