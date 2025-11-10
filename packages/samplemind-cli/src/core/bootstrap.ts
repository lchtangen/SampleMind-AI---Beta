import ora from 'ora';

import { buildIndex } from './indexer.js';
import { createSearchEngine } from './search.js';
import { loadConfiguration, loadSettings, type CliConfig } from '../services/configManager.js';
import { createLogger } from '../services/logger.js';
import type { CliSettings } from '../state/store.js';
import type { SearchEngine } from './search.js';

export interface BootstrapResult {
  config: CliConfig;
  settings: CliSettings;
  index: Awaited<ReturnType<typeof buildIndex>>;
  searchEngine: SearchEngine | null;
  timestamp: number;
}

export async function bootstrap(): Promise<BootstrapResult> {
  const logger = createLogger();
  const spinner = ora({ text: 'Initializing SampleMind CLI…', spinner: 'dots' }).start();

  try {
    const [config, settings] = await Promise.all([loadConfiguration(), loadSettings()]);
    const projectRoot = typeof config.projectRoot === 'string' ? config.projectRoot : process.cwd();
    spinner.text = 'Indexing project files…';
    const index = await buildIndex(projectRoot);

    spinner.text = 'Training search engine…';
    const searchEngine = await createSearchEngine(projectRoot, index.files);

    spinner.succeed('Environment ready');
    logger.info('CLI bootstrap completed.');

    return {
      config,
      settings,
      index,
      searchEngine,
      timestamp: Date.now()
    };
  } catch (error) {
    spinner.fail('Failed to initialize CLI');
    logger.error('Bootstrap failed', error);
    throw error;
  }
}
