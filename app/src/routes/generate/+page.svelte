<script lang="ts">
  import { generateSample, type GenerateResult } from '$lib/commands';

  let prompt = $state('');
  let durationS = $state(4.0);
  let bpm = $state<number | undefined>(undefined);
  let key = $state('');
  let result = $state<GenerateResult | null>(null);
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function generate() {
    if (!prompt.trim()) return;
    loading = true; error = null; result = null;
    try {
      result = await generateSample(
        prompt.trim(),
        durationS,
        bpm || undefined,
        key.trim() || undefined,
      );
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }
</script>

<div class="page">
  <h1 class="page-title">AI Generation</h1>
  <p class="subtitle">Generate audio samples from text using Meta MusicGen.</p>

  <form class="gen-form" onsubmit={(e) => { e.preventDefault(); generate(); }}>
    <label class="field">
      <span class="label">Prompt</span>
      <input
        type="text"
        placeholder="dark trap hi-hat loop, punchy 808 bass…"
        bind:value={prompt}
        class="input"
      />
    </label>

    <div class="row">
      <label class="field">
        <span class="label">Duration (seconds)</span>
        <input type="number" min="1" max="30" step="0.5" bind:value={durationS} class="input sm" />
      </label>
      <label class="field">
        <span class="label">BPM (optional)</span>
        <input type="number" min="60" max="220" placeholder="140" bind:value={bpm} class="input sm" />
      </label>
      <label class="field">
        <span class="label">Key (optional)</span>
        <input type="text" placeholder="Am" maxlength="4" bind:value={key} class="input sm" />
      </label>
    </div>

    <button type="submit" disabled={loading || !prompt.trim()} class="gen-btn">
      {loading ? 'Generating…' : 'Generate Sample'}
    </button>
  </form>

  {#if error}
    <div class="error-box">{error}</div>
  {/if}

  {#if result}
    <div class="result-card">
      <div class="result-header">
        <span class="result-label">Generated</span>
        {#if result.is_mock}<span class="mock-badge">Mock (no GPU)</span>{/if}
      </div>
      <p class="result-path">{result.file_path}</p>
      <div class="result-meta">
        <span>{result.duration_s}s</span>
        <span>·</span>
        <span>{result.model_used}</span>
        <span>·</span>
        <span>{result.prompt}</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .page { max-width: 700px; }
  .page-title { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; color: #f1f5f9; }
  .subtitle { color: #64748b; font-size: 0.875rem; margin-bottom: 2rem; }

  .gen-form { display: flex; flex-direction: column; gap: 1.25rem; }
  .field { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
  .label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
  .input {
    background: #111114;
    border: 1px solid #1e1e24;
    border-radius: 8px;
    padding: 0.65rem 0.875rem;
    color: #e2e8f0;
    font-size: 0.875rem;
    outline: none;
    width: 100%;
  }
  .input.sm { max-width: 160px; }
  .input:focus { border-color: #6366f1; }
  .row { display: flex; gap: 1rem; flex-wrap: wrap; }

  .gen-btn {
    padding: 0.75rem 2rem;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    align-self: flex-start;
  }
  .gen-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .error-box {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: #1a0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    color: #f87171;
    font-size: 0.875rem;
  }

  .result-card {
    margin-top: 1.5rem;
    background: #0d1f12;
    border: 1px solid #166534;
    border-radius: 12px;
    padding: 1.25rem;
  }
  .result-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
  .result-label { font-weight: 600; color: #34d399; font-size: 0.875rem; }
  .mock-badge { font-size: 0.7rem; color: #fbbf24; background: #292524; padding: 0.15rem 0.5rem; border-radius: 999px; }
  .result-path { font-family: monospace; font-size: 0.8rem; color: #94a3b8; word-break: break-all; margin-bottom: 0.5rem; }
  .result-meta { display: flex; gap: 0.5rem; font-size: 0.75rem; color: #64748b; }
</style>
