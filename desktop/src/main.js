/**
 * SampleMind AI - Electron Main Process
 *
 * Desktop application wrapper for the React PWA
 */

const { app, BrowserWindow, ipcMain, dialog, shell, Menu, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Initialize persistent store
const store = new Store({
  name: 'samplemind-config',
  defaults: {
    windowBounds: { width: 1400, height: 900 },
    apiUrl: 'http://localhost:8000',
    theme: 'dark',
    recentFiles: [],
  },
});

let mainWindow = null;
let tray = null;
let apiServerProcess = null;

// Development mode flag
const isDev = process.argv.includes('--dev') || !app.isPackaged;

// Graphics and performance optimizations - safer settings
if (process.platform === 'linux') {
  app.commandLine.appendSwitch('--no-sandbox');
  app.commandLine.appendSwitch('--disable-setuid-sandbox');
  app.commandLine.appendSwitch('--disable-dev-shm-usage');
}

// Reduce console noise in development
if (isDev) {
  app.commandLine.appendSwitch('--log-level', '1');
}

/**
 * Create the main application window
 */
function createWindow() {
  const windowBounds = store.get('windowBounds');

  mainWindow = new BrowserWindow({
    width: windowBounds.width,
    height: windowBounds.height,
    minWidth: 1024,
    minHeight: 768,
    backgroundColor: '#0A0A0F',
    transparent: true,
    frame: false,
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 20, y: 20 },
    vibrancy: 'dark',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev,
      // Graphics and performance optimizations
      enableRemoteModule: false,
      hardwareAcceleration: true,
      experimentalFeatures: false,
    },
    icon: getIcon(),
  });

  // Load the app
  if (isDev) {
    // Development: Load from Vite dev server
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // Production: Load from bundled files
    const appPath = path.join(__dirname, '../../resources/app/index.html');
    mainWindow.loadFile(appPath);
  }

  // Save window bounds on resize
  mainWindow.on('resize', () => {
    const bounds = mainWindow.getBounds();
    store.set('windowBounds', bounds);
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create application menu
  createMenu();

  // Check for updates (production only)
  if (!isDev) {
    setTimeout(() => {
      checkForUpdates();
    }, 3000);
  }
}

/**
 * Get platform-specific icon
 */
function getIcon() {
  const iconPath = path.join(__dirname, '../build');
  if (process.platform === 'darwin') {
    return path.join(iconPath, 'icon.icns');
  } else if (process.platform === 'win32') {
    return path.join(iconPath, 'icon.ico');
  } else {
    return path.join(iconPath, 'icon.png');
  }
}

/**
 * Create system tray icon
 */
function createTray() {
  const icon = getIcon();
  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        mainWindow.show();
      },
    },
    {
      label: 'Quit',
      click: () => {
        app.isQuiting = true;
        app.quit();
      },
    },
  ]);

  tray.setToolTip('SampleMind AI');
  tray.setContextMenu(contextMenu);
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Audio File...',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            openFileDialog();
          },
        },
        {
          label: 'Open Directory...',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: () => {
            openDirectoryDialog();
          },
        },
        { type: 'separator' },
        {
          label: 'Recent Files',
          submenu: getRecentFilesMenu(),
        },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        { type: 'separator' },
        { role: 'front' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://github.com/samplemind-ai/docs');
          },
        },
        {
          label: 'Report Issue',
          click: () => {
            shell.openExternal('https://github.com/samplemind-ai/issues');
          },
        },
        { type: 'separator' },
        {
          label: 'Check for Updates...',
          click: () => {
            checkForUpdates(true);
          },
        },
        { type: 'separator' },
        {
          label: 'About SampleMind AI',
          click: () => {
            showAboutDialog();
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Get recent files submenu
 */
function getRecentFilesMenu() {
  const recentFiles = store.get('recentFiles', []);

  if (recentFiles.length === 0) {
    return [{ label: 'No recent files', enabled: false }];
  }

  return recentFiles.map((filePath) => ({
    label: path.basename(filePath),
    click: () => {
      mainWindow.webContents.send('open-file', filePath);
    },
  }));
}

/**
 * Open file dialog
 */
async function openFileDialog() {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg'] },
      { name: 'All Files', extensions: ['*'] },
    ],
  });

  if (!result.canceled && result.filePaths.length > 0) {
    addToRecentFiles(result.filePaths[0]);
    mainWindow.webContents.send('open-files', result.filePaths);
  }
}

/**
 * Open directory dialog
 */
async function openDirectoryDialog() {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });

  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow.webContents.send('open-directory', result.filePaths[0]);
  }
}

/**
 * Add file to recent files
 */
function addToRecentFiles(filePath) {
  let recentFiles = store.get('recentFiles', []);

  // Remove if already exists
  recentFiles = recentFiles.filter((f) => f !== filePath);

  // Add to beginning
  recentFiles.unshift(filePath);

  // Keep only last 10
  recentFiles = recentFiles.slice(0, 10);

  store.set('recentFiles', recentFiles);
}

/**
 * Show about dialog
 */
function showAboutDialog() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'About SampleMind AI',
    message: 'SampleMind AI',
    detail: `Version: ${app.getVersion()}\n\nAI-powered music production and sample analysis platform.\n\n© 2025 SampleMind AI`,
    buttons: ['OK'],
  });
}

/**
 * Check for updates
 */
function checkForUpdates(userInitiated = false) {
  autoUpdater.checkForUpdatesAndNotify();

  autoUpdater.on('update-available', () => {
    if (Notification.isSupported()) {
      new Notification({
        title: 'Update Available',
        body: 'A new version of SampleMind AI is available. Downloading...',
      }).show();
    }
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'A new version has been downloaded. Restart to apply the update?',
      buttons: ['Restart', 'Later'],
      defaultId: 0,
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });

  if (userInitiated) {
    autoUpdater.on('update-not-available', () => {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'No Updates',
        message: 'You are running the latest version of SampleMind AI.',
        buttons: ['OK'],
      });
    });
  }
}

/**
 * Show notification
 */
function showNotification(title, body) {
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
}

// ============================================================================
// IPC Handlers
// ============================================================================

ipcMain.handle('get-config', (event, key) => {
  return store.get(key);
});

ipcMain.handle('set-config', (event, key, value) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('open-file-dialog', async () => {
  await openFileDialog();
});

ipcMain.handle('open-directory-dialog', async () => {
  await openDirectoryDialog();
});

ipcMain.handle('show-notification', (event, title, body) => {
  showNotification(title, body);
});

ipcMain.handle('get-path', (event, name) => {
  return app.getPath(name);
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const data = await fs.promises.readFile(filePath);
    return { success: true, data: data.toString('base64') };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-file', async (event, filePath, data) => {
  try {
    await fs.promises.writeFile(filePath, Buffer.from(data, 'base64'));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  return await dialog.showSaveDialog(mainWindow, options);
});

// ============================================================================
// App Lifecycle
// ============================================================================

app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Cleanup
  if (apiServerProcess) {
    apiServerProcess.kill();
  }
});

// Handle file open (macOS)
app.on('open-file', (event, filePath) => {
  event.preventDefault();
  if (mainWindow) {
    mainWindow.webContents.send('open-file', filePath);
  }
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
