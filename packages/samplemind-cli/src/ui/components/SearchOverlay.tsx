import React, { useEffect } from 'react';
import { Box, Text } from 'ink';

import { useCliStore } from '../../state/store.js';

export const SearchOverlay: React.FC = () => {
  const query = useCliStore((state) => state.searchQuery);
  const results = useCliStore((state) => state.searchResults);
  const searchEngine = useCliStore((state) => state.searchEngine);
  const setResults = useCliStore((state) => state.setSearchResults);

  useEffect(() => {
    if (!searchEngine) {
      setResults([]);
      return;
    }

    let cancelled = false;
    const timer = setTimeout(async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }

      const hits = await searchEngine.query(query);
      if (!cancelled) {
        setResults(hits);
      }
    }, 160);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query, searchEngine, setResults]);

  const hasResults = results.length > 0;

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="#22d3ee" padding={1} width={70}>
      <Text color="#22d3ee" bold>
        Global Search (Ctrl+F)
      </Text>
      <Text color="#94a3b8">Query: {query.length > 0 ? query : 'Type to search…'}</Text>
      <Text color="#475569">Press Esc to close, Enter to announce top hit.</Text>

      <Box flexDirection="column" marginTop={1}>
        {hasResults ? (
          results.map((result) => (
            <Box key={result.path} flexDirection="column" marginBottom={1}>
              <Text color="#38bdf8">{result.path}</Text>
              <Text color="#94a3b8">{result.snippet}</Text>
            </Box>
          ))
        ) : (
          <Text color="#64748b">
            {query.trim().length === 0 ? 'Start typing to search across the repository.' : 'No matches yet.'}
          </Text>
        )}
      </Box>
    </Box>
  );
};
