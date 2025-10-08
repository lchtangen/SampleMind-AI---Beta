/**
 * useElectron Hook
 *
 * Provides access to Electron APIs when running in desktop mode
 */

import { useEffect, useState } from 'react';

// Electron API types
interface ElectronAPI {
  platform: string;
  version: string;
  getConfig: (key: string) => Promise<any>;
  setConfig: (key: string, value: any) => Promise<boolean>;
  openFileDialog: () => Promise<void>;
  openDirectoryDialog: () => Promise<void>;
  readFile: (filePath: string) => Promise<{ success: boolean; data?: string; error?: string }>;
  writeFile: (filePath: string, data: string) => Promise<{ success: boolean; error?: string }>;
  showSaveDialog: (options: any) => Promise<any>;
  getPath: (name: string) => Promise<string>;
  showNotification: (title: string, body: string) => Promise<void>;
  onOpenFile: (callback: (filePath: string) => void) => void;
  onOpenFiles: (callback: (filePaths: string[]) => void) => void;
  onOpenDirectory: (callback: (dirPath: string) => void) => void;
  removeListener: (channel: string) => void;
}

interface AppInfo {
  name: string;
  version: string;
  isElectron: boolean;
}

declare global {
  interface Window {
    electron?: ElectronAPI;
    appInfo?: AppInfo;
  }
}

export function useElectron() {
  const [isElectron, setIsElectron] = useState(false);
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    if (window.electron && window.appInfo) {
      setIsElectron(true);
      setAppInfo(window.appInfo);
    }
  }, []);

  return {
    isElectron,
    appInfo,
    electron: window.electron,
  };
}

/**
 * Hook for file operations
 */
export function useElectronFiles() {
  const { isElectron, electron } = useElectron();

  const openFile = async () => {
    if (!electron) return null;
    await electron.openFileDialog();
  };

  const openDirectory = async () => {
    if (!electron) return null;
    await electron.openDirectoryDialog();
  };

  const readFile = async (filePath: string) => {
    if (!electron) return null;
    return await electron.readFile(filePath);
  };

  const writeFile = async (filePath: string, data: string) => {
    if (!electron) return null;
    return await electron.writeFile(filePath, data);
  };

  const saveFile = async (options: {
    defaultPath?: string;
    filters?: Array<{ name: string; extensions: string[] }>;
  }) => {
    if (!electron) return null;
    return await electron.showSaveDialog(options);
  };

  return {
    isElectron,
    openFile,
    openDirectory,
    readFile,
    writeFile,
    saveFile,
  };
}

/**
 * Hook for notifications
 */
export function useElectronNotifications() {
  const { isElectron, electron } = useElectron();

  const showNotification = async (title: string, body: string) => {
    if (electron) {
      await electron.showNotification(title, body);
    } else if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body });
    } else if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        new Notification(title, { body });
      }
    }
  };

  return {
    isElectron,
    showNotification,
  };
}

/**
 * Hook for configuration
 */
export function useElectronConfig() {
  const { isElectron, electron } = useElectron();

  const getConfig = async <T = any>(key: string, defaultValue?: T): Promise<T | null> => {
    if (!electron) {
      // Fallback to localStorage
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : defaultValue ?? null;
    }
    return await electron.getConfig(key);
  };

  const setConfig = async (key: string, value: any): Promise<boolean> => {
    if (!electron) {
      // Fallback to localStorage
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    }
    return await electron.setConfig(key, value);
  };

  return {
    isElectron,
    getConfig,
    setConfig,
  };
}

/**
 * Hook for file events
 */
export function useElectronFileEvents(
  onFileOpen?: (filePath: string) => void,
  onFilesOpen?: (filePaths: string[]) => void,
  onDirectoryOpen?: (dirPath: string) => void
) {
  const { isElectron, electron } = useElectron();

  useEffect(() => {
    if (!electron) return;

    if (onFileOpen) {
      electron.onOpenFile(onFileOpen);
    }

    if (onFilesOpen) {
      electron.onOpenFiles(onFilesOpen);
    }

    if (onDirectoryOpen) {
      electron.onOpenDirectory(onDirectoryOpen);
    }

    return () => {
      electron.removeListener('open-file');
      electron.removeListener('open-files');
      electron.removeListener('open-directory');
    };
  }, [electron, onFileOpen, onFilesOpen, onDirectoryOpen]);

  return { isElectron };
}
