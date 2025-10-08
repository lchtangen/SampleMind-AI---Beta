/**
 * Zustand Stores
 * 
 * Centralized state management for SampleMind AI.
 * Uses Zustand for lightweight, performant state management.
 * 
 * Features:
 * - Zero boilerplate (no actions, reducers, dispatch)
 * - No Provider wrapper needed
 * - Persistence to localStorage
 * - Redux DevTools integration
 * - Full TypeScript support
 */

export { useAudioStore } from './audioStore';
export type { AudioFile } from './audioStore';

export { useUIStore } from './uiStore';
export type { ToastNotification, ModalState, ThemeMode } from './uiStore';
