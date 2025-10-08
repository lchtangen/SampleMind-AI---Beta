/**
 * Analyze Audio Command
 *
 * Analyzes an audio file using the SampleMind AI API
 */

import * as vscode from 'vscode';
import { SampleMindAPI } from '../utils/api';
import { AnalysisWebViewProvider } from '../views/AnalysisWebView';

export async function analyzeAudioCommand(
  api: SampleMindAPI,
  webViewProvider: AnalysisWebViewProvider,
  uri?: vscode.Uri
): Promise<void> {
  // Get file URI
  let fileUri = uri;

  if (!fileUri) {
    // If no URI provided, ask user to select a file
    const selected = await vscode.window.showOpenDialog({
      canSelectFiles: true,
      canSelectFolders: false,
      canSelectMany: false,
      filters: {
        'Audio Files': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg'],
      },
      title: 'Select Audio File to Analyze',
    });

    if (!selected || selected.length === 0) {
      return;
    }

    fileUri = selected[0];
  }

  const filePath = fileUri.fsPath;
  const fileName = filePath.split('/').pop() || 'Unknown';

  // Check API health
  const isHealthy = await api.checkHealth();
  if (!isHealthy) {
    vscode.window.showErrorMessage(
      'Cannot connect to SampleMind AI API. Please check your settings and ensure the API server is running.',
      'Open Settings'
    ).then((selection) => {
      if (selection === 'Open Settings') {
        vscode.commands.executeCommand('samplemind.openSettings');
      }
    });
    return;
  }

  // Get analysis level from config
  const config = vscode.workspace.getConfiguration('samplemind');
  const level = config.get<string>('analysisLevel', 'STANDARD');

  // Show progress
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Analyzing ${fileName}...`,
      cancellable: false,
    },
    async (progress) => {
      try {
        progress.report({ increment: 0, message: 'Uploading file...' });

        const result = await api.analyzeAudio(filePath, level);

        progress.report({ increment: 50, message: 'Processing results...' });

        // Show results
        const features = result.features;
        const message = [
          `Analysis complete for ${fileName}`,
          `Tempo: ${features.tempo.toFixed(1)} BPM`,
          `Key: ${features.key}`,
          `Energy: ${(features.energy * 100).toFixed(0)}%`,
        ].join('\n');

        progress.report({ increment: 100, message: 'Done!' });

        // Show WebView with visualization
        await webViewProvider.showAnalysis(filePath, result);

        // Show notification if enabled
        if (config.get<boolean>('enableNotifications', true)) {
          vscode.window.showInformationMessage(
            `✓ Analysis complete: ${fileName}`,
            'View Details',
            'Copy Data'
          ).then((selection) => {
            if (selection === 'View Details') {
              // Re-show WebView
              webViewProvider.showAnalysis(filePath, result);
            } else if (selection === 'Copy Data') {
              vscode.env.clipboard.writeText(JSON.stringify(result, null, 2));
              vscode.window.showInformationMessage('Analysis data copied to clipboard');
            }
          });
        }

        // Cache results in Sample Explorer
        vscode.commands.executeCommand('_samplemind.cacheAnalysis', filePath, result);

      } catch (error: any) {
        vscode.window.showErrorMessage(
          `Analysis failed: ${error.message || 'Unknown error'}`,
          'Retry',
          'Open Settings'
        ).then((selection) => {
          if (selection === 'Retry') {
            analyzeAudioCommand(api, webViewProvider, fileUri);
          } else if (selection === 'Open Settings') {
            vscode.commands.executeCommand('samplemind.openSettings');
          }
        });
      }
    }
  );
}
