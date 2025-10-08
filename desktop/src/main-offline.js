/**
 * SampleMind AI - Offline-First Electron Main Process
 * Bypass network and shared memory issues with local HTML
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');

// Development mode flag
const isDev = process.argv.includes('--dev') || !app.isPackaged;

// Minimal, safe command line switches
app.commandLine.appendSwitch('--disable-web-security');
app.commandLine.appendSwitch('--no-sandbox');

let mainWindow = null;

function createWindow() {
    console.log('Creating Electron window (offline-first approach)...');

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        backgroundColor: '#1a1a1a',
        show: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: false, // Disable for local file access
        },
    });

    // Create a standalone HTML page with connection options
    const fallbackHtml = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SampleMind AI Desktop</title>
        <style>
            body {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d1b69 100%);
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                text-align: center;
                max-width: 600px;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .logo {
                font-size: 3em;
                margin-bottom: 20px;
                color: #6366f1;
            }
            h1 {
                font-size: 2.5em;
                margin: 0 0 20px 0;
                font-weight: 300;
            }
            .subtitle {
                font-size: 1.2em;
                opacity: 0.8;
                margin-bottom: 30px;
            }
            .status {
                background: rgba(255, 165, 0, 0.2);
                border: 1px solid #ffa500;
                border-radius: 10px;
                padding: 20px;
                margin: 30px 0;
            }
            .button {
                background: linear-gradient(45deg, #6366f1, #8b5cf6);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.1em;
                cursor: pointer;
                margin: 10px;
                transition: transform 0.2s;
            }
            .button:hover {
                transform: translateY(-2px);
            }
            .button:active {
                transform: translateY(0);
            }
            .instructions {
                text-align: left;
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            code {
                background: rgba(0, 0, 0, 0.5);
                padding: 3px 8px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
            }
            .footer {
                margin-top: 30px;
                opacity: 0.6;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎵</div>
            <h1>SampleMind AI Desktop</h1>
            <p class="subtitle">AI-Powered Music Production Platform</p>
            
            <div class="status">
                <h3>⚠️ Web Server Connection Required</h3>
                <p>The desktop application needs the web server to be running.</p>
            </div>
            
            <div class="instructions">
                <h4>🚀 Quick Start:</h4>
                <ol>
                    <li>Open a terminal in the project directory</li>
                    <li>Run: <code>cd web-app && npm run dev</code></li>
                    <li>Wait for "Local: http://localhost:3000/" message</li>
                    <li>Click "Connect to Web Server" below</li>
                </ol>
            </div>
            
            <button class="button" onclick="connectToServer()">🔄 Connect to Web Server</button>
            <button class="button" onclick="openWebBrowser()">🌐 Open in Browser</button>
            <button class="button" onclick="showHelp()">❓ Help & Troubleshooting</button>
            
            <div class="footer">
                <p>SampleMind AI Desktop v0.8.0</p>
                <p>Professional Music Production Suite</p>
            </div>
        </div>

        <script>
            function connectToServer() {
                console.log('Attempting to connect to web server...');
                fetch('http://localhost:3000')
                    .then(response => {
                        if (response.ok) {
                            window.location.href = 'http://localhost:3000';
                        } else {
                            alert('Web server not responding. Please start it first:\\n\\ncd web-app && npm run dev');
                        }
                    })
                    .catch(error => {
                        alert('Cannot connect to web server on localhost:3000\\n\\nPlease run:\\ncd web-app && npm run dev\\n\\nThen try connecting again.');
                    });
            }
            
            function openWebBrowser() {
                if (typeof require !== 'undefined') {
                    const { shell } = require('electron');
                    shell.openExternal('http://localhost:3000');
                } else {
                    window.open('http://localhost:3000', '_blank');
                }
            }
            
            function showHelp() {
                alert(\`SampleMind AI Desktop - Help\\n\\n1. Start Web Server:\\n   cd web-app && npm run dev\\n\\n2. Wait for server to start (shows "Local: http://localhost:3000/")\\n\\n3. Click "Connect to Web Server"\\n\\nIf issues persist:\\n- Check that port 3000 is not blocked\\n- Try restarting the web server\\n- Check logs in the terminal\`);
            }
            
            // Auto-retry connection every 5 seconds
            setInterval(() => {
                fetch('http://localhost:3000')
                    .then(response => {
                        if (response.ok) {
                            // Auto-redirect if server becomes available
                            const shouldRedirect = confirm('Web server is now available! Connect automatically?');
                            if (shouldRedirect) {
                                window.location.href = 'http://localhost:3000';
                            }
                        }
                    })
                    .catch(() => {
                        // Server still not available
                    });
            }, 5000);
        </script>
    </body>
    </html>
  `;

    // Load the fallback HTML directly
    mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(fallbackHtml)}`);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        console.log('Window ready to show');
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

console.log('Electron main process started (offline-first mode)');