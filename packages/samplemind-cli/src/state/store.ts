import { create } from 'zustand';

import type { FileIndex } from '../core/indexer.js';
import type { CliConfig } from '../services/configManager.js';
import type { SearchEngine, SearchResult } from '../core/search.js';

export type MenuRoute = 'dashboard' | 'analysis' | 'batch' | 'settings' | 'exit';

export type ThemeVariant = 'neon-glass' | 'dark-neon' | 'minimal';

export interface CliSettings {
  theme: ThemeVariant;
  telemetry: boolean;
  showHints: boolean;
}

export interface TaskProgress {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'success' | 'error';
  progress?: number;
  logs: string[];
  startedAt: number;
  finishedAt?: number;
}

export interface NotificationItem {
  id: string;
  message: string;
  tone: 'info' | 'success' | 'warning' | 'error';
  createdAt: number;
}

interface CliState {
  config: CliConfig;
  settings: CliSettings;
  index: FileIndex | null;
  searchEngine: SearchEngine | null;
  searchQuery: string;
  searchResults: SearchResult[];
  menuRoute: MenuRoute;
  notifications: NotificationItem[];
  activeTasks: TaskProgress[];
  showHelpOverlay: boolean;
  showShortcutOverlay: boolean;
  showSearchOverlay: boolean;
  setConfig: (config: CliConfig) => void;
  setSettings: (settings: Partial<CliSettings>) => void;
  setIndex: (index: FileIndex) => void;
  setSearchEngine: (engine: SearchEngine | null) => void;
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: SearchResult[]) => void;
  setMenuRoute: (route: MenuRoute) => void;
  pushNotification: (notification: Omit<NotificationItem, 'id' | 'createdAt'>) => void;
  dismissNotification: (id: string) => void;
  clearNotifications: () => void;
  registerTask: (task: TaskProgress) => void;
  updateTask: (id: string, patch: Partial<TaskProgress>) => void;
  clearFinishedTasks: () => void;
  toggleHelpOverlay: (value?: boolean) => void;
  toggleShortcutOverlay: (value?: boolean) => void;
  toggleSearchOverlay: (value?: boolean) => void;
}

const defaultConfig: CliConfig = {
  projectRoot: process.cwd(),
  theme: 'neon-glass',
  telemetry: false
};

const defaultSettings: CliSettings = {
  theme: 'neon-glass',
  telemetry: false,
  showHints: true
};

export const useCliStore = create<CliState>((set) => ({
  config: defaultConfig,
  settings: defaultSettings,
  index: null,
  searchEngine: null,
  searchQuery: '',
  searchResults: [],
  menuRoute: 'dashboard',
  notifications: [],
  activeTasks: [],
  showHelpOverlay: false,
  showShortcutOverlay: false,
  showSearchOverlay: false,
  setConfig: (config) => set({ config }),
  setSettings: (settings) => set((state) => ({ settings: { ...state.settings, ...settings } })),
  setIndex: (index) => set({ index }),
  setSearchEngine: (engine) => set({ searchEngine: engine }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSearchResults: (results) => set({ searchResults: results }),
  setMenuRoute: (route) => set({ menuRoute: route }),
  pushNotification: ({ message, tone }) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          id: Math.random().toString(36).slice(2),
          message,
          tone,
          createdAt: Date.now()
        }
      ]
    })),
  dismissNotification: (id) =>
    set((state) => ({ notifications: state.notifications.filter((note) => note.id !== id) })),
  clearNotifications: () => set({ notifications: [] }),
  registerTask: (task) =>
    set((state) => ({ activeTasks: [...state.activeTasks, task] })),
  updateTask: (id, patch) =>
    set((state) => ({
      activeTasks: state.activeTasks.map((task) =>
        task.id === id
          ? {
              ...task,
              ...patch,
              logs: patch.logs ? [...task.logs, ...patch.logs] : task.logs
            }
          : task
      )
    })),
  clearFinishedTasks: () =>
    set((state) => ({ activeTasks: state.activeTasks.filter((task) => task.status === 'running') })),
  toggleHelpOverlay: (value) =>
    set((state) => ({ showHelpOverlay: typeof value === 'boolean' ? value : !state.showHelpOverlay })),
  toggleShortcutOverlay: (value) =>
    set((state) => ({ showShortcutOverlay: typeof value === 'boolean' ? value : !state.showShortcutOverlay })),
  toggleSearchOverlay: (value) =>
    set((state) => ({ showSearchOverlay: typeof value === 'boolean' ? value : !state.showSearchOverlay }))
}));
