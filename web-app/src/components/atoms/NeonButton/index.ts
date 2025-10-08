/**
 * NeonButton - Barrel Export
 *
 * Provides tree-shakeable exports for the NeonButton component
 * and its associated types.
 *
 * @module NeonButton
 */

// Named exports for tree-shaking optimization
export { NeonButton } from './NeonButton';
export type {
  NeonButtonProps,
  ButtonVariant,
  ButtonSize,
  ReactNode,
} from './NeonButton.types';

// Default export for convenience
export { default } from './NeonButton';
