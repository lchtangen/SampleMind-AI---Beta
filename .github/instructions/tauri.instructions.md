---
applyTo: "app/**/*.svelte,app/**/*.ts,app/**/*.rs"
---

# Tauri Desktop App Instructions

- Location: `app/` — Tauri v2 + Svelte 5 desktop scaffold
- This is a scaffold — not fully built yet
- Svelte 5 with runes syntax (`$state`, `$derived`, `$effect`)
- Tauri v2 for native desktop functionality
- Rust backend for system-level operations
- Communicate with Python backend via HTTP API or IPC
- Do not duplicate Python backend logic in Rust — call the API instead
