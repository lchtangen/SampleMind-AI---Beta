import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AudioState {
  isPlaying: boolean;
  volume: number;
  currentTime: number;
  duration: number;
  currentTrack: string | null;
  actions: {
    togglePlay: () => void;
    setVolume: (volume: number) => void;
    setCurrentTime: (time: number) => void;
    loadTrack: (track: string, duration: number) => void;
  };
}

export const useAudioStore = create<AudioState>()(
  devtools(
    persist(
      (set) => ({
        isPlaying: false,
        volume: 0.8,
        currentTime: 0,
        duration: 0,
        currentTrack: null,
        actions: {
          togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
          setVolume: (volume) => set({ volume }),
          setCurrentTime: (time) => set({ currentTime: time }),
          loadTrack: (track, duration) =>
            set({
              currentTrack: track,
              duration,
              currentTime: 0,
              isPlaying: true,
            }),
        },
      }),
      {
        name: 'audio-storage',
        partialize: (state) => ({ volume: state.volume }), // Only persist volume
      }
    ),
    { name: 'AudioStore' }
  )
);
