import React from 'react';
import { Box, Text } from 'ink';

const shortcutGroups = [
  {
    title: 'Navigation',
    shortcuts: [
      { keys: '↑/↓', action: 'Move selection' },
      { keys: 'Enter', action: 'Select option' },
      { keys: 'Esc', action: 'Close overlay/modals' }
    ]
  },
  {
    title: 'Productivity',
    shortcuts: [
      { keys: 'Ctrl+L', action: 'Clear notifications' },
      { keys: 'Ctrl+K', action: 'Open command palette (coming soon)' }
    ]
  }
];

export const ShortcutOverlay: React.FC = () => (
  <Box flexDirection="column" borderStyle="double" borderColor="#22d3ee" padding={1} width={60}>
    <Text color="#22d3ee" bold>
      Keyboard Shortcuts
    </Text>
    {shortcutGroups.map((group) => (
      <Box key={group.title} flexDirection="column" marginTop={1}>
        <Text color="#38bdf8">{group.title}</Text>
        {group.shortcuts.map((shortcut) => (
          <Box key={shortcut.keys} justifyContent="space-between">
            <Text color="#c4b5fd">{shortcut.keys}</Text>
            <Text color="#94a3b8">{shortcut.action}</Text>
          </Box>
        ))}
      </Box>
    ))}
  </Box>
);
