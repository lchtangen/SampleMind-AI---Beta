#!/bin/bash

# SampleMind AI - Quick Launch Script for Ubuntu
# Starts both backend and frontend servers using tmux

echo "🚀 Launching SampleMind AI..."
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux not found. Installing..."
    sudo apt install -y tmux
fi

# Kill existing session if it exists
tmux kill-session -t samplemind 2>/dev/null

# Create new tmux session
tmux new-session -d -s samplemind -c /home/lchta/Projects/Samplemind-AI

# Split window horizontally
tmux split-window -h -t samplemind

# Backend in left pane
tmux send-keys -t samplemind:0.0 'source venv/bin/activate' C-m
tmux send-keys -t samplemind:0.0 'echo "🔧 Starting Backend (FastAPI + Claude Sonnet 4.5)..."' C-m
tmux send-keys -t samplemind:0.0 'export PYTHONPATH="${PYTHONPATH}:/home/lchta/Projects/Samplemind-AI/src"' C-m
tmux send-keys -t samplemind:0.0 'python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000' C-m

# Frontend in right pane
tmux send-keys -t samplemind:0.1 'cd web-app' C-m
tmux send-keys -t samplemind:0.1 'echo "⚛️  Starting Frontend (React + Vite)..."' C-m
tmux send-keys -t samplemind:0.1 'npm run dev' C-m

# Wait a moment for servers to start
sleep 3

echo "✅ SampleMind AI is starting in tmux session 'samplemind'"
echo ""
echo "📊 Status:"
echo "   Backend:  http://localhost:8000/api/assistant/health"
echo "   Frontend: http://localhost:5173"
echo "   Demo:     http://localhost:5173/assistant-demo"
echo ""
echo "🎮 tmux Controls:"
echo "   Attach:   tmux attach -t samplemind"
echo "   Detach:   Ctrl+B then D"
echo "   Switch:   Ctrl+B then arrow keys"
echo "   Kill:     tmux kill-session -t samplemind"
echo ""
echo "🌐 Opening browser in 5 seconds..."

# Open browser after 5 seconds
(sleep 5 && xdg-open http://localhost:5173/assistant-demo 2>/dev/null) &

# Attach to tmux session
tmux attach -t samplemind
