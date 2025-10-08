/**
 * SampleMind AI - Minimal Electron Main Process
 * Focus: Get the window to open reliably
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');

// Development mode flag
const isDev = process.argv.includes('--dev') || !app.isPackaged;

// Linux compatibility switches - balanced approach
if (process.platform === 'linux') {
    app.commandLine.appendSwitch('--no-sandbox');
    app.commandLine.appendSwitch('--disable-setuid-sandbox');
    app.commandLine.appendSwitch('--disable-dev-shm-usage');
}

let mainWindow = null;

function createWindow() {
    console.log('Creating Electron window...');

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        backgroundColor: '#1a1a1a',
        show: false, // Don't show until ready to prevent flash
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: !isDev,
        },
    });

    // Load the app with retry logic
    const targetUrl = 'http://localhost:3000';
    console.log(`Loading URL: ${targetUrl}`);

    // Function to check if web server is available
    const checkServer = async () => {
        try {
            const response = await fetch(targetUrl);
            return response.ok;
        } catch (error) {
            return false;
        }
    };

    // Try to load with retries
    const loadWithRetry = async (retries = 5) => {
        for (let i = 0; i < retries; i++) {
            const serverReady = await checkServer();
            if (serverReady) {
                try {
                    await mainWindow.loadURL(targetUrl);
                    console.log('URL loaded successfully');
                    return;
                } catch (error) {
                    console.error(`Attempt ${i + 1} failed:`, error);
                }
            } else {
                console.log(`Attempt ${i + 1}: Web server not ready yet...`);
            }

            if (i < retries - 1) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        // If all retries failed, show an error page
        console.error('All attempts failed, showing error page');
        const errorHtml = `
      <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; text-align: center; padding: 50px;">
          <h2>SampleMind AI - Connection Issue</h2>
          <p>Cannot connect to web server at ${targetUrl}</p>
          <p>Please ensure the web server is running:</p>
          <code style="background: #333; padding: 10px; border-radius: 5px; display: block; margin: 20px 0;">
            cd web-app && npm run dev
          </code>
          <button onclick="location.reload()" style="background: #0066cc; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
            Retry Connection
          </button>
        </body>
      </html>
    `;
        mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);
    };

    loadWithRetry();

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        console.log('Window ready to show');
        mainWindow.show();

        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
    });

    // Handle navigation
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        console.error(`Failed to load ${validatedURL}: ${errorDescription} (${errorCode})`);

        // Try to reload after a delay
        setTimeout(() => {
            console.log('Retrying to load...');
            mainWindow.loadURL(targetUrl);
        }, 2000);
    });

    // Handle window close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// App event handlers
app.whenReady().then(() => {
    console.log('App ready, creating window...');
    createWindow();
});

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

// Handle any unhandled errors
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
});

console.log('Electron main process started');