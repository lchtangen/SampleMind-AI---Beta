/**
 * Analysis WebView Provider
 *
 * Displays audio analysis with waveform and charts in a VSCode WebView panel
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { SampleMindAPI } from '../utils/api';

export class AnalysisWebViewProvider {
  private static readonly viewType = 'samplemind.analysisView';
  private panel: vscode.WebviewPanel | undefined;

  constructor(
    private readonly context: vscode.ExtensionContext,
    private readonly api: SampleMindAPI
  ) {}

  public async showAnalysis(filePath: string, analysisData: any): Promise<void> {
    const fileName = path.basename(filePath);

    if (this.panel) {
      // If panel exists, reveal it and update content
      this.panel.reveal(vscode.ViewColumn.Two);
      this.updateWebView(fileName, analysisData);
    } else {
      // Create new panel
      this.panel = vscode.window.createWebviewPanel(
        AnalysisWebViewProvider.viewType,
        `Analysis: ${fileName}`,
        vscode.ViewColumn.Two,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
          localResourceRoots: [
            vscode.Uri.file(path.join(this.context.extensionPath, 'media')),
          ],
        }
      );

      // Set initial content
      this.updateWebView(fileName, analysisData);

      // Handle panel disposal
      this.panel.onDidDispose(() => {
        this.panel = undefined;
      });

      // Handle messages from webview
      this.panel.webview.onDidReceiveMessage(
        (message) => {
          switch (message.command) {
            case 'reanalyze':
              vscode.commands.executeCommand('samplemind.analyzeAudio', vscode.Uri.file(filePath));
              break;
            case 'export':
              this.exportAnalysis(fileName, analysisData);
              break;
          }
        },
        undefined,
        this.context.subscriptions
      );
    }
  }

  private updateWebView(fileName: string, analysisData: any): void {
    if (!this.panel) return;

    this.panel.title = `Analysis: ${fileName}`;
    this.panel.webview.html = this.getWebViewContent(fileName, analysisData);
  }

  private getWebViewContent(fileName: string, analysisData: any): string {
    const features = analysisData.features || {};
    const spectral = features.spectral_features || {};
    const rhythm = features.rhythm_features || {};

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audio Analysis</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      padding: 20px;
      line-height: 1.6;
    }

    .header {
      border-bottom: 1px solid var(--vscode-widget-border);
      padding-bottom: 15px;
      margin-bottom: 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header h1 {
      font-size: 24px;
      font-weight: 600;
      color: var(--vscode-foreground);
    }

    .header .file-name {
      font-size: 14px;
      color: var(--vscode-descriptionForeground);
      margin-top: 5px;
    }

    .actions {
      display: flex;
      gap: 10px;
    }

    .btn {
      padding: 8px 16px;
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      transition: background 0.2s;
    }

    .btn:hover {
      background: var(--vscode-button-hoverBackground);
    }

    .btn-secondary {
      background: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }

    .btn-secondary:hover {
      background: var(--vscode-button-secondaryHoverBackground);
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }

    .metric-card {
      background: var(--vscode-editor-inactiveSelectionBackground);
      border: 1px solid var(--vscode-widget-border);
      border-radius: 8px;
      padding: 20px;
      text-align: center;
    }

    .metric-label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--vscode-descriptionForeground);
      margin-bottom: 8px;
      font-weight: 600;
    }

    .metric-value {
      font-size: 32px;
      font-weight: 700;
      color: var(--vscode-charts-blue);
      margin-bottom: 4px;
    }

    .metric-unit {
      font-size: 13px;
      color: var(--vscode-descriptionForeground);
    }

    .section {
      margin-bottom: 30px;
    }

    .section-title {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 15px;
      color: var(--vscode-foreground);
      border-bottom: 2px solid var(--vscode-charts-blue);
      padding-bottom: 8px;
    }

    .features-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 10px;
    }

    .feature-item {
      background: var(--vscode-editor-inactiveSelectionBackground);
      border-left: 3px solid var(--vscode-charts-green);
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 4px;
    }

    .feature-label {
      font-size: 13px;
      color: var(--vscode-foreground);
      font-weight: 500;
    }

    .feature-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--vscode-charts-blue);
    }

    .waveform-placeholder {
      background: var(--vscode-editor-inactiveSelectionBackground);
      border: 2px dashed var(--vscode-widget-border);
      border-radius: 8px;
      padding: 60px 20px;
      text-align: center;
      color: var(--vscode-descriptionForeground);
      margin-bottom: 30px;
    }

    .waveform-placeholder svg {
      width: 100%;
      height: 80px;
      opacity: 0.3;
    }

    .chart-container {
      background: var(--vscode-editor-inactiveSelectionBackground);
      border: 1px solid var(--vscode-widget-border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
    }

    .bar {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
    }

    .bar-label {
      width: 140px;
      font-size: 13px;
      color: var(--vscode-foreground);
    }

    .bar-track {
      flex: 1;
      height: 24px;
      background: var(--vscode-input-background);
      border-radius: 4px;
      overflow: hidden;
      position: relative;
    }

    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--vscode-charts-blue), var(--vscode-charts-purple));
      transition: width 0.5s ease;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 8px;
    }

    .bar-value {
      color: white;
      font-size: 11px;
      font-weight: 600;
    }

    .timestamp {
      text-align: center;
      padding-top: 20px;
      border-top: 1px solid var(--vscode-widget-border);
      color: var(--vscode-descriptionForeground);
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>Audio Analysis</h1>
      <div class="file-name">${fileName}</div>
    </div>
    <div class="actions">
      <button class="btn btn-secondary" onclick="reanalyze()">Re-analyze</button>
      <button class="btn" onclick="exportData()">Export JSON</button>
    </div>
  </div>

  <!-- Key Metrics -->
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-label">Tempo</div>
      <div class="metric-value">${features.tempo?.toFixed(1) || 'N/A'}</div>
      <div class="metric-unit">BPM</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Key</div>
      <div class="metric-value">${features.key || 'N/A'}</div>
      <div class="metric-unit">Musical Key</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Energy</div>
      <div class="metric-value">${((features.energy || 0) * 100).toFixed(0)}</div>
      <div class="metric-unit">%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Brightness</div>
      <div class="metric-value">${((spectral.centroid || 0) / 1000).toFixed(1)}</div>
      <div class="metric-unit">kHz</div>
    </div>
  </div>

  <!-- Waveform Placeholder -->
  <div class="section">
    <div class="section-title">Waveform</div>
    <div class="waveform-placeholder">
      <svg viewBox="0 0 1000 80" fill="currentColor">
        ${Array.from({ length: 100 }, (_, i) => {
          const height = Math.random() * 60 + 10;
          const y = (80 - height) / 2;
          return `<rect x="${i * 10}" y="${y}" width="8" height="${height}" rx="2" />`;
        }).join('')}
      </svg>
      <div style="margin-top: 15px;">Waveform visualization</div>
    </div>
  </div>

  <!-- Analysis Charts -->
  <div class="section">
    <div class="section-title">Feature Analysis</div>
    <div class="chart-container">
      <div class="bar">
        <div class="bar-label">Tempo</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${Math.min(((features.tempo || 0) / 200) * 100, 100)}%">
            <span class="bar-value">${features.tempo?.toFixed(0) || '0'} BPM</span>
          </div>
        </div>
      </div>
      <div class="bar">
        <div class="bar-label">Energy</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${((features.energy || 0) * 100)}%">
            <span class="bar-value">${((features.energy || 0) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
      <div class="bar">
        <div class="bar-label">Spectral Centroid</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${Math.min(((spectral.centroid || 0) / 10000) * 100, 100)}%">
            <span class="bar-value">${(spectral.centroid || 0).toFixed(0)} Hz</span>
          </div>
        </div>
      </div>
      ${spectral.brightness !== undefined ? `
      <div class="bar">
        <div class="bar-label">Brightness</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${((spectral.brightness || 0) * 100)}%">
            <span class="bar-value">${((spectral.brightness || 0) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
      ` : ''}
    </div>
  </div>

  <!-- Detailed Features -->
  <div class="section">
    <div class="section-title">Spectral Features</div>
    <div class="features-list">
      ${spectral.centroid !== undefined ? `
      <div class="feature-item">
        <span class="feature-label">Spectral Centroid</span>
        <span class="feature-value">${spectral.centroid.toFixed(0)} Hz</span>
      </div>
      ` : ''}
      ${spectral.rolloff !== undefined ? `
      <div class="feature-item">
        <span class="feature-label">Spectral Rolloff</span>
        <span class="feature-value">${spectral.rolloff.toFixed(0)} Hz</span>
      </div>
      ` : ''}
      ${spectral.bandwidth !== undefined ? `
      <div class="feature-item">
        <span class="feature-label">Bandwidth</span>
        <span class="feature-value">${spectral.bandwidth.toFixed(0)} Hz</span>
      </div>
      ` : ''}
      ${spectral.flatness !== undefined ? `
      <div class="feature-item">
        <span class="feature-label">Spectral Flatness</span>
        <span class="feature-value">${(spectral.flatness * 100).toFixed(1)}%</span>
      </div>
      ` : ''}
    </div>
  </div>

  ${rhythm.beats ? `
  <div class="section">
    <div class="section-title">Rhythm Features</div>
    <div class="features-list">
      <div class="feature-item">
        <span class="feature-label">Beats Detected</span>
        <span class="feature-value">${rhythm.beats.length}</span>
      </div>
      ${rhythm.onset_strength !== undefined ? `
      <div class="feature-item">
        <span class="feature-label">Onset Strength</span>
        <span class="feature-value">${(rhythm.onset_strength * 100).toFixed(0)}%</span>
      </div>
      ` : ''}
    </div>
  </div>
  ` : ''}

  <div class="timestamp">
    Analysis ID: ${analysisData.analysis_id || 'N/A'}
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    function reanalyze() {
      vscode.postMessage({ command: 'reanalyze' });
    }

    function exportData() {
      vscode.postMessage({ command: 'export' });
    }
  </script>
</body>
</html>`;
  }

  private async exportAnalysis(fileName: string, analysisData: any): Promise<void> {
    const saveUri = await vscode.window.showSaveDialog({
      defaultUri: vscode.Uri.file(`${fileName.replace(/\.[^.]+$/, '')}-analysis.json`),
      filters: {
        'JSON': ['json'],
      },
    });

    if (saveUri) {
      const jsonContent = JSON.stringify(analysisData, null, 2);
      await vscode.workspace.fs.writeFile(saveUri, Buffer.from(jsonContent, 'utf8'));
      vscode.window.showInformationMessage(`Analysis exported to ${saveUri.fsPath}`);
    }
  }

  public dispose(): void {
    if (this.panel) {
      this.panel.dispose();
    }
  }
}
