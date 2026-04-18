---
name: tauri-desktop
description: Guide for the Tauri v2 + Svelte 5 desktop application. Use when working on native desktop features.
---

## Tauri v2 Desktop App

### Location
`app/` — Scaffold stage (not fully built)

### Stack
- **Frontend:** Svelte 5 with runes syntax (`$state`, `$derived`, `$effect`)
- **Backend:** Rust for native operations
- **Bridge:** Tauri IPC for Svelte ↔ Rust communication

### Development
```bash
cd app
npm install
npm run tauri dev
```

### Architecture
- Svelte 5 handles the UI
- Rust handles system-level operations (file access, audio playback)
- Communicates with Python FastAPI backend via HTTP
- Do NOT duplicate backend logic in Rust — call the API

### Svelte 5 Runes
```svelte
<script>
  let count = $state(0)
  let doubled = $derived(count * 2)

  $effect(() => {
    console.log(`Count is ${count}`)
  })
</script>
```
