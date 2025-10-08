#!/bin/bash

# 🖥️ SampleMind AI - Fixed Desktop Application Launcher
# ====================================================

echo "🚀 Starting SampleMind AI Desktop Application (FIXED VERSION)..."
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the SampleMind-AI project root directory"
    exit 1
fi

# Check for shared memory permissions issue (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ ! -w "/dev/shm" ]; then
        echo "⚠️  SHARED MEMORY PERMISSION ISSUE DETECTED"
        echo ""
        echo "📋 To fix Electron desktop app issues, run:"
        echo "   sudo chmod 1777 /dev/shm"
        echo ""
        echo "🌐 Alternative: Use web browser instead:"
        echo "   http://localhost:3000 (after web server starts)"
        echo ""
        echo "📖 Full guide: DESKTOP_FIX_GUIDE.md"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f "vite" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
sleep 2

# Start web server
echo "🌐 Starting web application server..."
cd web-app
npm run dev > ../logs/web-server.log 2>&1 &
WEB_PID=$!
cd ..

# Wait for web server to be ready
echo "⏳ Waiting for web server to start..."
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Web server ready on http://localhost:3000"
        break
    fi
    echo "   Waiting... ($i/10)"
    sleep 2
done

# Start Electron with simplified configuration
echo "🖥️  Starting Electron desktop application..."
cd electron-app
npm run dev > ../logs/electron.log 2>&1 &
ELECTRON_PID=$!
cd ..

echo ""
echo "✅ SampleMind AI Desktop Application Started!"
echo ""
echo "📋 Status:"
echo "   🌐 Web Server: http://localhost:3000 (PID: $WEB_PID)"
echo "   🖥️  Desktop App: Electron (PID: $ELECTRON_PID)"
echo ""
echo "� Logs:"
echo "   • Web server: logs/web-server.log"
echo "   • Electron: logs/electron.log"
echo ""
echo "🎯 Next Steps:"
echo "   • Desktop window should open in 5-10 seconds"
echo "   • If issues, check log files above"
echo "   • Press Ctrl+C to stop all services"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping SampleMind AI Desktop Application..."; kill $ELECTRON_PID 2>/dev/null; kill $WEB_PID 2>/dev/null; echo "✅ All services stopped."; exit 0' INT

echo "⚡ Services running in background. Check desktop window!"
echo "   (Press Ctrl+C to stop)"

wait