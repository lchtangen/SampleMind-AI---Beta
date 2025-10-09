import { Hero } from "@/components/landing/Hero";
import { Navbar } from "@/components/landing/Navbar";
import { Stats } from "@/components/landing/Stats";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Pricing } from "@/components/landing/Pricing";
import { Testimonials } from "@/components/landing/Testimonials";
import { CTA } from "@/components/landing/CTA";
import { Footer } from "@/components/landing/Footer";

/**
 * Landing Page - SampleMind AI Beta Website (Complete)
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Structure:
 * 1. Navbar - Fixed header with navigation
 * 2. Hero - Full-screen welcome with waveform
 * 3. Features - 8 key product features
 * 4. How It Works - 4-step user journey
 * 5. Stats - Animated metrics showcase
 * 6. Pricing - 3-tier pricing with toggle
 * 7. Testimonials - Social proof carousel
 * 8. CTA - Email signup conversion
 * 9. Footer - Comprehensive site map
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
    </div>
  );
}
