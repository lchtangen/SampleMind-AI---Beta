/**
 * Global Application State Store using Zustand
 *
 * Manages:
 * - Audio files and analysis results
 * - WebSocket connection state
 * - UI state (theme, sidebar, modals)
 * - Music generation state
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// Types
// ============================================================================

export interface AudioFile {
  id: string;
  name: string;
  path: string;
  size: number;
  duration: number;
  uploadedAt: Date;
  analyzed: boolean;
  analysis?: AudioAnalysis;
}

export interface AudioAnalysis {
  tempo: number;
  key: string;
  genre?: string;
  mood?: string;
  energy: number;
  danceability?: number;
  acousticness?: number;
  instrumentalness?: number;
  valence?: number;
  spectralCentroid: number;
  onsets: number[];
  pitch?: number;
  summary?: string;
  suggestions?: string[];
  timestamp: number;
}

export interface StreamingSession {
  id: string;
  active: boolean;
  connected: boolean;
  latestAnalysis?: AudioAnalysis;
}

export interface MusicGeneration {
  id: string;
  prompt: string;
  style?: string;
  mood?: string;
  tempo?: number;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  audioUrl?: string;
  generatedAt?: Date;
  error?: string;
}

export interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  uploadModalOpen: boolean;
  generationModalOpen: boolean;
}

// ============================================================================
// Store Interface
// ============================================================================

interface AppState {
  // Audio files
  audioFiles: AudioFile[];
  selectedFile: AudioFile | null;
  addAudioFile: (file: AudioFile) => void;
  removeAudioFile: (id: string) => void;
  selectFile: (id: string | null) => void;
  updateFileAnalysis: (id: string, analysis: AudioAnalysis) => void;

  // Streaming
  streamingSession: StreamingSession | null;
  setStreamingSession: (session: StreamingSession | null) => void;
  updateStreamingAnalysis: (analysis: AudioAnalysis) => void;

  // Music generation
  generations: MusicGeneration[];
  addGeneration: (generation: MusicGeneration) => void;
  updateGeneration: (id: string, updates: Partial<MusicGeneration>) => void;
  removeGeneration: (id: string) => void;

  // UI state
  ui: UIState;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setUploadModalOpen: (open: boolean) => void;
  setGenerationModalOpen: (open: boolean) => void;

  // Actions
  reset: () => void;
}

// ============================================================================
// Initial State
// ============================================================================

const initialUIState: UIState = {
  theme: 'dark',
  sidebarOpen: true,
  uploadModalOpen: false,
  generationModalOpen: false,
};

// ============================================================================
// Store Implementation
// ============================================================================

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Audio files
        audioFiles: [],
        selectedFile: null,

        addAudioFile: (file) =>
          set((state) => ({
            audioFiles: [file, ...state.audioFiles],
          }), false, 'addAudioFile'),

        removeAudioFile: (id) =>
          set((state) => ({
            audioFiles: state.audioFiles.filter((f) => f.id !== id),
            selectedFile: state.selectedFile?.id === id ? null : state.selectedFile,
          }), false, 'removeAudioFile'),

        selectFile: (id) =>
          set((state) => ({
            selectedFile: id ? state.audioFiles.find((f) => f.id === id) || null : null,
          }), false, 'selectFile'),

        updateFileAnalysis: (id, analysis) =>
          set((state) => ({
            audioFiles: state.audioFiles.map((f) =>
              f.id === id ? { ...f, analyzed: true, analysis } : f
            ),
            selectedFile:
              state.selectedFile?.id === id
                ? { ...state.selectedFile, analyzed: true, analysis }
                : state.selectedFile,
          }), false, 'updateFileAnalysis'),

        // Streaming
        streamingSession: null,

        setStreamingSession: (session) =>
          set({ streamingSession: session }, false, 'setStreamingSession'),

        updateStreamingAnalysis: (analysis) =>
          set((state) => ({
            streamingSession: state.streamingSession
              ? { ...state.streamingSession, latestAnalysis: analysis }
              : null,
          }), false, 'updateStreamingAnalysis'),

        // Music generation
        generations: [],

        addGeneration: (generation) =>
          set((state) => ({
            generations: [generation, ...state.generations],
          }), false, 'addGeneration'),

        updateGeneration: (id, updates) =>
          set((state) => ({
            generations: state.generations.map((g) =>
              g.id === id ? { ...g, ...updates } : g
            ),
          }), false, 'updateGeneration'),

        removeGeneration: (id) =>
          set((state) => ({
            generations: state.generations.filter((g) => g.id !== id),
          }), false, 'removeGeneration'),

        // UI state
        ui: initialUIState,

        setTheme: (theme) =>
          set((state) => ({
            ui: { ...state.ui, theme },
          }), false, 'setTheme'),

        toggleSidebar: () =>
          set((state) => ({
            ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen },
          }), false, 'toggleSidebar'),

        setUploadModalOpen: (open) =>
          set((state) => ({
            ui: { ...state.ui, uploadModalOpen: open },
          }), false, 'setUploadModalOpen'),

        setGenerationModalOpen: (open) =>
          set((state) => ({
            ui: { ...state.ui, generationModalOpen: open },
          }), false, 'setGenerationModalOpen'),

        // Actions
        reset: () =>
          set({
            audioFiles: [],
            selectedFile: null,
            streamingSession: null,
            generations: [],
            ui: initialUIState,
          }, false, 'reset'),
      }),
      {
        name: 'samplemind-storage',
        partialize: (state) => ({
          audioFiles: state.audioFiles,
          ui: state.ui,
          // Don't persist streaming session or generations
        }),
      }
    )
  )
);
