#!/usr/bin/env python3
"""Quick validation of project documentation"""

import os
from pathlib import Path

def validate_project_docs():
    """Validate main project documentation"""
    project_root = Path('.')
    errors = []
    
    # Find markdown files excluding problematic directories
    exclude_dirs = {'node_modules', '.venv', 'packages', 'samplemind-core', 'samplemind-web', '.git'}
    
    md_files = []
    for md_file in project_root.rglob('*.md'):
        if not any(part in exclude_dirs for part in md_file.parts):
            md_files.append(md_file)
    
    print(f"Found {len(md_files)} markdown files to validate")
    
    # Check for broken internal links
    broken_links = 0
    missing_headers = 0
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Check for main header
            if not content.strip().startswith('#'):
                print(f"❌ Missing main header: {md_file}")
                missing_headers += 1
            
            # Simple link validation
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for text, link in links:
                if not link.startswith(('http', 'mailto:', '#')):
                    # Check if internal link exists
                    if link.startswith('/'):
                        target = project_root / link.lstrip('/')
                    else:
                        target = md_file.parent / link
                    
                    if not target.exists():
                        print(f"❌ Broken link: {link} (from {md_file})")
                        broken_links += 1
                        
        except Exception as e:
            print(f"❌ Error reading {md_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"- Total files: {len(md_files)}")
    print(f"- Broken links: {broken_links}")
    print(f"- Missing headers: {missing_headers}")
    
    return broken_links + missing_headers == 0

if __name__ == '__main__':
    success = validate_project_docs()
    exit(0 if success else 1)
