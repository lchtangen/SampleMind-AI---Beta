/**
 * LAYOUT SYSTEM
 * 12-column responsive grid
 */

export const grid = {
  columns: 12,
  gap: {
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
} as const;

/**
 * Z-Index Scale
 * Organized by layer hierarchy
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  modalBackdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
  notification: 1700,
} as const;

/**
 * Common layout patterns
 */
export const layouts = {
  // Container max-widths
  containerMaxWidth: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // Sidebar widths
  sidebarWidth: {
    collapsed: '64px',
    default: '256px',
    expanded: '320px',
  },
  
  // Header heights
  headerHeight: {
    sm: '48px',
    default: '64px',
    lg: '80px',
  },
  
  // Footer heights
  footerHeight: {
    default: '80px',
    lg: '120px',
  },
} as const;

export type ZIndex = keyof typeof zIndex;
