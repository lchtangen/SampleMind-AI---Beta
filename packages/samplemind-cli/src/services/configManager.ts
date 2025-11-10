import { promises as fs } from 'fs';
import path from 'path';

import type { CliSettings, ThemeVariant } from '../state/store.js';

export interface CliConfig {
  projectRoot: string;
  theme: ThemeVariant;
  telemetry: boolean;
  [key: string]: unknown;
}

const CONFIG_DIR = path.join(process.env.HOME ?? process.cwd(), '.config', 'samplemind');
const SETTINGS_PATH = path.join(CONFIG_DIR, 'settings.json');

const DEFAULT_CONFIG_LOCATIONS = [
  process.env.SAMPLEMIND_CLI_CONFIG,
  path.join(process.cwd(), '.samplemindrc.json'),
  path.join(CONFIG_DIR, 'config.json')
].filter(Boolean) as string[];

const DEFAULT_CONFIG: CliConfig = {
  projectRoot: process.cwd(),
  theme: 'neon-glass',
  telemetry: false
};

const DEFAULT_SETTINGS: CliSettings = {
  theme: 'neon-glass',
  telemetry: false,
  showHints: true
};

async function ensureConfigDir() {
  await fs.mkdir(CONFIG_DIR, { recursive: true });
}

export async function loadConfiguration(): Promise<CliConfig> {
  for (const location of DEFAULT_CONFIG_LOCATIONS) {
    try {
      const raw = await fs.readFile(location, 'utf8');
      const parsed = JSON.parse(raw) as Record<string, unknown>;
      return {
        ...DEFAULT_CONFIG,
        ...parsed,
        projectRoot: typeof parsed.projectRoot === 'string' ? parsed.projectRoot : DEFAULT_CONFIG.projectRoot,
        theme: (parsed.theme as ThemeVariant) ?? DEFAULT_CONFIG.theme,
        telemetry: typeof parsed.telemetry === 'boolean' ? parsed.telemetry : DEFAULT_CONFIG.telemetry
      };
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        console.warn(`[SampleMind CLI] Failed to parse config at ${location}:`, error);
      }
    }
  }

  return { ...DEFAULT_CONFIG };
}

export async function loadSettings(): Promise<CliSettings> {
  try {
    const raw = await fs.readFile(SETTINGS_PATH, 'utf8');
    const parsed = JSON.parse(raw) as Partial<CliSettings>;
    return {
      ...DEFAULT_SETTINGS,
      ...parsed,
      theme: parsed?.theme ?? DEFAULT_SETTINGS.theme,
      telemetry: typeof parsed?.telemetry === 'boolean' ? parsed.telemetry : DEFAULT_SETTINGS.telemetry,
      showHints: typeof parsed?.showHints === 'boolean' ? parsed.showHints : DEFAULT_SETTINGS.showHints
    };
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
      console.warn('[SampleMind CLI] Failed to load settings:', error);
    }
    return DEFAULT_SETTINGS;
  }
}

export async function saveSettings(settings: CliSettings): Promise<void> {
  await ensureConfigDir();
  await fs.writeFile(SETTINGS_PATH, JSON.stringify(settings, null, 2), 'utf8');
}
