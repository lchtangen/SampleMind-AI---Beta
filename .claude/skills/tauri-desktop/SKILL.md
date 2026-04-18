---
name: tauri-desktop
description: Tauri v2 + Svelte 5 desktop app scaffold — call API, don't duplicate
---

## Tauri Desktop App

### Location
`app/` — Tauri v2 + Svelte 5 desktop scaffold (not fully built yet)

### Stack
- **Frontend:** Svelte 5 with runes syntax (`$state`, `$derived`, `$effect`)
- **Backend:** Rust (Tauri v2) for native desktop functionality
- **Communication:** HTTP API calls to Python backend or Tauri IPC

### Svelte 5 Runes
```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);

  $effect(() => {
    console.log(`Count is ${count}`);
  });
</script>

<button onclick={() => count++}>{count} (doubled: {doubled})</button>
```

### Rules
- Do NOT duplicate Python backend logic in Rust — call the API instead
- Use Tauri v2 APIs for native features (file system, notifications, etc.)
- Communicate with Python backend via HTTP or IPC
- This is a scaffold — add features incrementally
