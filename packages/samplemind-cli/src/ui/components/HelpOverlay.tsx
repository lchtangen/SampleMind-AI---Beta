import React from 'react';
import { Box, Text } from 'ink';

const tips = [
  { shortcut: 'Enter', description: 'Activate highlighted menu item' },
  { shortcut: 'Tab', description: 'Switch between panels' },
  { shortcut: '?', description: 'Toggle contextual help overlay' },
  { shortcut: 'Shift+?', description: 'Show keyboard shortcuts summary' },
  { shortcut: 'Ctrl+C', description: 'Exit the CLI gracefully' }
];

export const HelpOverlay: React.FC = () => (
  <Box flexDirection="column" borderStyle="round" borderColor="#7c3aed" padding={1} width={60}>
    <Text color="#c4b5fd" bold>
      Contextual Help
    </Text>
    {tips.map((tip) => (
      <Box key={tip.shortcut} justifyContent="space-between">
        <Text color="#22d3ee">{tip.shortcut}</Text>
        <Text color="#cbd5f5">{tip.description}</Text>
      </Box>
    ))}
    <Box marginTop={1}>
      <Text color="#475569">Tips update dynamically as we add more workflows.</Text>
    </Box>
  </Box>
);
