import fg from 'fast-glob';
import { promises as fs } from 'fs';
import path from 'path';

export interface IndexedFile {
  path: string;
  size: number;
  modified: number;
  extension: string;
}

export interface FileIndex {
  files: IndexedFile[];
  totalFiles: number;
  totalSize: number;
}

export async function buildIndex(root: string): Promise<FileIndex> {
  const entries = await fg(['**/*'], {
    cwd: root,
    dot: false,
    ignore: ['**/node_modules/**', '**/.git/**', '**/dist/**', '**/.next/**']
  });

  const files: IndexedFile[] = [];
  let totalSize = 0;

  for (const relative of entries) {
    const absolute = path.join(root, relative);
    try {
      const stats = await fs.stat(absolute);
      if (!stats.isFile()) continue;

      const fileRecord: IndexedFile = {
        path: relative,
        size: stats.size,
        modified: stats.mtimeMs,
        extension: path.extname(relative)
      };

      files.push(fileRecord);
      totalSize += stats.size;
    } catch (error) {
      // Non-critical: skip files we cannot read
      continue;
    }
  }

  return {
    files,
    totalFiles: files.length,
    totalSize
  };
}
