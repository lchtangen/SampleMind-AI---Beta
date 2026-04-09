<script lang="ts">
  import { onMount } from 'svelte';
  import { getLibrary, type LibrarySummary } from '$lib/commands';

  let summary = $state<LibrarySummary | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  onMount(async () => {
    try {
      summary = await getLibrary();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="page">
  <h1 class="page-title">Library</h1>

  {#if loading}
    <p class="muted">Loading library stats…</p>
  {:else if error}
    <p class="error">Could not connect to SampleMind server: {error}</p>
    <p class="muted hint">Make sure <code>python main.py</code> is running.</p>
  {:else if summary}
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">{summary.total_samples.toLocaleString()}</span>
        <span class="stat-label">Total Samples</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{summary.unique_genres ?? '—'}</span>
        <span class="stat-label">Unique Genres</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{summary.unique_keys ?? '—'}</span>
        <span class="stat-label">Unique Keys</span>
      </div>
    </div>

    {#if summary.top_genres.length}
      <section class="section">
        <h2 class="section-title">Top Genres</h2>
        <div class="tag-list">
          {#each summary.top_genres as genre}
            <span class="tag">{genre}</span>
          {/each}
        </div>
      </section>
    {/if}

    {#if summary.top_keys.length}
      <section class="section">
        <h2 class="section-title">Top Keys</h2>
        <div class="tag-list">
          {#each summary.top_keys as key}
            <span class="tag key-tag">{key}</span>
          {/each}
        </div>
      </section>
    {/if}

    {#if !summary.indexed}
      <div class="notice">
        <strong>Index not built.</strong> Run <code>samplemind index rebuild</code> to enable semantic search and analytics.
      </div>
    {/if}
  {/if}
</div>

<style>
  .page { max-width: 900px; }
  .page-title { font-size: 1.75rem; font-weight: 700; margin-bottom: 1.5rem; color: #f1f5f9; }

  .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem; }
  .stat-card {
    background: #111114;
    border: 1px solid #1e1e24;
    border-radius: 12px;
    padding: 1.25rem;
    display: flex; flex-direction: column; gap: 0.25rem;
  }
  .stat-value { font-size: 2rem; font-weight: 700; color: #a78bfa; }
  .stat-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }

  .section { margin-top: 1.5rem; }
  .section-title { font-size: 0.875rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }

  .tag-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .tag { padding: 0.25rem 0.75rem; background: #1e1e2e; border-radius: 999px; font-size: 0.8rem; color: #c4b5fd; }
  .key-tag { color: #34d399; background: #0d2417; }

  .notice {
    margin-top: 2rem;
    padding: 1rem 1.25rem;
    background: #1a1a2e;
    border: 1px solid #312e81;
    border-radius: 8px;
    font-size: 0.875rem;
    color: #a5b4fc;
  }
  .notice code { background: #312e81; padding: 0.1rem 0.4rem; border-radius: 4px; font-family: monospace; }

  .muted { color: #475569; font-size: 0.875rem; }
  .hint { margin-top: 0.5rem; }
  .hint code { color: #a78bfa; }
  .error { color: #f87171; font-size: 0.875rem; margin-bottom: 0.5rem; }
</style>
