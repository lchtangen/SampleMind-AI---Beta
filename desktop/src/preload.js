/**
 * SampleMind AI - Electron Preload Script
 *
 * Secure bridge between main and renderer processes
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // Platform info
  platform: process.platform,
  version: process.versions.electron,

  // Config management
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),

  // File system operations
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  openDirectoryDialog: () => ipcRenderer.invoke('open-directory-dialog'),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, data) => ipcRenderer.invoke('write-file', filePath, data),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),

  // System paths
  getPath: (name) => ipcRenderer.invoke('get-path', name),

  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body),

  // Event listeners
  onOpenFile: (callback) => {
    ipcRenderer.on('open-file', (event, filePath) => callback(filePath));
  },
  onOpenFiles: (callback) => {
    ipcRenderer.on('open-files', (event, filePaths) => callback(filePaths));
  },
  onOpenDirectory: (callback) => {
    ipcRenderer.on('open-directory', (event, dirPath) => callback(dirPath));
  },

  // Remove listeners
  removeListener: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  },
});

// Expose app info
contextBridge.exposeInMainWorld('appInfo', {
  name: 'SampleMind AI',
  version: require('../../package.json').version,
  isElectron: true,
});
