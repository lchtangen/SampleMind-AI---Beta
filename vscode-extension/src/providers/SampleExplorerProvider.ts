/**
 * Sample Explorer Tree Data Provider
 *
 * Displays audio samples in a tree view
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { SampleMindAPI } from '../utils/api';

export class SampleItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly resourceUri?: vscode.Uri,
    public readonly isAudioFile: boolean = false,
    public readonly analysis?: any
  ) {
    super(label, collapsibleState);

    if (resourceUri) {
      this.resourceUri = resourceUri;
      this.tooltip = resourceUri.fsPath;
    }

    if (isAudioFile) {
      this.contextValue = 'audioFile';
      this.iconPath = new vscode.ThemeIcon('file-media');
      this.command = {
        command: 'vscode.open',
        title: 'Open Audio File',
        arguments: [resourceUri],
      };

      if (analysis) {
        this.description = `${analysis.tempo.toFixed(0)} BPM, ${analysis.key}`;
      }
    } else {
      this.contextValue = 'folder';
      this.iconPath = new vscode.ThemeIcon('folder');
    }
  }
}

export class SampleExplorerProvider implements vscode.TreeDataProvider<SampleItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<SampleItem | undefined | null | void> =
    new vscode.EventEmitter<SampleItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<SampleItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  private analysisCache: Map<string, any> = new Map();

  constructor(
    private context: vscode.ExtensionContext,
    private api: SampleMindAPI
  ) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: SampleItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: SampleItem): Promise<SampleItem[]> {
    if (!element) {
      // Root level: show configured sample folders
      const config = vscode.workspace.getConfiguration('samplemind');
      const folders = config.get<string[]>('sampleFolders', []);

      if (folders.length === 0) {
        return [];
      }

      return folders.map((folder) => {
        const folderName = path.basename(folder);
        return new SampleItem(
          folderName,
          vscode.TreeItemCollapsibleState.Collapsed,
          vscode.Uri.file(folder),
          false
        );
      });
    } else {
      // Show folder contents
      if (element.resourceUri) {
        return this.getDirectoryContents(element.resourceUri.fsPath);
      }
      return [];
    }
  }

  private async getDirectoryContents(dirPath: string): Promise<SampleItem[]> {
    try {
      const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
      const items: SampleItem[] = [];

      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);

        if (entry.isDirectory()) {
          items.push(
            new SampleItem(
              entry.name,
              vscode.TreeItemCollapsibleState.Collapsed,
              vscode.Uri.file(fullPath),
              false
            )
          );
        } else if (this.isAudioFile(entry.name)) {
          // Check if we have cached analysis
          const analysis = this.analysisCache.get(fullPath);

          items.push(
            new SampleItem(
              entry.name,
              vscode.TreeItemCollapsibleState.None,
              vscode.Uri.file(fullPath),
              true,
              analysis
            )
          );
        }
      }

      // Sort: folders first, then files alphabetically
      items.sort((a, b) => {
        if (a.isAudioFile === b.isAudioFile) {
          return a.label.localeCompare(b.label);
        }
        return a.isAudioFile ? 1 : -1;
      });

      return items;
    } catch (error) {
      vscode.window.showErrorMessage(`Error reading directory: ${error}`);
      return [];
    }
  }

  private isAudioFile(fileName: string): boolean {
    const audioExtensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'];
    const ext = path.extname(fileName).toLowerCase();
    return audioExtensions.includes(ext);
  }

  public cacheAnalysis(filePath: string, analysis: any): void {
    this.analysisCache.set(filePath, analysis);
    this.refresh();
  }
}
