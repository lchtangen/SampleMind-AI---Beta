import React, { useEffect, useMemo } from 'react';
import { Box, Text, useInput } from 'ink';

import type { BootstrapResult } from '../core/bootstrap.js';
import { useCliStore, type MenuRoute, type ThemeVariant } from '../state/store.js';
import { NeonHeader } from './components/NeonHeader.js';
import { Menu } from './components/Menu.js';
import { AnimatedBackground } from './components/AnimatedBackground.js';
import { NotificationCenter } from './components/NotificationCenter.js';
import { TaskPanel } from './components/TaskPanel.js';
import { HelpOverlay } from './components/HelpOverlay.js';
import { ShortcutOverlay } from './components/ShortcutOverlay.js';
import { SettingsPanel } from './components/SettingsPanel.js';
import { Wizard } from './components/Wizard.js';
import { SearchOverlay } from './components/SearchOverlay.js';
import { recordEvent } from '../services/analytics.js';

interface AppProps {
  bootstrap: BootstrapResult;
}

export const App: React.FC<AppProps> = ({ bootstrap }) => {
  const setConfig = useCliStore((state) => state.setConfig);
  const setSettings = useCliStore((state) => state.setSettings);
  const setIndex = useCliStore((state) => state.setIndex);
  const setSearchEngine = useCliStore((state) => state.setSearchEngine);
  const setSearchQuery = useCliStore((state) => state.setSearchQuery);
  const setSearchResults = useCliStore((state) => state.setSearchResults);
  const pushNotification = useCliStore((state) => state.pushNotification);
  const route = useCliStore((state) => state.menuRoute);
  const notifications = useCliStore((state) => state.notifications);
  const index = useCliStore((state) => state.index);
  const settings = useCliStore((state) => state.settings);
  const showHelpOverlay = useCliStore((state) => state.showHelpOverlay);
  const showShortcutOverlay = useCliStore((state) => state.showShortcutOverlay);
  const showSearchOverlay = useCliStore((state) => state.showSearchOverlay);
  const toggleHelpOverlay = useCliStore((state) => state.toggleHelpOverlay);
  const toggleShortcutOverlay = useCliStore((state) => state.toggleShortcutOverlay);
  const toggleSearchOverlay = useCliStore((state) => state.toggleSearchOverlay);
  const clearNotifications = useCliStore((state) => state.clearNotifications);
  const activeTasks = useCliStore((state) => state.activeTasks);
  const searchQuery = useCliStore((state) => state.searchQuery);
  const searchResults = useCliStore((state) => state.searchResults);

  useEffect(() => {
    setConfig(bootstrap.config);
    setSettings(bootstrap.settings);
    setIndex(bootstrap.index);
    setSearchEngine(bootstrap.searchEngine);
    pushNotification({ message: `Indexed ${bootstrap.index.totalFiles} files`, tone: 'success' });
    recordEvent('cli_bootstrap_complete', bootstrap.settings);
  }, [bootstrap, pushNotification, setConfig, setSettings, setIndex, setSearchEngine]);

  useEffect(() => {
    recordEvent(`navigate_${route}`, settings);
  }, [route, settings]);

  useInput((input, key) => {
    if (showSearchOverlay) {
      if (key.escape) {
        toggleSearchOverlay(false);
        setSearchQuery('');
        setSearchResults([]);
        return;
      }

      if (key.return && searchResults.length > 0) {
        const topHit = searchResults[0];
        pushNotification({ message: `Top match: ${topHit.path}`, tone: 'info' });
        return;
      }

      if (key.backspace || key.delete) {
        if (searchQuery.length > 0) {
          setSearchQuery(searchQuery.slice(0, -1));
        }
        return;
      }

      if (!key.ctrl && !key.meta && input) {
        setSearchQuery(searchQuery + input);
      }
      return;
    }

    if (input === '?' && !key.shift && !key.ctrl && !key.meta) {
      toggleHelpOverlay();
    } else if (input === '?' && key.shift) {
      toggleShortcutOverlay();
    } else if (key.ctrl && input?.toLowerCase() === 'f') {
      toggleSearchOverlay(true);
      setSearchQuery('');
      setSearchResults([]);
    } else if (key.escape) {
      toggleHelpOverlay(false);
      toggleShortcutOverlay(false);
      toggleSearchOverlay(false);
      setSearchQuery('');
      setSearchResults([]);
    } else if (key.ctrl && input?.toLowerCase() === 'l') {
      clearNotifications();
      pushNotification({ message: 'Notifications cleared', tone: 'info' });
    } else if (key.ctrl && input?.toLowerCase() === 'k') {
      pushNotification({ message: 'Command palette coming soon', tone: 'warning' });
    }
  });

  return (
    <Box flexDirection="column" padding={1}>
      <AnimatedBackground width={80} />
      <NeonHeader />
      <Box>
        <Menu />
        <Box flexDirection="column" marginLeft={2} flexGrow={1}>
          <ContentView route={route} indexSummary={index ? index.totalFiles : 0} settings={settings} />
          <NotificationCenter />
        </Box>
        <Box marginLeft={2}>
          <TaskPanel />
        </Box>
      </Box>

      {showSearchOverlay && (
        <Box marginTop={1}>
          <SearchOverlay />
        </Box>
      )}

      {showHelpOverlay && (
        <Box marginTop={1}>
          <HelpOverlay />
        </Box>
      )}

      {showShortcutOverlay && (
        <Box marginTop={1}>
          <ShortcutOverlay />
        </Box>
      )}

      {settings.showHints && notifications.length === 0 && activeTasks.length === 0 && (
        <Box marginTop={1}>
          <Text color="#475569">
            Tip: Ctrl+F to search, ? for help, Shift+? for shortcuts, Ctrl+L to clear notifications.
          </Text>
        </Box>
      )}
    </Box>
  );
};

interface ContentProps {
  route: MenuRoute;
  indexSummary: number;
  settings: { theme: ThemeVariant; showHints: boolean; telemetry: boolean };
}

const ContentView: React.FC<ContentProps> = ({ route, indexSummary, settings }) => {
  const wizardSteps = useMemo(
    () => [
      { title: 'Select audio source', description: 'Choose a file or directory to analyze.' },
      { title: 'Configure AI providers', description: 'Pick between OpenAI, Google, or local engines.' },
      { title: 'Review & launch', description: 'Confirm settings and start the pipeline.' }
    ],
    []
  );

  switch (route) {
    case 'dashboard':
      return (
        <Box flexDirection="column">
          <Text color="#f8fafc" bold>
            Dashboard
          </Text>
          <Text color="#94a3b8">Project files indexed: {indexSummary}</Text>
          <Text color="#94a3b8">Active theme: {settings.theme}</Text>
          <Text color="#94a3b8">Telemetry: {settings.telemetry ? 'enabled' : 'disabled'}</Text>
        </Box>
      );
    case 'analysis':
      return (
        <Wizard title="Quick Analysis" steps={wizardSteps} activeStep={0} footer="Use Enter to advance. 📡" />
      );
    case 'batch':
      return (
        <Wizard title="Batch Processing" steps={wizardSteps} activeStep={1} footer="Batch templates launching soon." />
      );
    case 'settings':
      return <SettingsPanel />;
    case 'exit':
      return (
        <Box flexDirection="column">
          <Text bold color="#f8fafc">
            Exit CLI
          </Text>
          <Text color="#94a3b8">Press Ctrl+C to exit or pick another route.</Text>
        </Box>
      );
    default:
      return null;
  }
};
