import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

type Theme = 'dark' | 'light' | 'system';

type Notification = {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
};

interface UIState {
  theme: Theme;
  isSidebarOpen: boolean;
  notifications: Notification[];
  actions: {
    setTheme: (theme: Theme) => void;
    toggleSidebar: () => void;
    addNotification: (notification: Omit<Notification, 'id'>) => void;
    dismissNotification: (id: string) => void;
  };
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        theme: 'system',
        isSidebarOpen: true,
        notifications: [],
        actions: {
          setTheme: (theme) => set({ theme }),
          toggleSidebar: () =>
            set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
          addNotification: (notification) =>
            set((state) => ({
              notifications: [
                ...state.notifications,
                { ...notification, id: crypto.randomUUID() },
              ],
            })),
          dismissNotification: (id) =>
            set((state) => ({
              notifications: state.notifications.filter((n) => n.id !== id),
            })),
        },
      }),
      {
        name: 'ui-storage',
        partialize: (state) => ({
          theme: state.theme,
          isSidebarOpen: state.isSidebarOpen,
        }),
      }
    ),
    { name: 'UIStore' }
  )
);
