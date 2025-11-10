import { promises as fs } from 'fs';
import path from 'path';

import MiniSearch from 'minisearch';
import stripAnsi from 'strip-ansi';

import type { IndexedFile } from './indexer.js';

const SUPPORTED_EXTENSIONS = new Set([
  '.ts',
  '.tsx',
  '.js',
  '.jsx',
  '.json',
  '.md',
  '.mdx',
  '.yml',
  '.yaml'
]);

const MAX_FILE_SIZE = 256 * 1024; // 256 KB
const SNIPPET_LENGTH = 160;

interface SearchDocument {
  id: string;
  path: string;
  content: string;
}

export interface SearchResult {
  path: string;
  score: number;
  snippet: string;
}

export interface SearchEngine {
  query: (term: string) => Promise<SearchResult[]>;
}

function createSnippet(content: string, term: string): string {
  const cleanContent = stripAnsi(content);
  const lower = cleanContent.toLowerCase();
  const index = lower.indexOf(term.toLowerCase());

  if (index === -1) {
    return cleanContent.slice(0, SNIPPET_LENGTH).trim();
  }

  const start = Math.max(0, index - SNIPPET_LENGTH / 2);
  const end = Math.min(cleanContent.length, index + SNIPPET_LENGTH / 2);
  return cleanContent.slice(start, end).trim();
}

async function loadDocuments(root: string, files: IndexedFile[]): Promise<SearchDocument[]> {
  const docs: SearchDocument[] = [];

  for (const file of files) {
    if (!SUPPORTED_EXTENSIONS.has(file.extension)) continue;
    if (file.size > MAX_FILE_SIZE) continue;

    const absolute = path.join(root, file.path);
    try {
      const content = await fs.readFile(absolute, 'utf8');
      docs.push({ id: file.path, path: file.path, content });
    } catch (error) {
      // Skip unreadable files silently
      continue;
    }
  }

  return docs;
}

export async function createSearchEngine(root: string, files: IndexedFile[]): Promise<SearchEngine | null> {
  try {
    const documents = await loadDocuments(root, files);
    if (documents.length === 0) {
      return null;
    }

    const miniSearch = new MiniSearch<SearchDocument>({
      fields: ['content', 'path'],
      storeFields: ['path', 'content'],
      searchOptions: {
        boost: { content: 2, path: 1 },
        prefix: true,
        fuzzy: 0.2
      }
    });

    miniSearch.addAll(documents);

    return {
      async query(term: string) {
        const trimmed = term.trim();
        if (!trimmed) return [];

        const hits = miniSearch.search(trimmed);
        return hits.slice(0, 5).map((hit) => ({
          path: hit.path,
          score: hit.score,
          snippet: createSnippet(hit.content, trimmed)
        }));
      }
    };
  } catch (error) {
    console.warn('[SampleMind CLI] Failed to initialize search engine:', error);
    return null;
  }
}
