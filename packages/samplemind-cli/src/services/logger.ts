import chalk from 'chalk';

interface Logger {
  info: (message: string, meta?: unknown) => void;
  warn: (message: string, meta?: unknown) => void;
  error: (message: string, meta?: unknown) => void;
}

export function createLogger(): Logger {
  const prefix = chalk.hex('#00f0ff')('[SampleMind CLI]');

  return {
    info(message, meta) {
      console.log(prefix, chalk.hex('#7c3aed')(message));
      if (meta) console.log(chalk.gray(JSON.stringify(meta, null, 2)));
    },
    warn(message, meta) {
      console.warn(prefix, chalk.hex('#fbbf24')(message));
      if (meta) console.warn(chalk.gray(JSON.stringify(meta, null, 2)));
    },
    error(message, meta) {
      console.error(prefix, chalk.hex('#fb7185')(message));
      if (meta) console.error(chalk.gray(JSON.stringify(meta, null, 2)));
    }
  };
}
