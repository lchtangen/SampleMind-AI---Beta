<script lang="ts">
  import { onMount } from 'svelte';
  import { getLibrary } from '$lib/commands';

  let { children } = $props();

  // Nav items wired to route slugs
  const navItems = [
    { label: 'Library', href: '/' },
    { label: 'Search', href: '/search' },
    { label: 'Generate', href: '/generate' },
    { label: 'Analytics', href: '/analytics' },
    { label: 'Marketplace', href: '/marketplace' },
  ];
</script>

<div class="app-shell">
  <nav class="sidebar">
    <div class="logo">
      <span class="logo-mark">SM</span>
      <span class="logo-text">SampleMind</span>
    </div>
    <ul class="nav-list">
      {#each navItems as item}
        <li><a href={item.href} class="nav-link">{item.label}</a></li>
      {/each}
    </ul>
    <div class="sidebar-footer">
      <span class="version">v0.3.0</span>
    </div>
  </nav>

  <main class="content">
    {@render children()}
  </main>
</div>

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; margin: 0; padding: 0; }
  :global(body) { font-family: 'Inter', system-ui, sans-serif; background: #0d0d0f; color: #e2e8f0; }

  .app-shell { display: flex; height: 100vh; overflow: hidden; }

  .sidebar {
    width: 200px;
    min-width: 200px;
    background: #111114;
    border-right: 1px solid #1e1e24;
    display: flex;
    flex-direction: column;
    padding: 1.5rem 1rem;
    gap: 2rem;
  }

  .logo { display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.5rem; }
  .logo-mark {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.75rem; color: white;
  }
  .logo-text { font-weight: 700; font-size: 1rem; color: #f1f5f9; }

  .nav-list { list-style: none; display: flex; flex-direction: column; gap: 0.25rem; flex: 1; }
  .nav-link {
    display: block;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    color: #94a3b8;
    text-decoration: none;
    font-size: 0.875rem;
    transition: background 0.15s, color 0.15s;
  }
  .nav-link:hover { background: #1e1e2e; color: #e2e8f0; }

  .sidebar-footer { padding-top: 1rem; border-top: 1px solid #1e1e24; }
  .version { font-size: 0.75rem; color: #475569; }

  .content { flex: 1; overflow-y: auto; padding: 2rem; }
</style>
