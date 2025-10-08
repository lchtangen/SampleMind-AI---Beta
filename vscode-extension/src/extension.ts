/**
 * SampleMind AI - VSCode Extension
 *
 * AI-powered audio analysis and sample management for VSCode
 */

import * as vscode from 'vscode';
import { analyzeAudioCommand } from './commands/analyzeAudio';
import { generateMusicCommand } from './commands/generateMusic';
import { openSampleBrowserCommand } from './commands/openSampleBrowser';
import { refreshSamplesCommand } from './commands/refreshSamples';
import { AnalysisProvider } from './providers/AnalysisProvider';
import { SampleExplorerProvider } from './providers/SampleExplorerProvider';
import { SampleMindAPI } from './utils/api';
import { AnalysisWebViewProvider } from './views/AnalysisWebView';

let sampleExplorerProvider: SampleExplorerProvider;
let analysisProvider: AnalysisProvider;
let analysisWebViewProvider: AnalysisWebViewProvider;
let api: SampleMindAPI;

export function activate(context: vscode.ExtensionContext) {
  console.log('SampleMind AI extension is now active');

  // Initialize API client
  const config = vscode.workspace.getConfiguration('samplemind');
  const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
  api = new SampleMindAPI(apiUrl);

  // Create tree data providers
  sampleExplorerProvider = new SampleExplorerProvider(context, api);
  analysisProvider = new AnalysisProvider(context, api);
  analysisWebViewProvider = new AnalysisWebViewProvider(context, api);

  // Register tree views
  const sampleExplorerView = vscode.window.createTreeView('samplemindExplorer', {
    treeDataProvider: sampleExplorerProvider,
    showCollapseAll: true,
  });

  const analysisView = vscode.window.createTreeView('samplemindAnalysis', {
    treeDataProvider: analysisProvider,
    showCollapseAll: true,
  });

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.analyzeAudio',
      (uri?: vscode.Uri) => analyzeAudioCommand(api, analysisWebViewProvider, uri)
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.generateMusic',
      () => generateMusicCommand(api)
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.refreshSamples',
      () => refreshSamplesCommand(sampleExplorerProvider)
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.openSampleBrowser',
      () => openSampleBrowserCommand(context, api)
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.openSettings',
      () => {
        vscode.commands.executeCommand(
          'workbench.action.openSettings',
          'samplemind'
        );
      }
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      'samplemind.addSampleFolder',
      async () => {
        const folderUri = await vscode.window.showOpenDialog({
          canSelectFolders: true,
          canSelectFiles: false,
          canSelectMany: false,
          title: 'Select Sample Folder',
        });

        if (folderUri && folderUri[0]) {
          const config = vscode.workspace.getConfiguration('samplemind');
          const folders = config.get<string[]>('sampleFolders', []);
          folders.push(folderUri[0].fsPath);
          await config.update('sampleFolders', folders, vscode.ConfigurationTarget.Global);
          sampleExplorerProvider.refresh();
          vscode.window.showInformationMessage(`Added sample folder: ${folderUri[0].fsPath}`);
        }
      }
    )
  );

  // Register context subscriptions
  context.subscriptions.push(sampleExplorerView);
  context.subscriptions.push(analysisView);

  // Watch for configuration changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('samplemind.apiUrl')) {
        const newUrl = vscode.workspace.getConfiguration('samplemind').get<string>('apiUrl');
        if (newUrl) {
          api.setBaseUrl(newUrl);
          vscode.window.showInformationMessage('SampleMind API URL updated');
        }
      }
      if (e.affectsConfiguration('samplemind.sampleFolders')) {
        sampleExplorerProvider.refresh();
      }
    })
  );

  // Watch for file system changes
  const watcher = vscode.workspace.createFileSystemWatcher(
    '**/*.{mp3,wav,flac,m4a,aac,ogg}'
  );

  watcher.onDidCreate(() => sampleExplorerProvider.refresh());
  watcher.onDidDelete(() => sampleExplorerProvider.refresh());
  watcher.onDidChange(() => sampleExplorerProvider.refresh());

  context.subscriptions.push(watcher);

  // Auto-analyze on file open if enabled
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(async (document) => {
      const config = vscode.workspace.getConfiguration('samplemind');
      const autoAnalyze = config.get<boolean>('autoAnalyze', false);

      if (autoAnalyze && isAudioFile(document.uri.fsPath)) {
        await analyzeAudioCommand(api, analysisWebViewProvider, document.uri);
      }
    })
  );

  // Show welcome message
  vscode.window.showInformationMessage(
    'SampleMind AI is ready! Right-click on audio files to analyze them.',
    'Open Settings',
    'View Samples'
  ).then((selection) => {
    if (selection === 'Open Settings') {
      vscode.commands.executeCommand('samplemind.openSettings');
    } else if (selection === 'View Samples') {
      vscode.commands.executeCommand('samplemind.openSampleBrowser');
    }
  });
}

export function deactivate() {
  console.log('SampleMind AI extension is now deactivated');
}

function isAudioFile(filePath: string): boolean {
  const audioExtensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'];
  return audioExtensions.some((ext) => filePath.toLowerCase().endsWith(ext));
}
