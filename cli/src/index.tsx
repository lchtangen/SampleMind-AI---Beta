import React from 'react';
import { render, Box, Text } from 'ink';
import chalk from 'chalk';

const App = () => (
  <Box borderStyle="round" borderColor="cyan" padding={2}>
    <Text>
      <Text color="magenta">{chalk.bold('SampleMind AI CLI')}</Text>
      {'\n'}
      <Text color="cyan">Welcome to the Cyberpunk future!</Text>
    </Text>
  </Box>
);

render(<App />);
