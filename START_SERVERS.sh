#!/bin/bash

# 🚀 SampleMind AI - Quick Start Script
# Starts both backend and frontend servers

echo "🎯 Starting SampleMind AI Full Stack..."
echo ""

# Terminal 1 - Backend API
echo "📡 Starting Backend API on http://localhost:8000"
echo "   Docs: http://localhost:8000/api/docs"
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Terminal 2 - Frontend
echo ""
echo "🎨 Starting Frontend on http://localhost:3000"
cd apps/web && pnpm dev &
FRONTEND_PID=$!

echo ""
echo "✅ Servers starting..."
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📚 Access:"
echo "   Frontend:  http://localhost:3000"
echo "   API:       http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
