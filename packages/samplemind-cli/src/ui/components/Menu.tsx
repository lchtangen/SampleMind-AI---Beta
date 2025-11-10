import React, { useMemo } from 'react';
import { Box, Text } from 'ink';
import SelectInput from 'ink-select-input';

import { useCliStore, type MenuRoute } from '../../state/store.js';

interface MenuItem {
  label: string;
  value: MenuRoute;
  hint?: string;
}

const menuItems: MenuItem[] = [
  { label: 'Dashboard', value: 'dashboard', hint: 'Overview & project stats' },
  { label: 'Quick Analysis', value: 'analysis', hint: 'Run single-file analysis' },
  { label: 'Batch Processing', value: 'batch', hint: 'Folder workflows' },
  { label: 'Settings', value: 'settings', hint: 'Personalize experience' },
  { label: 'Exit', value: 'exit', hint: 'Quit the CLI' }
];

export const Menu: React.FC = () => {
  const setMenuRoute = useCliStore((state) => state.setMenuRoute);
  const route = useCliStore((state) => state.menuRoute);

  const items = useMemo<Array<{ key: string; label: string; value: MenuRoute }>>(
    () =>
      menuItems.map((item) => ({
        key: item.value,
        label: `${item.label}${item.hint ? ` — ${item.hint}` : ''}`,
        value: item.value
      })),
    []
  );

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="#7c3aed" paddingX={1} paddingY={1} width={40}>
      <Text color="#00f0ff" bold>
        Navigate
      </Text>
      <SelectInput
        items={items}
        initialIndex={Math.max(items.findIndex((item) => item.value === route), 0)}
        onSelect={(item) => setMenuRoute(item.value as MenuRoute)}
      />
    </Box>
  );
};
