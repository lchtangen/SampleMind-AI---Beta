'use client';

/**
 * COMMAND PALETTE COMPONENT
 * Global keyboard-accessible command center (Cmd+K / Ctrl+K)
 * Features: Fuzzy search, recent actions, keyboard navigation, action categories
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Command,
  Upload,
  Settings,
  FileMusic,
  Zap,
  Clock,
  FolderOpen,
  Download,
  Share2,
  Trash2,
  RotateCcw,
} from 'lucide-react';
import { commandPaletteBackdrop, commandPaletteContent } from '@/design-system/animations/presets';

export interface CommandAction {
  id: string;
  label: string;
  description?: string;
  category: 'action' | 'settings' | 'navigation' | 'recent';
  icon?: React.ReactNode;
  onSelect: () => void;
  shortcut?: string;
  keywords?: string[];
}

interface CommandPaletteProps {
  actions: CommandAction[];
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  placeholder?: string;
}

/**
 * Fuzzy search algorithm for command matching
 */
const fuzzyMatch = (query: string, text: string): boolean => {
  const lowerQuery = query.toLowerCase();
  const lowerText = text.toLowerCase();

  let queryIdx = 0;
  let textIdx = 0;

  while (queryIdx < lowerQuery.length && textIdx < lowerText.length) {
    if (lowerQuery[queryIdx] === lowerText[textIdx]) {
      queryIdx++;
    }
    textIdx++;
  }

  return queryIdx === lowerQuery.length;
};

/**
 * Calculate fuzzy match score (0-1)
 */
const fuzzyScore = (query: string, text: string): number => {
  if (!fuzzyMatch(query, text)) return 0;

  const lowerQuery = query.toLowerCase();
  const lowerText = text.toLowerCase();

  // Exact match
  if (lowerQuery === lowerText) return 1;

  // Starts with query
  if (lowerText.startsWith(lowerQuery)) return 0.9;

  // Word boundary match
  if (lowerText.includes(` ${lowerQuery}`)) return 0.8;

  // Contains query
  if (lowerText.includes(lowerQuery)) return 0.6;

  // Fuzzy match
  return 0.3;
};

/**
 * Default SampleMind AI commands
 */
const DEFAULT_COMMANDS: CommandAction[] = [
  {
    id: 'upload',
    label: 'Upload Audio',
    description: 'Upload new audio files for analysis',
    category: 'action',
    icon: <Upload className="w-4 h-4" />,
    onSelect: () => console.log('Upload'),
    shortcut: 'Ctrl+U',
    keywords: ['upload', 'add', 'file', 'audio'],
  },
  {
    id: 'analyze',
    label: 'Analyze Audio',
    description: 'Start analysis on selected files',
    category: 'action',
    icon: <Zap className="w-4 h-4" />,
    onSelect: () => console.log('Analyze'),
    shortcut: 'Ctrl+A',
    keywords: ['analyze', 'process', 'run'],
  },
  {
    id: 'library',
    label: 'Open Library',
    description: 'Browse your audio library',
    category: 'navigation',
    icon: <FolderOpen className="w-4 h-4" />,
    onSelect: () => console.log('Library'),
    shortcut: 'Ctrl+L',
    keywords: ['library', 'browse', 'samples'],
  },
  {
    id: 'settings',
    label: 'Settings',
    description: 'Open application settings',
    category: 'settings',
    icon: <Settings className="w-4 h-4" />,
    onSelect: () => console.log('Settings'),
    shortcut: 'Ctrl+,',
    keywords: ['settings', 'preferences', 'config'],
  },
  {
    id: 'export',
    label: 'Export Results',
    description: 'Export analysis results',
    category: 'action',
    icon: <Download className="w-4 h-4" />,
    onSelect: () => console.log('Export'),
    keywords: ['export', 'download', 'save'],
  },
  {
    id: 'share',
    label: 'Share Analysis',
    description: 'Share results with others',
    category: 'action',
    icon: <Share2 className="w-4 h-4" />,
    onSelect: () => console.log('Share'),
    keywords: ['share', 'send', 'export'],
  },
  {
    id: 'clear',
    label: 'Clear Cache',
    description: 'Clear application cache',
    category: 'settings',
    icon: <RotateCcw className="w-4 h-4" />,
    onSelect: () => console.log('Clear'),
    keywords: ['clear', 'cache', 'reset'],
  },
];

/**
 * Main Command Palette Component
 */
export const CommandPalette: React.FC<CommandPaletteProps> = ({
  actions = DEFAULT_COMMANDS,
  isOpen: initialIsOpen = false,
  onOpenChange,
  placeholder = 'Type a command...',
}) => {
  const [isOpen, setIsOpen] = useState(initialIsOpen);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentActions, setRecentActions] = useState<string[]>([]);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Handle Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        setQuery('');
      }

      // Handle Escape
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        setQuery('');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 0);
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Notify parent of open state change
  useEffect(() => {
    onOpenChange?.(isOpen);
  }, [isOpen, onOpenChange]);

  // Filter and sort actions based on query
  const filteredActions = useMemo(() => {
    let results = actions;

    if (query.trim()) {
      results = actions
        .map((action) => ({
          action,
          score: Math.max(
            fuzzyScore(query, action.label),
            fuzzyScore(query, action.description || ''),
            action.keywords
              ? Math.max(...action.keywords.map((k) => fuzzyScore(query, k)))
              : 0
          ),
        }))
        .filter((result) => result.score > 0)
        .sort((a, b) => b.score - a.score)
        .map((result) => result.action);
    } else {
      // No query: show recent actions first, then other categories
      const recentActionsData = actions.filter((a) => recentActions.includes(a.id));
      const otherActions = actions.filter((a) => !recentActions.includes(a.id));
      results = [...recentActionsData, ...otherActions];
    }

    return results;
  }, [query, actions, recentActions]);

  // Group actions by category
  const groupedActions = useMemo(() => {
    const groups: Record<string, CommandAction[]> = {
      recent: [],
      action: [],
      navigation: [],
      settings: [],
    };

    filteredActions.forEach((action) => {
      groups[action.category].push(action);
    });

    return query.trim() ? filteredActions : groups;
  }, [filteredActions, query]);

  // Handle action selection
  const handleSelect = useCallback(
    (actionId: string) => {
      const action = actions.find((a) => a.id === actionId);
      if (action) {
        action.onSelect();
        setRecentActions((prev) => {
          const updated = [actionId, ...prev.filter((a) => a !== actionId)];
          return updated.slice(0, 5); // Keep last 5
        });
      }
      setIsOpen(false);
      setQuery('');
    },
    [actions]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredActions.length - 1 ? prev + 1 : prev
        );
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredActions[selectedIndex]) {
          handleSelect(filteredActions[selectedIndex].id);
        }
      }
    },
    [filteredActions, selectedIndex, handleSelect]
  );

  return (
    <>
      {/* Keyboard shortcut hint (shown in footer or settings) */}
      <div className="hidden md:fixed md:bottom-4 md:right-4 md:block">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-xs text-slate-500">
          <Command className="w-3 h-3" />
          <span>K</span>
        </div>
      </div>

      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={commandPaletteBackdrop}
            initial="initial"
            animate="animate"
            exit="exit"
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 z-50"
          />
        )}
      </AnimatePresence>

      {/* Command Palette */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={commandPaletteContent}
            initial="initial"
            animate="animate"
            exit="exit"
            className="fixed top-[20vh] left-1/2 -translate-x-1/2 w-full max-w-xl z-50 mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="bg-slate-800/95 border border-slate-700 rounded-lg shadow-2xl overflow-hidden backdrop-blur-xl">
              {/* Search input */}
              <div className="px-4 py-3 border-b border-slate-700/50">
                <div className="flex items-center gap-3">
                  <Search className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setSelectedIndex(0);
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    className="flex-1 bg-transparent text-slate-200 placeholder-slate-500 outline-none text-sm"
                  />
                  {query && (
                    <button
                      onClick={() => {
                        setQuery('');
                        setSelectedIndex(0);
                      }}
                      className="text-slate-500 hover:text-slate-400 transition-colors"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              {/* Results */}
              <div className="max-h-[400px] overflow-y-auto">
                {filteredActions.length === 0 ? (
                  <div className="px-4 py-8 text-center text-slate-500">
                    <p>No commands found for "{query}"</p>
                  </div>
                ) : Array.isArray(groupedActions) ? (
                  // Flat list mode (when searching)
                  <div className="py-2">
                    {(groupedActions as CommandAction[]).map((action, index) => (
                      <motion.button
                        key={action.id}
                        onClick={() => handleSelect(action.id)}
                        onMouseEnter={() => setSelectedIndex(index)}
                        className={`w-full px-4 py-3 flex items-center gap-3 text-left transition-colors ${
                          selectedIndex === index
                            ? 'bg-blue-500/20 text-slate-200'
                            : 'text-slate-400 hover:text-slate-300'
                        }`}
                        whileHover={{ x: 4 }}
                      >
                        <div className="w-4 h-4 flex-shrink-0">
                          {action.icon || <FileMusic className="w-4 h-4" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium">{action.label}</div>
                          {action.description && (
                            <div className="text-xs text-slate-600">
                              {action.description}
                            </div>
                          )}
                        </div>
                        {action.shortcut && (
                          <div className="text-xs text-slate-600">
                            {action.shortcut}
                          </div>
                        )}
                      </motion.button>
                    ))}
                  </div>
                ) : (
                  // Grouped mode (when not searching)
                  <div className="py-2">
                    {Object.entries(groupedActions).map(([category, items]) => {
                      if (items.length === 0) return null;

                      const categoryLabels: Record<string, string> = {
                        recent: 'Recent',
                        action: 'Actions',
                        navigation: 'Navigation',
                        settings: 'Settings',
                      };

                      return (
                        <div key={category}>
                          <div className="px-4 py-2 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                            {categoryLabels[category]}
                          </div>
                          {items.map((action, idx) => {
                            const globalIndex = filteredActions.indexOf(action);
                            return (
                              <motion.button
                                key={action.id}
                                onClick={() => handleSelect(action.id)}
                                onMouseEnter={() => setSelectedIndex(globalIndex)}
                                className={`w-full px-4 py-3 flex items-center gap-3 text-left transition-colors ${
                                  selectedIndex === globalIndex
                                    ? 'bg-blue-500/20 text-slate-200'
                                    : 'text-slate-400 hover:text-slate-300'
                                }`}
                                whileHover={{ x: 4 }}
                              >
                                <div className="w-4 h-4 flex-shrink-0">
                                  {action.icon || <FileMusic className="w-4 h-4" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="text-sm font-medium">{action.label}</div>
                                  {action.description && (
                                    <div className="text-xs text-slate-600">
                                      {action.description}
                                    </div>
                                  )}
                                </div>
                                {action.shortcut && (
                                  <div className="text-xs text-slate-600">
                                    {action.shortcut}
                                  </div>
                                )}
                              </motion.button>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Footer hints */}
              <div className="px-4 py-2 border-t border-slate-700/50 bg-slate-900/50 text-xs text-slate-600 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span>↑↓ Navigate</span>
                  <span>↵ Select</span>
                  <span>Esc Dismiss</span>
                </div>
                <span>{filteredActions.length} results</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CommandPalette;
