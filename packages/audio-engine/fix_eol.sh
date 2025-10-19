#!/bin/bash
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.json" -o -name "*.md" -o -name "*.css" -o -name "*.jsx" \) -not -path "*/node_modules/*" -not -path "*/.next/*" | while read -r file; do
    if [ -s "$file" ] && [ "$(tail -c1 "$file" | wc -l)" -eq 0 ]; then
        echo >> "$file"
        echo "Fixed: $file"
    fi
done
