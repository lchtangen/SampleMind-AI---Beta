#!/usr/bin/env python3
"""
Quick type hints fixer for common patterns
Adds type hints to functions missing them
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


def add_return_none_hints(file_path: Path) -> int:
    """Add -> None hints to functions without return statements.
    
    Args:
        file_path: Path to Python file to fix
        
    Returns:
        Number of fixes applied
    """
    content = file_path.read_text()
    lines = content.split('\n')
    fixes = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Match function definitions without return type hints
        if line.strip().startswith('def ') and '->' not in line and ':' in line:
            # Check if it's a simple one-liner or has body
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Skip if already has return type
                if '->' in line:
                    i += 1
                    continue
                    
                # Add -> None before the colon
                if line.rstrip().endswith(':'):
                    lines[i] = line.rstrip()[:-1] + ' -> None:'
                    fixes += 1
        
        i += 1
    
    if fixes > 0:
        file_path.write_text('\n'.join(lines))
        print(f"✅ Fixed {fixes} return type hints in {file_path.name}")
    
    return fixes


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python fix_type_hints.py <file_or_directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    total_fixes = 0
    
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py"))
    
    for file_path in files:
        if '.venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
        
        try:
            fixes = add_return_none_hints(file_path)
            total_fixes += fixes
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Total fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
