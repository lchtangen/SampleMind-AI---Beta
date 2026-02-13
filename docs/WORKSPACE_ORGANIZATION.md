# Workspace Organization Guide

**Last Updated:** February 13, 2026  
**Purpose:** Document the organized workspace structure for SampleMind AI Beta release

---

## Overview

The SampleMind AI workspace has been reorganized for clarity, maintainability, and ease of navigation as we prepare for the beta release. This guide explains the new structure and where to find everything.

---

## Root Directory Structure

### Essential Files (Kept at Root)

These files remain at the root level as they are essential for GitHub visibility and project access:

- **README.md** - Main project documentation and quick start guide
- **CONTRIBUTING.md** - Contribution guidelines for developers
- **CODE_OF_CONDUCT.md** - Community guidelines and conduct policies
- **CHANGELOG.md** - Version history and change log
- **LICENSE** - MIT license file
- **CLAUDE.md** - AI assistant instructions and development guidelines
- **RELEASE_NOTES_v2.1.0-beta.md** - Current release notes

### Configuration Files

- **pyproject.toml** - Python project configuration and dependencies
- **Makefile** - Development commands and automation
- **docker-compose.yml** - Docker service orchestration
- **.gitignore** - Git ignore patterns
- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- Various config files for tools (pytest.ini, .coveragerc, etc.)

### Entry Points

- **main.py** - Primary CLI entry point for development

---

## Directory Organization

### `/docs/` - All Documentation

Centralized location for all project documentation:

```
docs/
├── 00-INDEX/              # Navigation and quick references
├── 01-PHASES/             # Phase-specific documentation (Phases 1-10+)
├── 02-ROADMAPS/           # Strategic planning and feature roadmaps
├── 03-BUSINESS-STRATEGY/  # Business plans and go-to-market strategy
├── 04-TECHNICAL-IMPLEMENTATION/ # Developer guides, API docs, architecture
└── archive/               # Historical documentation (see below)
```

**Key Documentation:**
- [Documentation Index](./docs/00-INDEX/README.md) - Central navigation hub
- [Getting Started](./docs/04-TECHNICAL-IMPLEMENTATION/guides/START_HERE.md) - Setup guide
- [Phase Status Dashboard](./docs/00-INDEX/PHASE_STATUS_DASHBOARD.md) - Project status

### `/docs/archive/` - Historical Documentation

Archived documentation and reports from development:

```
docs/archive/
├── analysis-reports/      # Code quality and analysis reports
├── sessions/             # Development session summaries
├── completion-reports/   # Historical completion reports
├── deprecated/           # Deprecated documentation
└── historical-plans/     # Old planning documents
```

**Purpose:**
- Preserve development history
- Maintain context for past decisions
- Reference for future development

See [Archive README](./docs/archive/README.md) for details.

### `/src/` - Source Code

Main application code organized by function:

```
src/samplemind/
├── core/                 # Core audio processing engine
├── integrations/         # AI provider integrations
├── interfaces/           # CLI, API, GUI interfaces
└── utils/               # Utility functions
```

### `/tests/` - Test Suite

Comprehensive test coverage:

```
tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
├── e2e/                # End-to-end tests
└── fixtures/           # Test fixtures and data
    └── audio/          # Test audio files
```

**Note:** Test audio files (`.wav`, `.mp3`) are now in `tests/fixtures/audio/` instead of project root.

### `/scripts/` - Scripts and Utilities

Organized scripts for various purposes:

```
scripts/
├── setup/              # Installation and setup scripts
├── debug/              # Debug and diagnostic scripts
├── start_*.sh         # Service startup scripts
└── verify_setup.py    # Environment verification
```

**Moved Files:**
- `debug_forensics.py` → `scripts/debug/`
- `create_test_audio.py` → `scripts/debug/`

### `/examples/` - Example Code

Example implementations and experimental code:

```
examples/
├── main_enhanced.py    # Enhanced entry point example
└── README.md          # Examples documentation
```

**Purpose:**
- Showcase advanced patterns
- Experimental implementations
- Learning resources

### `/config/` - Configuration Files

Configuration files for various tools and services.

### `/plugins/` - DAW Plugins

FL Studio, Ableton, and other DAW integrations.

### `/apps/` - Web Applications

Web UI and related applications (future development).

---

## What Was Moved

### Documentation Reorganization

**Moved to `docs/01-PHASES/`:**
- PHASE1_COMPLETE.md
- PHASES_8_9_10_COMPLETION.md
- PHASE_10_IMPLEMENTATION_GUIDE.md
- PHASE_10_QA_SUMMARY.md

**Moved to `docs/02-ROADMAPS/`:**
- BETA_FEATURES_v2.2.md
- BETA_RELEASE.md
- MULTI_TRACK_PLAN.md

**Moved to `docs/04-TECHNICAL-IMPLEMENTATION/guides/`:**
- MODERN_MENU_QUICK_START.md
- PLUGIN_INSTALLATION_GUIDE.md
- QUICK_ACTION_GUIDE.md

**Moved to `docs/archive/`:**
- A_PLUS_ACHIEVEMENT.md
- IMPROVEMENT_STRATEGY.md
- SETUP_COMPLETE.md
- VISUAL_SUMMARY.txt

**Moved to `docs/archive/analysis-reports/`:**
- ANALYSIS_COMPLETE.md
- ANALYSIS_RESULTS.md
- BETA_POLISH_ANALYSIS.md
- BETA_POLISH_SUMMARY.md
- CODE_QUALITY_REPORT.md
- CODE_QUALITY_SESSION_REPORT.md

**Moved to `docs/archive/sessions/`:**
- SESSION_COMPLETE.md
- SESSION_SUMMARY_2026-02-03.md

### Code and Resource Reorganization

**Moved to `tests/fixtures/audio/`:**
- neural_test.wav
- integration_test.wav

**Moved to `scripts/debug/`:**
- debug_forensics.py
- create_test_audio.py

**Moved to `examples/`:**
- main_enhanced.py

---

## .gitignore Updates

Added entries for test session directories:
```
.test_sessions/
.test_favorites/
```

These directories contain local test data and should not be committed.

---

## Benefits of New Organization

### For Developers

1. **Cleaner Root Directory** - Only essential files at root level
2. **Logical Structure** - Easy to find documentation and code
3. **Better Navigation** - Clear separation of concerns
4. **Reduced Confusion** - No duplicate or outdated docs at root

### For New Contributors

1. **Clear Entry Points** - README.md leads to all documentation
2. **Organized Guides** - All guides in predictable locations
3. **Historical Context** - Archive preserves development history
4. **Example Code** - Examples directory for learning

### For Beta Release

1. **Professional Appearance** - Clean, organized repository
2. **Easy Onboarding** - New users find what they need quickly
3. **Maintainability** - Easier to update and maintain documentation
4. **Scalability** - Structure supports future growth

---

## Finding Documentation

### Quick Reference

| What You Need | Location |
|---------------|----------|
| Getting Started | `README.md` → `docs/04-TECHNICAL-IMPLEMENTATION/guides/START_HERE.md` |
| CLI Commands | `docs/CLI_REFERENCE.md` |
| Plugin Installation | `docs/04-TECHNICAL-IMPLEMENTATION/guides/PLUGIN_INSTALLATION_GUIDE.md` |
| API Documentation | `docs/API_DOCUMENTATION.md` |
| Phase Status | `docs/00-INDEX/PHASE_STATUS_DASHBOARD.md` |
| Contributing | `CONTRIBUTING.md` |
| Change History | `CHANGELOG.md` |
| Old Reports | `docs/archive/` |

### Documentation Index

All documentation is indexed at:
- **[Main Index](./docs/00-INDEX/README.md)** - Central documentation hub
- **[Quick Reference](./docs/00-INDEX/QUICK_REFERENCE.md)** - Fast access guide

---

## Updating Documentation

When adding new documentation:

1. **Choose the Right Location:**
   - User guides → `docs/04-TECHNICAL-IMPLEMENTATION/guides/`
   - Phase docs → `docs/01-PHASES/`
   - Planning → `docs/02-ROADMAPS/`
   - Business → `docs/03-BUSINESS-STRATEGY/`

2. **Update the Index:**
   - Add entry to `docs/00-INDEX/README.md`
   - Update relevant quick references

3. **Check Links:**
   - Ensure all relative links work
   - Update links to moved files

4. **Archive Old Docs:**
   - Move superseded docs to `docs/archive/`
   - Update archive README

---

## Questions?

If you can't find something or have suggestions for improving the organization:

1. Check the [Documentation Index](./docs/00-INDEX/README.md)
2. Search the repository: `grep -r "keyword" docs/`
3. Check the archive: `docs/archive/README.md`
4. Open an issue for suggestions

---

## Maintenance

This organization should be maintained by:

- Keeping root directory minimal (only essential files)
- Moving completed/archived docs to appropriate locations
- Updating links when files are moved
- Documenting new directories in this guide
- Regular cleanup of test files and temporary data

**Last Review:** February 13, 2026  
**Next Review:** Before Phase 2 (Preview Video Production)
