import { Hero } from '@/components/landing/Hero';

/**
 * Landing Page - SampleMind AI Homepage
 * 
 * Design: Modern Tech Cyberpunk with Glassmorphism
 * Components: Hero, Features, Stats, CTA
 */
export function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Hero />
      {/* Add more sections here: Navbar, Features, Stats, etc. */}
    </div>
  );
}
