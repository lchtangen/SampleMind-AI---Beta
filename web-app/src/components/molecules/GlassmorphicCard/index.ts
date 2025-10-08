/**
 * GlassmorphicCard - Barrel Export
 *
 * Provides tree-shakeable exports for the GlassmorphicCard component
 * and its associated types.
 *
 * @module GlassmorphicCard
 */

// Named exports for tree-shaking optimization
export { GlassmorphicCard } from './GlassmorphicCard';
export type {
  GlassmorphicCardProps,
  CardClickHandler,
  CardVariant,
  ReactNode,
} from './GlassmorphicCard.types';

// Default export for convenience
export { default } from './GlassmorphicCard';
