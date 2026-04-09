<script lang="ts">
  import { searchSemantic, type SampleResult } from '$lib/commands';

  let query = $state('');
  let results = $state<SampleResult[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let searched = $state(false);

  async function doSearch() {
    if (!query.trim()) return;
    loading = true;
    error = null;
    try {
      results = await searchSemantic(query.trim(), 20);
      searched = true;
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') doSearch();
  }

  function energyColor(energy?: string) {
    switch (energy?.toLowerCase()) {
      case 'high': return '#f87171';
      case 'mid': return '#34d399';
      case 'low': return '#60a5fa';
      default: return '#94a3b8';
    }
  }
</script>

<div class="page">
  <h1 class="page-title">Semantic Search</h1>

  <div class="search-bar">
    <input
      type="text"
      placeholder="Search by sound: 'dark trap kick', 'ambient pad C minor'…"
      bind:value={query}
      onkeydown={onKeydown}
      class="search-input"
    />
    <button onclick={doSearch} disabled={loading} class="search-btn">
      {loading ? 'Searching…' : 'Search'}
    </button>
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if searched && results.length === 0 && !loading}
    <p class="muted">No results found. Try rebuilding the index: <code>samplemind index rebuild</code></p>
  {/if}

  {#if results.length > 0}
    <div class="results-list">
      {#each results as result, i}
        <div class="result-row">
          <span class="rank">#{i + 1}</span>
          <div class="result-info">
            <span class="filename">{result.filename}</span>
            <div class="meta">
              {#if result.bpm}<span class="badge">{result.bpm} BPM</span>{/if}
              {#if result.key}<span class="badge key">{result.key}</span>{/if}
              {#if result.energy}
                <span class="badge energy" style="color: {energyColor(result.energy)}">{result.energy}</span>
              {/if}
              {#each (result.genre_labels ?? []).slice(0, 3) as g}
                <span class="badge genre">{g}</span>
              {/each}
            </div>
          </div>
          {#if result.score !== undefined}
            <span class="score">{(result.score * 100).toFixed(1)}%</span>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .page { max-width: 900px; }
  .page-title { font-size: 1.75rem; font-weight: 700; margin-bottom: 1.5rem; color: #f1f5f9; }

  .search-bar { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }
  .search-input {
    flex: 1;
    background: #111114;
    border: 1px solid #1e1e24;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #e2e8f0;
    font-size: 0.875rem;
    outline: none;
  }
  .search-input:focus { border-color: #6366f1; }
  .search-btn {
    padding: 0.75rem 1.5rem;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.875rem;
  }
  .search-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .results-list { display: flex; flex-direction: column; gap: 0.5rem; }
  .result-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #111114;
    border: 1px solid #1e1e24;
    border-radius: 8px;
    padding: 0.75rem 1rem;
  }
  .rank { color: #475569; font-size: 0.75rem; min-width: 2rem; }
  .result-info { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
  .filename { font-size: 0.875rem; color: #e2e8f0; font-weight: 500; }
  .meta { display: flex; flex-wrap: wrap; gap: 0.35rem; }
  .badge {
    padding: 0.1rem 0.5rem;
    border-radius: 999px;
    font-size: 0.7rem;
    background: #1e1e2e;
    color: #94a3b8;
  }
  .badge.key { color: #34d399; }
  .badge.genre { color: #c4b5fd; }
  .score { font-size: 0.75rem; color: #6366f1; font-weight: 600; min-width: 3rem; text-align: right; }
  .error { color: #f87171; font-size: 0.875rem; margin-bottom: 1rem; }
  .muted { color: #475569; font-size: 0.875rem; }
  .muted code { color: #a78bfa; }
</style>
