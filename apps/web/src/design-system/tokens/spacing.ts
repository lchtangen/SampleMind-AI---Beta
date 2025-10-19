/**
 * SPACING SCALE
 * Base unit: 4px
 * Follows 4px grid system for consistent spacing
 */

export const spacing = {
  // Micro spacing (1-4px)
  0: '0',
  px: '1px',
  0.5: '2px',
  
  // Base scale (4px increments)
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  7: '28px',
  8: '32px',
  
  // Medium scale
  10: '40px',
  12: '48px',
  14: '56px',
  16: '64px',
  
  // Large scale
  20: '80px',
  24: '96px',
  28: '112px',
  32: '128px',
  
  // Extra large
  36: '144px',
  40: '160px',
  48: '192px',
  56: '224px',
  64: '256px',
} as const;

/**
 * Container widths for responsive layouts
 */
export const containerWidth = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
  full: '100%',
} as const;

/**
 * Breakpoints matching Tailwind defaults
 */
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

/**
 * Common spacing patterns
 */
export const spacingPatterns = {
  // Component internal padding
  componentPaddingSm: spacing[3],      // 12px
  componentPadding: spacing[4],        // 16px
  componentPaddingLg: spacing[6],      // 24px
  
  // Section spacing
  sectionGapSm: spacing[8],            // 32px
  sectionGap: spacing[12],             // 48px
  sectionGapLg: spacing[16],           // 64px
  
  // Layout margins
  layoutMarginSm: spacing[4],          // 16px
  layoutMargin: spacing[6],            // 24px
  layoutMarginLg: spacing[8],          // 32px
  
  // Grid gaps
  gridGapSm: spacing[2],               // 8px
  gridGap: spacing[4],                 // 16px
  gridGapLg: spacing[6],               // 24px
} as const;

export type Spacing = keyof typeof spacing;
export type ContainerWidth = keyof typeof containerWidth;
export type Breakpoint = keyof typeof breakpoints;
