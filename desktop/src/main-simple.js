/**
 * SampleMind AI - Simplified Electron Main Process
 * Fixed for reliability and reduced errors
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');

// Development mode flag
const isDev = process.argv.includes('--dev') || !app.isPackaged;

// Simplified command line switches for stability
if (process.platform === 'linux') {
    app.commandLine.appendSwitch('--no-sandbox');
    app.commandLine.appendSwitch('--disable-setuid-sandbox');
    app.commandLine.appendSwitch('--disable-dev-shm-usage');
    app.commandLine.appendSwitch('--disable-gpu-sandbox');
}

let mainWindow = null;

/**
 * Create the main application window - simplified version
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        backgroundColor: '#0f172a',
        show: false, // Don't show until ready
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: !isDev,
        },
    });

    // Load the app
    if (isDev) {
        // Development: Load from Vite dev server
        mainWindow.loadURL('http://localhost:3000');
    } else {
        // Production: Load from bundled files
        const appPath = path.join(__dirname, '../../web-app/dist/index.html');
        mainWindow.loadFile(appPath);
    }

    // Show window when ready to prevent white flash
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
    });

    // Handle window close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});