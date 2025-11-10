import React from 'react';
import { Box, Text } from 'ink';
import SelectInput from 'ink-select-input';

import { useCliStore, type ThemeVariant } from '../../state/store.js';
import { saveSettings } from '../../services/configManager.js';

const themeOptions: Array<{ label: string; value: ThemeVariant }> = [
  { label: 'Neon Glass (default)', value: 'neon-glass' },
  { label: 'Dark Neon', value: 'dark-neon' },
  { label: 'Minimal', value: 'minimal' }
];

export const SettingsPanel: React.FC = () => {
  const settings = useCliStore((state) => state.settings);
  const setSettings = useCliStore((state) => state.setSettings);
  const pushNotification = useCliStore((state) => state.pushNotification);

  const handleThemeChange = async (theme: ThemeVariant) => {
    const next = { ...settings, theme };
    setSettings({ theme });
    await saveSettings(next);
    pushNotification({ message: `Theme updated to ${theme}`, tone: 'success' });
  };

  const handleTelemetryToggle = async () => {
    const next = { ...settings, telemetry: !settings.telemetry };
    setSettings({ telemetry: next.telemetry });
    await saveSettings(next);
    pushNotification({ message: `Telemetry ${next.telemetry ? 'enabled' : 'disabled'}`, tone: 'info' });
  };

  const handleHintsToggle = async () => {
    const next = { ...settings, showHints: !settings.showHints };
    setSettings({ showHints: next.showHints });
    await saveSettings(next);
    pushNotification({ message: `Hints ${next.showHints ? 'enabled' : 'hidden'}`, tone: 'info' });
  };

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="#7c3aed" padding={1} width={50}>
      <Text color="#c4b5fd" bold>
        Settings
      </Text>
      <Box flexDirection="column" marginTop={1}>
        <Text color="#94a3b8">Theme</Text>
        <SelectInput
          items={themeOptions.map((theme) => ({ key: theme.value, label: theme.label, value: theme.value }))}
          initialIndex={themeOptions.findIndex((option) => option.value === settings.theme)}
          onSelect={(item) => handleThemeChange(item.value as ThemeVariant)}
        />
      </Box>
      <Box flexDirection="column" marginTop={1}>
        <Text color="#94a3b8">Telemetry</Text>
        <Text color="#cbd5f5">Currently {settings.telemetry ? 'enabled' : 'disabled'} (press Enter to toggle)</Text>
        <SelectInput
          items={[{ key: 'toggle-telemetry', label: 'Toggle telemetry', value: 'toggle-telemetry' }]}
          onSelect={handleTelemetryToggle}
        />
      </Box>
      <Box flexDirection="column" marginTop={1}>
        <Text color="#94a3b8">Hints</Text>
        <Text color="#cbd5f5">Currently {settings.showHints ? 'visible' : 'hidden'} (press Enter to toggle)</Text>
        <SelectInput
          items={[{ key: 'toggle-hints', label: 'Toggle hints', value: 'toggle-hints' }]}
          onSelect={handleHintsToggle}
        />
      </Box>
    </Box>
  );
};
