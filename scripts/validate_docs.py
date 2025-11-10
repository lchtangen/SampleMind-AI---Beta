#!/usr/bin/env python3
"""
SampleMind AI - Documentation Validation Script

Validates documentation structure, links, and content quality.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DocumentationValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_files': 0,
            'broken_links': 0,
            'missing_headers': 0,
            'duplicate_content': 0
        }
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the project"""
        md_files = []
        for pattern in ['*.md', '**/*.md']:
            md_files.extend(self.project_root.glob(pattern))
        return sorted(md_files)
    
    def extract_links(self, content: str) -> List[str]:
        """Extract markdown links from content"""
        # Match [text](link) format
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        return [match[1] for match in matches]
    
    def validate_internal_links(self, file_path: Path, content: str) -> List[str]:
        """Validate internal markdown links"""
        errors = []
        links = self.extract_links(content)
        
        for link in links:
            # Skip external links
            if link.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Skip anchors for now
            if link.startswith('#'):
                continue
            
            # Resolve relative path
            if link.startswith('/'):
                target_path = self.project_root / link.lstrip('/')
            else:
                target_path = file_path.parent / link
            
            # Check if target exists
            if not target_path.exists():
                errors.append(f"Broken link: {link} (from {file_path.relative_to(self.project_root)})")
                self.stats['broken_links'] += 1
        
        return errors
    
    def validate_structure(self, file_path: Path, content: str) -> List[str]:
        """Validate document structure"""
        errors = []
        
        # Check for main header
        if not content.strip().startswith('#'):
            errors.append(f"Missing main header: {file_path.relative_to(self.project_root)}")
            self.stats['missing_headers'] += 1
        
        # Check for empty files
        if len(content.strip()) < 50:
            errors.append(f"Very short content: {file_path.relative_to(self.project_root)}")
        
        return errors
    
    def check_duplicate_content(self, files_content: Dict[Path, str]) -> List[str]:
        """Check for duplicate content across files"""
        errors = []
        content_hashes = {}
        
        for file_path, content in files_content.items():
            # Simple content hash (first 200 chars)
            content_hash = content[:200].strip()
            if len(content_hash) > 50:  # Only check substantial content
                if content_hash in content_hashes:
                    errors.append(
                        f"Potential duplicate content: "
                        f"{file_path.relative_to(self.project_root)} and "
                        f"{content_hashes[content_hash].relative_to(self.project_root)}"
                    )
                    self.stats['duplicate_content'] += 1
                else:
                    content_hashes[content_hash] = file_path
        
        return errors
    
    def validate_required_files(self) -> List[str]:
        """Check for required documentation files"""
        required_files = [
            'README.md',
            'CONTRIBUTING.md',
            'LICENSE',
            'docs/README.md'
        ]
        
        errors = []
        for required_file in required_files:
            file_path = self.project_root / required_file
            if not file_path.exists():
                errors.append(f"Missing required file: {required_file}")
        
        return errors
    
    def check_documentation_coverage(self) -> List[str]:
        """Check if key areas have documentation"""
        warnings = []
        
        # Check for key documentation areas
        key_areas = {
            'installation': ['install', 'setup', 'getting-started'],
            'api': ['api', 'reference'],
            'development': ['develop', 'contrib'],
            'architecture': ['architect', 'design', 'structure']
        }
        
        md_files = self.find_markdown_files()
        file_names = [f.name.lower() for f in md_files]
        file_content = ' '.join(file_names)
        
        for area, keywords in key_areas.items():
            if not any(keyword in file_content for keyword in keywords):
                warnings.append(f"No documentation found for: {area}")
        
        return warnings
    
    def analyze_documentation_quality(self) -> Dict[str, int]:
        """Analyze overall documentation quality metrics"""
        md_files = self.find_markdown_files()
        
        metrics = {
            'total_files': len(md_files),
            'total_size': 0,
            'avg_file_size': 0,
            'files_with_toc': 0,
            'files_with_examples': 0
        }
        
        total_size = 0
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                size = len(content)
                total_size += size
                
                # Check for table of contents
                if 'table of contents' in content.lower() or '- [' in content:
                    metrics['files_with_toc'] += 1
                
                # Check for code examples
                if '```' in content or '    ' in content:
                    metrics['files_with_examples'] += 1
                    
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        metrics['total_size'] = total_size
        metrics['avg_file_size'] = total_size // len(md_files) if md_files else 0
        
        return metrics
    
    def validate_all(self) -> Dict[str, any]:
        """Run all validation checks"""
        logger.info("🔍 Starting documentation validation...")
        
        md_files = self.find_markdown_files()
        self.stats['total_files'] = len(md_files)
        
        files_content = {}
        
        # Read all files and validate individually
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                files_content[file_path] = content
                
                # Validate links
                link_errors = self.validate_internal_links(file_path, content)
                self.errors.extend(link_errors)
                
                # Validate structure
                structure_errors = self.validate_structure(file_path, content)
                self.errors.extend(structure_errors)
                
            except Exception as e:
                self.errors.append(f"Could not read {file_path}: {e}")
        
        # Cross-file validation
        duplicate_errors = self.check_duplicate_content(files_content)
        self.errors.extend(duplicate_errors)
        
        # Required files
        required_errors = self.validate_required_files()
        self.errors.extend(required_errors)
        
        # Coverage warnings
        coverage_warnings = self.check_documentation_coverage()
        self.warnings.extend(coverage_warnings)
        
        # Quality metrics
        quality_metrics = self.analyze_documentation_quality()
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': self.stats,
            'quality': quality_metrics
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate validation report"""
        report = f"""# Documentation Validation Report

## Summary
- Total files: {results['stats']['total_files']}
- Errors found: {len(results['errors'])}
- Warnings: {len(results['warnings'])}
- Broken links: {results['stats']['broken_links']}

## Quality Metrics
- Average file size: {results['quality']['avg_file_size']} characters
- Files with examples: {results['quality']['files_with_examples']}/{results['quality']['total_files']}
- Files with TOC: {results['quality']['files_with_toc']}/{results['quality']['total_files']}

## Errors
"""
        
        if results['errors']:
            for error in results['errors']:
                report += f"❌ {error}\n"
        else:
            report += "✅ No errors found!\n"
        
        report += "\n## Warnings\n"
        if results['warnings']:
            for warning in results['warnings']:
                report += f"⚠️  {warning}\n"
        else:
            report += "✅ No warnings!\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Validate SampleMind AI Documentation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--fail-on-errors", action="store_true", help="Exit with error code if validation fails")
    
    args = parser.parse_args()
    
    validator = DocumentationValidator(args.project_root)
    results = validator.validate_all()
    
    # Generate report
    report = validator.generate_report(results)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📊 Report saved to: {args.output}")
    else:
        print(report)
    
    # Summary
    error_count = len(results['errors'])
    warning_count = len(results['warnings'])
    
    if error_count == 0 and warning_count == 0:
        logger.info("✅ Documentation validation passed!")
        exit_code = 0
    elif error_count == 0:
        logger.info(f"⚠️  Documentation validation passed with {warning_count} warnings")
        exit_code = 0
    else:
        logger.error(f"❌ Documentation validation failed with {error_count} errors and {warning_count} warnings")
        exit_code = 1 if args.fail_on_errors else 0
    
    exit(exit_code)

if __name__ == "__main__":
    main()
