import { mkdir, writeFile } from 'fs/promises';
import path from 'path';

import type { CliSettings } from '../state/store.js';

const ANALYTICS_DIR = path.join(process.env.HOME ?? process.cwd(), '.config', 'samplemind');
const ANALYTICS_PATH = path.join(ANALYTICS_DIR, 'analytics.log');

export async function recordEvent(event: string, settings: CliSettings) {
  if (!settings.telemetry) return;

  const payload = {
    event,
    timestamp: new Date().toISOString()
  };

  try {
    await mkdir(ANALYTICS_DIR, { recursive: true });
    await writeFile(ANALYTICS_PATH, JSON.stringify(payload) + '\n', { flag: 'a' });
  } catch (error) {
    // Safe to ignore telemetry write failures
  }
}
