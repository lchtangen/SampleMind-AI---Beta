import React, { useEffect } from 'react';
import { Box, Text } from 'ink';

import { useCliStore } from '../../state/store.js';

const toneColor: Record<string, string> = {
  info: '#38bdf8',
  success: '#22c55e',
  warning: '#facc15',
  error: '#f87171'
};

export const NotificationCenter: React.FC = () => {
  const notifications = useCliStore((state) => state.notifications);
  const dismiss = useCliStore((state) => state.dismissNotification);

  useEffect(() => {
    if (notifications.length === 0) return;
    const timers = notifications.map((note) =>
      setTimeout(() => dismiss(note.id), 4500)
    );

    return () => {
      for (const timer of timers) clearTimeout(timer);
    };
  }, [notifications, dismiss]);

  if (notifications.length === 0) return null;

  return (
    <Box flexDirection="column" marginTop={1}>
      {notifications.map((note) => (
        <Box key={note.id} borderStyle="round" borderColor={toneColor[note.tone]} paddingX={1} paddingY={0} marginBottom={1}>
          <Text color={toneColor[note.tone]}>
            ▸ {note.message}
          </Text>
        </Box>
      ))}
    </Box>
  );
};
