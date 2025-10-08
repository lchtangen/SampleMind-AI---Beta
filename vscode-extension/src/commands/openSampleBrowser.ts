/**
 * Open Sample Browser Command
 */

import * as vscode from 'vscode';
import { SampleMindAPI } from '../utils/api';

export async function openSampleBrowserCommand(
  context: vscode.ExtensionContext,
  api: SampleMindAPI
): Promise<void> {
  // Focus on the sample explorer view
  await vscode.commands.executeCommand('samplemindExplorer.focus');

  vscode.window.showInformationMessage(
    'Sample Browser opened. Configure sample folders in settings to get started.',
    'Add Folder',
    'Open Settings'
  ).then((selection) => {
    if (selection === 'Add Folder') {
      vscode.commands.executeCommand('samplemind.addSampleFolder');
    } else if (selection === 'Open Settings') {
      vscode.commands.executeCommand('samplemind.openSettings');
    }
  });
}
