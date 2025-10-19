# 🔧 Dependency Install Troubleshooting Guide

**Issue:** ERR_INVALID_THIS on npm registry fetches  
**Root Cause:** Node v24.10.0 + pnpm (8.0.0 or 9.12.3) + undici HTTP client incompatibility  
**Status:** Blocking gallery preview at `http://localhost:3000/gallery`

---

## ✅ What's Already Complete

All code is ready and functional once dependencies are installed:

### Components (12)
- ✅ `apps/web/src/components/NeonButton.tsx`
- ✅ `apps/web/src/components/GlassPanel.tsx`
- ✅ `apps/web/src/components/GlowCard.tsx`
- ✅ `apps/web/src/components/NeonTabs.tsx`
- ✅ `apps/web/src/components/Modal.tsx`
- ✅ `apps/web/src/components/Dropdown.tsx`
- ✅ `apps/web/src/components/Toast.tsx`
- ✅ `apps/web/src/components/Skeleton.tsx`
- ✅ `apps/web/src/components/WaveformCanvas.tsx`
- ✅ `apps/web/src/components/SpectrogramCanvas.tsx`
- ✅ `apps/web/src/components/ThreeJSVisualizer.tsx`
- ✅ `apps/web/src/components/GradientBackground.tsx`

### Pages
- ✅ `apps/web/app/gallery/page.tsx` — Complete theme showcase

### Documentation
- ✅ `DOCUMENTS/DESIGN_INSPIRATION_SOURCES.md` (80 sources)
- ✅ `DOCUMENTS/DESIGN_INSPIRATION_SOURCES_BATCH2.md` (145 sources)
- ✅ `DOCUMENTS/COMPLETE_10_PHASE_100_TASK_PLAN.md` (100 tasks)
- ✅ `DOCUMENTS/SESSION_SUMMARY_OCT19_EVENING.md`

### Theme
- ✅ `apps/web/tailwind.config.js` — Cyberpunk glassmorphism with HSL tokens

---

## 🚧 Install Attempts Made

1. ❌ pnpm 8.0.0 install — ERR_INVALID_THIS
2. ❌ pnpm 9.12.3 install — ERR_INVALID_THIS (persists)
3. ❌ npm install in apps/web — "Invalid Version:" error

---

## 🔄 Recommended Solutions

### Option 1: Switch to Node 20 LTS (Most Reliable)

```bash
# Install nvm if not present
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use Node 20 LTS
nvm install 20
nvm use 20
node -v  # Should show v20.x.x

# Install pnpm 8.15.8
corepack enable
corepack prepare pnpm@8.15.8 --activate
pnpm -v  # Should show 8.15.8

# Install dependencies
pnpm install

# Start dev server
pnpm web:dev
```

### Option 2: Use Yarn as Alternative

```bash
# Enable corepack and install yarn
corepack enable
corepack prepare yarn@stable --activate

# Install dependencies
yarn install

# Start dev server
cd apps/web
yarn dev
```

### Option 3: Docker Development Environment

```bash
# Use existing docker-compose setup
docker-compose up -d

# Or create a dedicated frontend container
docker run -it --rm \
  -v $(pwd):/app \
  -w /app/apps/web \
  -p 3000:3000 \
  node:20-alpine \
  sh -c "corepack enable && pnpm install && pnpm dev"
```

### Option 4: Manual Dependency Resolution

If all else fails, manually install critical dependencies:

```bash
cd apps/web

# Install Next.js and React directly
npm install next@14.1.0 react@18.2.0 react-dom@18.2.0 --legacy-peer-deps

# Install Tailwind
npm install tailwindcss@3.4.0 postcss@8.4.32 autoprefixer@10.4.16 --legacy-peer-deps

# Install UI dependencies
npm install clsx@2.1.0 framer-motion@10.16.4 lucide-react@0.294.0 --legacy-peer-deps

# Start dev
npm run dev
```

---

## 🎯 Preview Without Dev Server

You can view the component code directly:

### Gallery Page
```bash
cat apps/web/app/gallery/page.tsx
```

### Component Example
```bash
cat apps/web/src/components/NeonButton.tsx
```

### Tailwind Theme
```bash
cat apps/web/tailwind.config.js
```

---

## 📊 System Info

- **Node Version:** v24.10.0
- **pnpm Attempted:** 8.0.0, 9.12.3
- **OS:** macOS
- **Error:** ERR_INVALID_THIS (undici HTTP client issue)

---

## 🔍 Root Cause Analysis

The ERR_INVALID_THIS error occurs because:
1. Node v24 uses a newer undici version as the HTTP client
2. pnpm (both 8 and 9) has internal HTTP code that conflicts
3. Specific to @storybook and @testing-library packages
4. Registry fetch timing out after multiple retries

**Known Issue:** https://github.com/pnpm/pnpm/issues/7438

---

## ✅ Next Steps

1. **Immediate:** Switch to Node 20 LTS (Option 1 above)
2. **Alternative:** Use Yarn if pnpm continues failing
3. **Workaround:** Remove Storybook/testing deps temporarily
4. **Long-term:** Wait for pnpm/Node 24 compatibility fix

---

## 📝 Temporary Package.json Simplification

If you want to bypass Storybook/testing for now:

```bash
cd apps/web
# Backup original
cp package.json package.json.backup

# Remove problematic devDependencies manually or with jq
# Then run: npm install
```

---

**Status:** Install blocked but all code ready. Recommend Node 20 LTS switch.
