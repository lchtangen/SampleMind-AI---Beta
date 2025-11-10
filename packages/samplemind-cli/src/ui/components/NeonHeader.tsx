import React from 'react';
import Gradient from 'ink-gradient';
import { Box, Text } from 'ink';

import { theme } from '../../utils/theme.js';

export const NeonHeader: React.FC = () => (
  <Box flexDirection="column" marginBottom={1}>
    <Gradient name="morning">
      <Text>{theme.ascii.logo}</Text>
    </Gradient>
    <Text color="gray">Welcome to the SampleMind AI interactive terminal</Text>
  </Box>
);
