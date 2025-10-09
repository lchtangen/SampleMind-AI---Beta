import { Hero } from "@/components/landing/Hero";
import { Navbar } from "@/components/landing/Navbar";
import { Stats } from "@/components/landing/Stats";

/**
 * Landing Page - SampleMind AI Homepage
 *
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Components: Navbar, Hero, Stats, Features (coming soon)
 */
export function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />
      <Hero />
      <Stats />
      {/* Coming soon: Features, Pricing, Testimonials, Footer */}
    </div>
  );
}
