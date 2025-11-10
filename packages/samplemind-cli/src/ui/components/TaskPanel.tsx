import React from 'react';
import { Box, Text } from 'ink';

import { useCliStore } from '../../state/store.js';

const statusColor: Record<string, string> = {
  pending: '#94a3b8',
  running: '#38bdf8',
  success: '#22c55e',
  error: '#f87171'
};

export const TaskPanel: React.FC = () => {
  const tasks = useCliStore((state) => state.activeTasks);

  if (tasks.length === 0) {
    return (
      <Box flexDirection="column" borderStyle="round" borderColor="#1f2937" padding={1} width={50}>
        <Text color="#475569">No active tasks</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="#38bdf8" padding={1} width={50}>
      <Text color="#38bdf8" bold>
        Task Runner
      </Text>
      {tasks.map((task) => (
        <Box key={task.id} flexDirection="column" marginTop={1}>
          <Text>
            <Text color={statusColor[task.status]}>●</Text> {task.label}
          </Text>
          {typeof task.progress === 'number' && (
            <Text color="#94a3b8">Progress: {Math.round(task.progress * 100)}%</Text>
          )}
          {task.logs.slice(-3).map((log, idx) => (
            <Text key={idx} color="#64748b">  ↳ {log}</Text>
          ))}
        </Box>
      ))}
    </Box>
  );
};
