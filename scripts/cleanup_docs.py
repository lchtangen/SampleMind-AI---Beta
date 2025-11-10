#!/usr/bin/env python3
"""
SampleMind AI - Documentation Cleanup Automation Script

This script automates the documentation cleanup and reorganization process
according to the DOCUMENTATION_CLEANUP_PLAN.md.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DocumentationCleaner:
    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.moved_files = []
        self.deleted_files = []
        
    def create_backup(self):
        """Create git backup branch before cleanup"""
        if not self.dry_run:
            os.system("git checkout -b docs-cleanup-backup")
            os.system("git add . && git commit -m 'Backup before documentation cleanup'")
            logger.info("✅ Created backup branch: docs-cleanup-backup")
        else:
            logger.info("🔍 DRY RUN: Would create backup branch")
    
    def create_new_structure(self):
        """Create new documentation directory structure"""
        new_dirs = [
            "docs/getting-started",
            "docs/guides/platform-guides", 
            "docs/architecture",
            "docs/development",
            "docs/reference",
            "docs/archive/status-reports",
            "docs/archive/old-guides",
            "docs/archive/test-reports"
        ]
        
        for dir_path in new_dirs:
            full_path = self.project_root / dir_path
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {dir_path}")
            else:
                logger.info(f"🔍 DRY RUN: Would create directory: {dir_path}")
    
    def move_to_archive(self):
        """Move obsolete files to archive"""
        archive_moves = {
            # Status and completion reports
            "docs/archive/status-reports/": [
                "PHASE_*_COMPLETE.md",
                "SESSION_COMPLETE*.md", 
                "PROGRESS_*.md",
                "BETA_RELEASE*.md",
                "FINAL_*.md",
                "*_COMPLETE.md"
            ],
            # Test reports
            "docs/archive/test-reports/": [
                "TEST_RESULTS*.md",
                "MANUAL_TESTING_GUIDE.md",
                "FULL_STACK_TEST*.md"
            ],
            # Old guides
            "docs/archive/old-guides/": [
                "QUICKSTART_BETA.md",
                "FRONTEND_*.md", 
                "BACKEND_READY.md",
                "ARCHITECTURE_ENHANCED.md",
                "REORGANIZATION_COMPLETE.md"
            ]
        }
        
        for target_dir, patterns in archive_moves.items():
            for pattern in patterns:
                files = list(self.project_root.glob(pattern))
                for file_path in files:
                    if file_path.is_file():
                        target_path = self.project_root / target_dir / file_path.name
                        if not self.dry_run:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(target_path))
                            self.moved_files.append((str(file_path), str(target_path)))
                            logger.info(f"📦 Moved: {file_path.name} → {target_dir}")
                        else:
                            logger.info(f"🔍 DRY RUN: Would move {file_path.name} → {target_dir}")
    
    def delete_redundant_files(self):
        """Delete redundant and duplicate files"""
        files_to_delete = [
            "README-GITHUB.md",
            ".github-README.md", 
            "EVERYTHING_FIXED.md",
            "WARP.md"  # symlink
        ]
        
        for filename in files_to_delete:
            file_path = self.project_root / filename
            if file_path.exists():
                if not self.dry_run:
                    file_path.unlink()
                    self.deleted_files.append(str(file_path))
                    logger.info(f"🗑️  Deleted: {filename}")
                else:
                    logger.info(f"🔍 DRY RUN: Would delete {filename}")
    
    def consolidate_guides(self):
        """Consolidate overlapping documentation"""
        consolidations = {
            "docs/getting-started/installation.md": [
                "GETTING_STARTED.md",
                "SETUP_GUIDE.md", 
                "INSTALLATION_GUIDE.md"
            ],
            "docs/guides/quickstart.md": [
                "QUICK_REFERENCE.md",
                "QUICKSTART.md",
                "START_HERE.md"
            ],
            "docs/architecture/overview.md": [
                "ARCHITECTURE.md",
                "PROJECT_STRUCTURE.md"
            ]
        }
        
        for target_file, source_files in consolidations.items():
            target_path = self.project_root / target_file
            
            if not self.dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Combine content from source files
                combined_content = []
                combined_content.append(f"# {target_file.split('/')[-1].replace('.md', '').title()}")
                combined_content.append(f"\n> Consolidated from: {', '.join(source_files)}\n")
                
                for source_file in source_files:
                    source_path = self.project_root / source_file
                    if source_path.exists():
                        with open(source_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            combined_content.append(f"\n## From {source_file}\n")
                            combined_content.append(content)
                
                # Write consolidated file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(combined_content))
                
                logger.info(f"📝 Consolidated: {' + '.join(source_files)} → {target_file}")
            else:
                logger.info(f"🔍 DRY RUN: Would consolidate {' + '.join(source_files)} → {target_file}")
    
    def create_documentation_index(self):
        """Create main documentation index"""
        index_content = """# SampleMind AI - Documentation

## Quick Start
- [Installation Guide](getting-started/installation.md) - Complete setup instructions
- [Quickstart Tutorial](guides/quickstart.md) - Get running in 5 minutes
- [User Guide](guides/user-guide.md) - End-user documentation

## Development
- [Developer Guide](development/setup.md) - Development environment setup
- [API Reference](guides/api-reference.md) - Complete API documentation
- [Contributing](development/contributing.md) - How to contribute

## Architecture
- [System Overview](architecture/overview.md) - High-level architecture
- [Database Schema](architecture/database-schema.md) - Data models
- [Security Design](architecture/security.md) - Security architecture

## Platform Guides
- [Linux Setup](guides/platform-guides/linux.md)
- [macOS Setup](guides/platform-guides/macos.md) 
- [Windows Setup](guides/platform-guides/windows.md)

## Reference
- [CLI Commands](reference/cli-commands.md) - Command reference
- [Configuration](reference/configuration.md) - Configuration options
- [Troubleshooting](reference/troubleshooting.md) - Common issues

## Archive
Historical documentation is available in the [archive](archive/) directory.
"""
        
        index_path = self.project_root / "docs" / "README.md"
        if not self.dry_run:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            logger.info("📋 Created documentation index: docs/README.md")
        else:
            logger.info("🔍 DRY RUN: Would create documentation index")
    
    def generate_report(self):
        """Generate cleanup report"""
        report = f"""
# Documentation Cleanup Report

## Summary
- Files moved to archive: {len(self.moved_files)}
- Files deleted: {len(self.deleted_files)}
- New directory structure created
- Documentation index created

## Moved Files
"""
        for source, target in self.moved_files:
            report += f"- {source} → {target}\n"
        
        report += "\n## Deleted Files\n"
        for deleted_file in self.deleted_files:
            report += f"- {deleted_file}\n"
        
        report_path = self.project_root / "DOCUMENTATION_CLEANUP_REPORT.md"
        if not self.dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info("📊 Generated cleanup report: DOCUMENTATION_CLEANUP_REPORT.md")
        else:
            logger.info("🔍 DRY RUN: Would generate cleanup report")
    
    def run_cleanup(self):
        """Execute the complete cleanup process"""
        logger.info("🚀 Starting documentation cleanup...")
        
        # Phase 1: Backup and setup
        self.create_backup()
        self.create_new_structure()
        
        # Phase 2: Archive and delete
        self.move_to_archive()
        self.delete_redundant_files()
        
        # Phase 3: Consolidate
        self.consolidate_guides()
        self.create_documentation_index()
        
        # Phase 4: Report
        self.generate_report()
        
        logger.info("✅ Documentation cleanup completed!")
        if self.dry_run:
            logger.info("🔍 This was a DRY RUN - no files were actually modified")
            logger.info("💡 Run with --execute to perform actual cleanup")

def main():
    parser = argparse.ArgumentParser(description="SampleMind AI Documentation Cleanup")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry run)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirm execution if not dry run
    if args.execute:
        response = input("⚠️  This will modify your documentation structure. Continue? (y/N): ")
        if response.lower() != 'y':
            logger.info("❌ Cleanup cancelled")
            return
    
    cleaner = DocumentationCleaner(
        project_root=args.project_root,
        dry_run=not args.execute
    )
    
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()
