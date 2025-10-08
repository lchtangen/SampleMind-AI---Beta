/**
 * Analysis Results Tree Data Provider
 *
 * Displays audio analysis results in a tree view
 */

import * as vscode from 'vscode';
import { SampleMindAPI } from '../utils/api';

export class AnalysisItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly value?: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
  ) {
    super(label, collapsibleState);

    if (value) {
      this.description = value;
    }

    this.iconPath = new vscode.ThemeIcon('pulse');
  }
}

export class AnalysisProvider implements vscode.TreeDataProvider<AnalysisItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<AnalysisItem | undefined | null | void> =
    new vscode.EventEmitter<AnalysisItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<AnalysisItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  private currentAnalysis: any = null;
  private currentFileName: string = '';

  constructor(
    private context: vscode.ExtensionContext,
    private api: SampleMindAPI
  ) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  setAnalysis(fileName: string, analysis: any): void {
    this.currentFileName = fileName;
    this.currentAnalysis = analysis;
    this.refresh();
  }

  clearAnalysis(): void {
    this.currentFileName = '';
    this.currentAnalysis = null;
    this.refresh();
  }

  getTreeItem(element: AnalysisItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: AnalysisItem): Promise<AnalysisItem[]> {
    if (!this.currentAnalysis) {
      return [new AnalysisItem('No analysis available')];
    }

    if (!element) {
      // Root level
      return [
        new AnalysisItem('File', this.currentFileName),
        new AnalysisItem(
          'Features',
          undefined,
          vscode.TreeItemCollapsibleState.Expanded
        ),
      ];
    }

    if (element.label === 'Features') {
      const features = this.currentAnalysis.features;
      const items: AnalysisItem[] = [];

      if (features.tempo !== undefined) {
        items.push(new AnalysisItem('Tempo', `${features.tempo.toFixed(1)} BPM`));
      }

      if (features.key) {
        items.push(new AnalysisItem('Key', features.key));
      }

      if (features.energy !== undefined) {
        items.push(
          new AnalysisItem('Energy', `${(features.energy * 100).toFixed(0)}%`)
        );
      }

      if (features.spectral_features) {
        const spectral = features.spectral_features;
        if (spectral.centroid !== undefined) {
          items.push(
            new AnalysisItem('Spectral Centroid', `${spectral.centroid.toFixed(0)} Hz`)
          );
        }
        if (spectral.rolloff !== undefined) {
          items.push(
            new AnalysisItem('Spectral Rolloff', `${spectral.rolloff.toFixed(0)} Hz`)
          );
        }
        if (spectral.brightness !== undefined) {
          items.push(
            new AnalysisItem(
              'Brightness',
              `${(spectral.brightness * 100).toFixed(0)}%`
            )
          );
        }
      }

      if (features.rhythm_features) {
        const rhythm = features.rhythm_features;
        if (rhythm.onset_strength !== undefined) {
          items.push(
            new AnalysisItem(
              'Onset Strength',
              `${(rhythm.onset_strength * 100).toFixed(0)}%`
            )
          );
        }
        if (rhythm.beats !== undefined) {
          items.push(new AnalysisItem('Beats Detected', `${rhythm.beats.length}`));
        }
      }

      return items;
    }

    return [];
  }
}
