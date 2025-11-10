import { render } from 'ink';

import { bootstrap } from './core/bootstrap.js';
import { App } from './ui/app.js';

(async () => {
  const bootstrapResult = await bootstrap();
  render(<App bootstrap={bootstrapResult} />);
})();
