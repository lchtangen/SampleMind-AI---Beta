/**
 * Refresh Samples Command
 */

import * as vscode from 'vscode';
import { SampleExplorerProvider } from '../providers/SampleExplorerProvider';

export async function refreshSamplesCommand(
  provider: SampleExplorerProvider
): Promise<void> {
  provider.refresh();
  vscode.window.showInformationMessage('Sample library refreshed');
}
