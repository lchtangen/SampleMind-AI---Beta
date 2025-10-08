/**
 * Generate Music Command
 *
 * Generates AI music using Google Gemini Lyria
 */

import * as vscode from 'vscode';
import { SampleMindAPI } from '../utils/api';

export async function generateMusicCommand(api: SampleMindAPI): Promise<void> {
  // Get prompt from user
  const prompt = await vscode.window.showInputBox({
    prompt: 'Enter music generation prompt',
    placeHolder: 'e.g., "Upbeat electronic music for coding"',
    validateInput: (value) => {
      return value.trim().length === 0 ? 'Prompt cannot be empty' : null;
    },
  });

  if (!prompt) {
    return;
  }

  // Get styles and moods
  const styles = await api.getMusicStyles();
  const moods = await api.getMusicMoods();

  // Select style
  const styleItems = styles.map((s) => ({
    label: s.display_name,
    description: s.description,
    value: s.name,
  }));

  const selectedStyle = await vscode.window.showQuickPick(
    [{ label: 'Auto', description: 'Let AI choose', value: undefined }, ...styleItems],
    {
      placeHolder: 'Select music style',
    }
  );

  if (!selectedStyle) {
    return;
  }

  // Select mood
  const moodItems = moods.map((m) => ({
    label: m.display_name,
    description: m.description,
    value: m.name,
  }));

  const selectedMood = await vscode.window.showQuickPick(
    [{ label: 'Auto', description: 'Let AI choose', value: undefined }, ...moodItems],
    {
      placeHolder: 'Select music mood',
    }
  );

  if (!selectedMood) {
    return;
  }

  // Generate music
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Generating music...',
      cancellable: false,
    },
    async (progress) => {
      try {
        progress.report({ message: 'Sending request to AI...' });

        const result = await api.generateMusic({
          prompt,
          style: selectedStyle.value,
          mood: selectedMood.value,
          duration: 30,
        });

        if (result.success) {
          vscode.window.showInformationMessage(
            `✓ Music generated successfully! (${result.generation_time.toFixed(1)}s)`,
            'Open File'
          );
        } else {
          vscode.window.showErrorMessage('Music generation failed');
        }
      } catch (error: any) {
        vscode.window.showErrorMessage(
          `Generation failed: ${error.message || 'Unknown error'}`
        );
      }
    }
  );
}
