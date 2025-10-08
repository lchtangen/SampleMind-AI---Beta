# 🖥️ Electron Desktop Application - Complete Setup Guide

## 🚀 **Quick Start Commands**

### **Method 1: Using the Launcher Script (Easiest)**
```bash
cd /home/lchta/Projects/Samplemind-AI
./start-desktop.sh
```

### **Method 2: Manual Setup (Step by Step)**

#### **Step 1: Install Dependencies**
```bash
# Install web app dependencies
cd /home/lchta/Projects/Samplemind-AI/web-app
npm install

# Install Electron dependencies  
cd /home/lchta/Projects/Samplemind-AI/electron-app
npm install
```

#### **Step 2: Start Services (Development Mode)**
```bash
# Terminal 1: Start web server
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev
# ✅ Should show: Local: http://localhost:3000/

# Terminal 2: Start Electron app
cd /home/lchta/Projects/Samplemind-AI/electron-app  
npm run dev
# ✅ Desktop application should open
```

#### **Step 3: Production Build (Optional)**
```bash
# Build web application
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run build

# Build and package Electron app
cd /home/lchta/Projects/Samplemind-AI/electron-app
npm run build
```

---

## 🔧 **Troubleshooting**

### **Issue: Blank Screen in Desktop App**

**Cause**: Web server not running or wrong port configuration

**Solution**:
```bash
# 1. Check if web server is running
curl http://localhost:3000
# Should return HTML content

# 2. If not running, start it:
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev

# 3. Then start Electron:
cd /home/lchta/Projects/Samplemind-AI/electron-app
npm run dev
```

### **Issue: "Connection Refused" Error**

**Cause**: Port mismatch between Electron and web server

**Solution**: The fix is already applied - Electron now uses port 3000 to match the web server.

### **Issue: "GL Surface" Errors**

**Cause**: Graphics driver warnings (harmless)

**Solution**: These warnings can be ignored. The app will still work normally.

### **Issue: Web App Shows Blank Page**

**Cause**: Missing dependencies or build issues

**Solution**:
```bash
# 1. Clear node modules and reinstall
cd /home/lchta/Projects/Samplemind-AI/web-app
rm -rf node_modules package-lock.json
npm install

# 2. Try running in different mode
npm run dev --host 0.0.0.0

# 3. Check browser console for errors (F12)
```

### **Issue: Electron Won't Start**

**Cause**: Missing Electron dependencies

**Solution**:
```bash
# 1. Reinstall Electron dependencies
cd /home/lchta/Projects/Samplemind-AI/electron-app
rm -rf node_modules package-lock.json
npm install

# 2. Try running with more verbose output
npm run dev -- --enable-logging --v=1
```

---

## 📋 **Available Commands**

### **Web Application Commands**
```bash
cd /home/lchta/Projects/Samplemind-AI/web-app

npm run dev      # Start development server (port 3000)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Check code quality  
```

### **Electron Application Commands**
```bash
cd /home/lchta/Projects/Samplemind-AI/electron-app

npm start        # Start production app
npm run dev      # Start development app  
npm run build    # Build distributables
npm run package  # Package for current platform
```

---

## ✅ **Verification Steps**

### **1. Check Web Server**
```bash
# Should return HTML content
curl http://localhost:3000

# Or open in browser
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
```

### **2. Check Electron App**
- Desktop window should open automatically
- Should display the SampleMind AI interface
- DevTools should be available (F12 or Cmd+Option+I)

### **3. Test Features**
- Drag and drop audio files
- Use the analysis features
- Check that AI integration works

---

## 🎯 **Expected Results**

### **✅ Working State**
- Web server runs on `http://localhost:3000/`
- Electron desktop app opens with full interface
- Drag & drop functionality works
- AI analysis features accessible
- No connection errors in console

### **🔴 Common Issues Fixed**
- ~~Port mismatch (5173 vs 3000)~~ ✅ Fixed
- ~~Missing dependencies~~ ✅ Should be installed
- ~~Blank screen issue~~ ✅ Should be resolved

---

## 📞 **Getting Help**

If you're still having issues:

1. **Check Terminal Output**: Look for specific error messages
2. **Browser Console**: Press F12 and check for JavaScript errors  
3. **Network Tab**: Verify API calls are working
4. **Process List**: Make sure both processes are running
   ```bash
   ps aux | grep -E "(npm|electron|vite)"
   ```

The desktop application should now work perfectly! 🎉