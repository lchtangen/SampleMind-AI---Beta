# CLAUDE.md

Comprehensive guidance for Claude Code when working with SampleMind AI codebase. This document covers architecture, development workflow, and UI/UX best practices for both CLI and web interfaces.

## Development Commands

### CLI Development (Primary Focus)
- `source .venv/bin/activate && python main.py` - Run CLI application (main product)
- `make setup` - Complete development environment setup (creates .venv, installs dependencies)
- `make install-models` - Download offline AI models (phi3:mini, qwen2.5:7b-instruct, gemma2:2b for Ollama)
- `scripts/launch-ollama-api.sh` - Launch Ollama API server for offline-first inference
- `scripts/setup/quick_start.sh` - Quick project startup with all CLI dependencies

### API and Services
- `make dev` - Start development server (uvicorn on localhost:8000)
- `make dev-full` - Start full development stack with Docker services
- `make setup-db` - Start development databases (MongoDB, Redis, ChromaDB via Docker)

### Testing and Quality
- `make test` - Run all tests with coverage (`pytest tests/ -v --cov=src --cov-report=term-missing`)
- `make lint` - Run linters (`ruff check .` and `mypy src/`)
- `make format` - Format code (`black .` and `isort .`)
- `make security` - Run security checks (`bandit -r src/` and `safety check`)
- `make quality` - Run all quality checks (lint + security)

### Docker and Deployment
- `make build` - Build Docker image
- `docker-compose up -d` - Start all services in containers
- `make clean` - Clean temporary files and caches

## UI/UX Development Guidelines

### Terminal UI (CLI/TUI) - Textual Framework

#### Core Principles
- **User-First Design**: Keyboard-first navigation with mouse support as enhancement
- **Performance**: <50ms response time for UI interactions (keyboard input, animations)
- **Accessibility**: Support keyboard navigation, screen readers, high contrast themes
- **Consistency**: Unified color palette, typography, spacing across all screens
- **Feedback**: Clear visual feedback for every user action (highlights, animations, status)

#### Textual Component Development
```python
# Location: src/samplemind/interfaces/tui/components/

# ✅ DO:
- Inherit from `Screen` or `Widget` appropriately
- Use `watch_` methods for reactive state changes
- Compose widgets for reusability (small, focused components)
- Implement `compose()` for layout, `render()` for styling
- Use `call_later()` for async operations to avoid blocking UI
- Leverage CSS for styling (stored in .css files alongside components)
- Add loading states and progress indicators
- Validate user input in real-time with visual feedback

# ❌ DON'T:
- Block the event loop with long-running operations
- Use blocking I/O in render methods
- Mix CSS in Python code
- Create monolithic mega-components
- Ignore keyboard navigation
```

#### Theme and Styling
- **Color System**: 12 built-in themes available (`make dev` to test)
- **Design Tokens**: Define colors, spacing, typography in `tui/theme/` directory
- **CSS Files**: Each component should have corresponding `.css` file for styling
- **Accessibility**: Ensure 4.5:1 contrast ratio for all text, test in high-contrast mode
- **Dark/Light**: Themes support both dark (primary) and light modes

#### Testing Terminal UI Components
```bash
# Test interactive behavior
python -m pytest tests/unit/tui/ -v --capture=no

# Test on different terminals
# Test in: gnome-terminal, kitty, alacritty, iterm2, Windows Terminal

# Visual regression testing
# Run manually and compare with previous screenshots
```

#### Common Patterns
- **Modal Dialogs**: Use `Screen` with `BINDINGS` for modal behavior
- **Input Validation**: Show inline errors below input fields
- **Loading States**: Use spinners and progress bars (`LoadingIndicator`, `ProgressBar`)
- **Command Palette**: Tab-completion for common actions
- **Status Bar**: Always visible footer with current state/help text
- **Breadcrumbs**: Show navigation hierarchy for nested screens

### Web UI (React/Next.js) - `apps/web/`

#### Core Architecture
- **Framework**: Next.js 14+ with React 18+
- **Styling**: Tailwind CSS for utility-first styling
- **State Management**: React hooks + Context API (avoid Redux unless needed)
- **API Integration**: Fetch from FastAPI backend (localhost:8000/api/v1/)
- **Deployment**: Vercel or self-hosted via Docker

#### Component Structure
```
apps/web/src/
├── components/          # Reusable components
│   ├── audio/          # Audio-specific components
│   ├── common/         # Button, Input, Modal, etc.
│   ├── layouts/        # Page layouts
│   └── features/       # Feature-specific components
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── styles/             # Global CSS, Tailwind config
├── app/                # Next.js app router pages
└── lib/                # Library code (API clients, formatters)
```

#### React Development Best Practices
- **Components**: Prefer functional components with hooks
- **State Management**:
  - Local state for simple UI state (useState)
  - Context API for global state (theme, auth, workspace)
  - Server state via API (audio files, analysis results)
- **Performance**:
  - Use React.memo for expensive components
  - Lazy load routes with React.lazy + Suspense
  - Optimize images with Next.js Image component
  - Code split by route automatically
- **Accessibility**:
  - Use semantic HTML (buttons, links, forms)
  - Include proper ARIA labels
  - Test with keyboard navigation
  - Ensure 4.5:1 contrast ratios

#### Styling Strategy
- **Tailwind CSS**: Primary styling approach
- **CSS Modules**: For component-scoped styles if needed
- **Global CSS**: In `styles/globals.css` only
- **Design System**: Extend Tailwind config in `tailwind.config.ts`
  ```typescript
  // Define design tokens: colors, spacing, typography, shadows
  ```
- **Dark Mode**: Built-in support via Tailwind dark mode
- **Responsive**: Mobile-first approach (sm, md, lg, xl breakpoints)

#### Form Handling
```typescript
// ✅ Use React Hook Form for complex forms
import { useForm } from 'react-hook-form'

// API validation errors → display on form fields
// Real-time validation with debouncing
// Submission loading state
```

#### API Integration
```typescript
// Location: apps/web/src/lib/api/

// Create typed API client
interface AudioAnalysisResult { /* ... */ }

async function analyzeAudio(file: File): Promise<AudioAnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/v1/audio/analyze', {
    method: 'POST',
    body: formData,
  })

  return response.json()
}

// Use in components with proper error handling & loading states
```

#### Testing Web Components
```bash
# Unit tests
npm run test -- components/

# E2E tests
npm run test:e2e

# Visual regression
npm run test:visual

# Accessibility audits
npm run test:a11y
```

### Cross-Platform UI Consistency

#### Design Decisions
- **CLI Primary, Web Secondary**: CLI is the main product, web supplements it
- **Feature Parity**: Critical features available in both interfaces
- **Platform Differences**: Leverage native capabilities
  - CLI: Terminal aesthetics, fast keyboard-driven workflows
  - Web: Drag-and-drop, rich visualizations, collaborative features
- **Responsive**: Both interfaces work across device sizes

#### Breaking Down Features
When implementing a feature:
1. **CLI First**: Implement in CLI with all logic/algorithms
2. **Web Later**: Reuse backend logic via FastAPI, create web UI
3. **Test Both**: Ensure feature works identically in both interfaces
4. **Optimize Separately**: CLI for speed, web for richness

### User Experience Best Practices

#### Information Architecture
- **Clear Navigation**: Users always know where they are
- **Progressive Disclosure**: Show only relevant options at each step
- **Shortcuts**: Power users can bypass dialogs (e.g., drag file to analyze)
- **Defaults**: Smart defaults that work for 80% of users

#### Feedback and Responsiveness
- **Immediate Response**: Even if action takes time, show confirmation immediately
- **Progress Indication**: For operations >1 second, show progress
- **Error Messages**: Specific, actionable, with recovery suggestions
  - Bad: "Error"
  - Good: "Failed to analyze audio. Ensure file is valid MP3/WAV (try with sample.wav)"
- **Success Confirmation**: Brief feedback that action succeeded

#### Performance from User Perspective
- **Perceived Performance**: Skeleton screens, spinners, progress bars
- **Actual Performance**: <100ms for interactions, <500ms for file operations
- **Offline Support**: Graceful degradation when offline, queue operations
- **Caching**: Cache analysis results, library searches, suggestions

#### Accessibility Standards (WCAG 2.1 AA)
- **Keyboard Navigation**: All features accessible via keyboard alone
- **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Focus Management**: Clear, visible focus indicators
- **Screen Reader Support**: Proper semantic HTML, ARIA labels
- **Motion**: Respect `prefers-reduced-motion` setting
- **Text Alternatives**: Alt text for images, captions for audio

### Design System & Tokens

#### Color System (Light & Dark Modes)
```
Primary:     For main actions and highlights
Secondary:   For alternative actions
Success:     For positive feedback (✓ analyzed)
Warning:     For caution (⚠ API rate limit)
Error:       For failures (✗ analysis failed)
Neutral:     For backgrounds and borders
```

#### Typography
- **Headings**: Clear hierarchy (h1 > h2 > h3)
- **Body**: Consistent line-height (1.5), spacing between paragraphs
- **Code**: Monospace font, proper syntax highlighting
- **Emphasis**: Bold for important, italic for citations

#### Spacing System
- **Base Unit**: 4px or 8px (define in Tailwind config)
- **Consistent Scale**: 4, 8, 12, 16, 24, 32, 48, 64...
- **Breathing Room**: Margins equal half the component height

### Workflow Integration

#### Before Starting UI Work
1. Check if feature exists in CLI - reuse design patterns
2. Review `/docs/03-BUSINESS-STRATEGY/` for design inspiration
3. Test with keyboard navigation and accessibility tools
4. Create/update UI mockup or specification

#### During Development
1. Code the structure first (layout, no styling)
2. Add styling with design tokens
3. Implement interactions (keyboard, mouse, animation)
4. Add loading/error states
5. Test on multiple devices/terminals/browsers
6. Test with accessibility tools (axe, WAVE)

#### Code Review Checklist
- [ ] Keyboard navigation works
- [ ] Loading states present
- [ ] Error messages helpful
- [ ] Accessible to screen readers
- [ ] Performance acceptable (<100ms response)
- [ ] Matches design system
- [ ] Works on target platforms (terminals/browsers)
- [ ] Tests added and passing

## Architecture Overview

### Core System Design
SampleMind AI is a CLI-first, offline-capable AI-powered music production platform with three main architectural layers:

1. **Primary Interface: CLI** (`src/samplemind/interfaces/`)
   - **CLI**: Typer-based command line interface (main product with modern terminal UI)
   - Modern terminal animations and effects for interactive experience
   - Cross-platform support (Linux, macOS, Windows, all terminals)
   - Real-time performance optimization and minimal latency
   - Future secondary interfaces: FastAPI async web service, Web/Electron applications

2. **Hybrid AI Architecture** (`src/samplemind/ai/`)
   - **Primary AI**: Google Gemini 3 Flash for fast, intelligent analysis
   - **Offline-First**: Ultra-fast local models via Ollama (Phi3, Gemma2, Qwen2.5) for <100ms responses without internet
   - **Cloud Fallback**: Gemini for complex analysis, OpenAI/Anthropic Claude as alternatives
   - **Smart Routing**: Automatic model selection based on task complexity and connectivity

3. **Audio Processing Engine** (`src/samplemind/core/engine/`)
   - Real-time audio analysis using librosa, soundfile, scipy
   - Advanced audio classification with basic-pitch, demucs, spleeter tools
   - Feature extraction: tempo, key, chroma, MFCC, spectral features
   - Harmonic/percussive separation and rhythm pattern analysis
   - Multi-level caching system for performance optimization

### Data Layer
- **Vector Database**: ChromaDB for similarity search and embeddings
- **Cache Strategy**: Multi-level (memory, disk, vector) with Redis
- **Primary Database**: MongoDB with async Motor driver
- **Audio Storage**: Organized sample library with metadata

### DAW Integration Strategy
- FL Studio: Native plugin with real-time sync
- Ableton Live: Project-aware sample suggestions
- Logic Pro: Intelligent browser organization
- Plugin formats: VST3, AU for cross-DAW compatibility

## Key Technical Details

### Dependencies and Stack
- **Core**: Python 3.11+, FastAPI, Poetry for dependency management
- **Audio**: librosa, soundfile, scipy, numpy for signal processing
- **AI/ML**: torch, transformers, sentence-transformers, ollama client
- **Database**: motor (MongoDB), redis, chromadb
- **Testing**: pytest with asyncio, coverage, mock support
- **Code Quality**: ruff, black, isort, mypy, bandit for linting and security

### Performance Considerations
- Async processing throughout with ThreadPoolExecutor for CPU-bound tasks
- Feature caching with configurable size limits and SHA-256 file hashing
- Batch processing support for multiple audio files
- Analysis levels: BASIC, STANDARD, DETAILED, PROFESSIONAL for scalable complexity

### Configuration
- Poetry scripts: `samplemind` and `smai` as entry points
- Docker Compose for development services
- Environment-based configuration for different deployment targets
- Pre-commit hooks for code quality enforcement

## Development Workflow (CLI-First)

### CLI Development Process
1. **Setup**: Run `make setup` for complete environment preparation
2. **Offline Models**: Run `make install-models` and `scripts/launch-ollama-api.sh` for offline-first development
3. **CLI Development**: Run CLI directly with `source .venv/bin/activate && python main.py` for interactive testing
4. **Real-time Testing**: Test CLI features immediately with actual user workflows
5. **Quality**: Always run `make quality` before commits
6. **Testing**: Use `make test` to verify changes with coverage reporting

### Performance Optimization Guidelines
- Prioritize CLI response time (target: <1 second for common operations)
- Use offline Ollama models for development to avoid API latency
- Test on lower-performance systems to ensure wide compatibility
- Profile CPU and memory usage regularly with CLI operations
- Cache audio analysis results aggressively to minimize reprocessing

### Cross-Platform Testing
- Test on Linux, macOS, and Windows before major releases
- Test with various terminal emulators (terminals with/without true color support)
- Verify modern terminal UI animations work across all platforms
- Ensure ASCII-only fallback mode for limited terminals

## Development Phases

The project follows a strategic phased approach focused on quality and completeness:

### Phase 1: CLI Development (Current Priority)
- **Goal**: Complete, fully-featured CLI with modern terminal UI
- **Requirements**: 100% feature completeness before proceeding to Phase 2
- **Focus Areas**: Performance optimization, offline-first architecture, cross-platform compatibility
- **AI Integration**: Gemini 3 Flash as primary with offline Ollama fallback
- **Audio Features**: All advanced classification tools (basic-pitch, demucs, spleeter) fully working
- **Quality Gate**: All tests passing, comprehensive coverage, no known bugs

### Phase 2: Preview Video Production
- **Goal**: Professional video showcase of CLI capabilities
- **Content**: Demonstrate core workflows, feature highlights, modern terminal UI
- **Requirements**: Feature completeness from Phase 1 is prerequisite
- **Audience**: Potential beta testers and early adopters

### Phase 3: Beta Testing Program
- **Goal**: Gather real-world feedback from 10-100 early users
- **Process**: Structured testing with feedback collection
- **Improvements**: Refine based on user feedback and usage patterns
- **Duration**: 4-8 weeks of active testing

### Phase 4: Web UI (Post-CLI Release)
- **Goal**: Secondary interface layer for web-based access
- **Requirements**: CLI must be stable and feature-complete
- **Focus**: Supplement CLI, not replace it as primary interface
- **Technologies**: Next.js/React frontend, FastAPI backend integration

## Project File Structure

The project follows a clean, minimal directory structure optimized for VSCode:

### Root Directory (Essential Files Only)
- `README.md` - Main project documentation with quick start guide
- `CLAUDE.md` - This file - AI assistant instructions
- `pyproject.toml` - Python project configuration and dependencies
- `Makefile` - Development commands and automation
- `docker-compose.yml` - Docker service orchestration
- `main.py` - CLI entry point
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community guidelines
- `LICENSE` - MIT license

### Documentation (`docs/`)
All project documentation is centralized here:
- `docs/guides/` - User guides, platform guides (Linux, macOS, Windows), quickstart guides
- `docs/archive/` - Historical task completion files and analysis documents
- `docs/PROJECT_SUMMARY.md` - Comprehensive project overview
- `docs/PROJECT_ROADMAP.md` - Development roadmap and priorities
- `docs/PROJECT_STRUCTURE.md` - Codebase architecture details
- `docs/CURRENT_STATUS.md` - Current development status

### Scripts (`scripts/`)
All executable scripts organized by purpose:
- `scripts/setup/` - Installation and setup scripts (quick_start.sh, platform-specific setup)
- `scripts/start_*.sh` - Service startup scripts (API, CLI, Celery workers)
- `scripts/verify_setup.py` - Environment verification
- `scripts/demo_*.py` - Demo and test scripts

### Source Code (`src/samplemind/`)
Main application code:
- `src/samplemind/core/engine/` - Audio processing engine
- `src/samplemind/integrations/` - AI provider integrations (Google, OpenAI)
- `src/samplemind/interfaces/` - CLI, API, GUI interfaces
- `src/samplemind/utils/` - Utilities (cross-platform file picker, etc.)

### Tests (`tests/`)
Comprehensive test suite:
- `tests/unit/` - Unit tests (81 tests passing, 30% coverage)
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Shared fixtures and configuration

### Configuration (`config/`)
Configuration files for various tools

### Data (`data/`)
Sample audio files, databases, and data storage

## Important Notes

### CLI-First Development Philosophy
- **CLI is the primary product** - focus features and optimizations on the CLI interface
- All UI/UX decisions should prioritize CLI usability and performance
- Modern terminal UI with animations and effects is a core feature, not an afterthought
- Web UI is a secondary interface for Phase 2+, designed to complement (not replace) CLI
- Design principle: "Keyboard first, mouse friendly, touch-friendly on web"

#### When Working on CLI
- Assume 80 characters terminal width as minimum (test on 80x24 terminal)
- Keyboard navigation must be faster than mouse for power users
- Every screen should have a help bar (usually `?` key)
- Use consistent keybindings across all screens
- Test with screen readers (NVDA, JAWS, VoiceOver)

#### When Working on Web UI
- Maintain feature parity with CLI for critical workflows
- Add "web-exclusive" features (visualization, collaboration, drag-and-drop)
- Ensure mobile responsive (test on mobile sizes: 320px, 480px, 768px+)
- Graceful degradation when JavaScript disabled
- API-first: web UI should never have logic the CLI doesn't have

### Offline-First Architecture
- **Ollama local AI models are mandatory for development** - ensure `make install-models` runs successfully
- Prioritize offline functionality: the CLI should work without internet connectivity
- Google Gemini is the primary cloud AI, with offline models as smart fallback
- Performance targets assume offline-first operation (<1 second response time)

#### UI Implications
- Show "offline mode" indicator when no internet detected
- Queue operations when offline, sync when connection restored
- Cache all static content (UI resources, common analysis results)
- Display cached results with "last updated 2 hours ago" label

### Performance and Optimization

#### General
- The project uses Python venv for dependency management - always use `source .venv/bin/activate` or the make commands
- Audio files should be tested with the `AudioEngine` class in `src/samplemind/core/engine/audio_engine.py`
- Aggressive caching of audio analysis results is essential for performance
- Test on lower-performance systems to identify bottlenecks early

#### Terminal UI Performance
- **Interaction Response**: <50ms for keyboard input response
- **Animation Smoothness**: 60 FPS for smooth animations (Textual handles this)
- **Rendering**: <100ms for full screen redraws
- **Avoid**:
  - Synchronous file I/O in render methods
  - Long-running computations in event handlers
  - Re-rendering entire UI for small state changes
- **Profiling Tool**: Use `python -m cProfile` to identify bottlenecks
  ```bash
  python -m cProfile -s cumulative main.py > profile.txt
  ```

#### Web UI Performance
- **First Contentful Paint (FCP)**: <1 second
- **Time to Interactive (TTI)**: <2 seconds
- **Largest Contentful Paint (LCP)**: <2.5 seconds
- **Cumulative Layout Shift (CLS)**: <0.1
- **Interaction to Paint (INP)**: <200ms
- **Code Splitting**: Split by route automatically, lazy load heavy components
- **Images**: Use Next.js Image component with proper sizes/srcSet
- **API Calls**:
  - Deduplicate requests (don't fetch same data twice)
  - Show optimistic updates immediately, sync in background
  - Use SWR or React Query for data fetching patterns
- **Profiling**:
  ```bash
  npm run build  # Shows bundle analysis
  npm run dev    # Chrome DevTools: Performance tab
  ```

#### Target Metrics by Feature
- **Audio Upload**: Show file selector <100ms, accept file <50ms
- **Waveform Render**: Start rendering <500ms, complete <2s for 10min audio
- **Analysis Result**: Show initial result <1s, complete details <3s
- **Search Results**: Show first 5 results <500ms, paginate rest
- **Library Browse**: Load 20 items <500ms, lazy load more on scroll

### Integration and Testing

#### Backend Integration
- All async operations should use the established patterns in the FastAPI application
- Vector embeddings and similarity search are core features - consider ChromaDB integration for new features
- FL Studio integration is a primary use case - test changes against DAW workflow requirements

#### UI-Specific Testing
- **Keyboard Navigation**: Test all features with keyboard only (no mouse)
  ```bash
  # Disable mouse completely during testing
  ```
- **Terminal Emulators**: Test on gnome-terminal, kitty, alacritty, iterm2, Windows Terminal
- **Accessibility**: Use axe DevTools, WAVE, VoiceOver (macOS), NVDA (Windows)
- **Responsive Design**: Test web UI at 320px, 480px, 768px, 1024px, 1440px widths
- **Browser Compatibility**:
  - Chrome/Edge (latest)
  - Firefox (latest)
  - Safari (latest)
  - Mobile Chrome/Safari
- **Color Blindness**: Test with color blindness simulators (Coblis, Color Oracle)
- **Performance**:
  ```bash
  # CLI
  python -m cProfile main.py

  # Web
  npm run build  # Check bundle size
  lighthouse  # Run performance audit
  ```

#### Cross-Platform Compatibility
- CLI must work on Linux, macOS, Windows, and various terminal emulators
- Web UI must work on desktop and mobile browsers
- Never assume terminal features (colors, unicode, mouse support)
- Always provide ASCII-only fallback for limited terminals

### Documentation and Organization
- **All documentation is in `docs/`** - guides, references, and archives are organized there
- **All scripts are in `scripts/`** - setup scripts in `scripts/setup/`, start scripts at root level of scripts/
- Update docs/ for new features before shipping, especially platform-specific guides
- Document UI components with:
  - Purpose and use cases
  - Props/parameters with types
  - Examples of typical usage
  - Accessibility considerations
  - Browser/terminal compatibility

## Common UI Patterns & Anti-Patterns

### ✅ DO: Best Practices

#### Loading States
```python
# Terminal UI - show spinner during analysis
with self.disable():  # Disable interaction
    with Loading():   # Show spinner
        result = await self.analyze_audio(file)
self.show_result(result)

# Web - show skeleton, then real content
<Suspense fallback={<AudioSkeleton />}>
  <AudioAnalysis file={file} />
</Suspense>
```

#### Error Handling
```python
# Terminal UI - show actionable error with recovery options
try:
    result = await api.analyze(file)
except FileNotFoundError:
    self.notify("File not found. Check path and try again.", severity="error")
except APIError:
    self.notify("API offline. Using local model instead.", severity="warning")

# Web - show error in context, with recovery
<div className="error-banner">
  <p>Failed to analyze audio</p>
  <button onClick={retry}>Try again</button>
  <button onClick={useLocal}>Use local model</button>
</div>
```

#### User Input Validation
```python
# Terminal UI - validate as user types
def on_change_filename(self, event: Input.Changed) -> None:
    value = event.value
    if not value:
        self.error_text = "Filename required"
    elif len(value) > 255:
        self.error_text = "Filename too long (max 255)"
    else:
        self.error_text = ""

# Web - validate on blur + submit
const [errors, setErrors] = useState({})
const handleBlur = (field) => {
  const error = validate[field](formData[field])
  setErrors(prev => ({ ...prev, [field]: error }))
}
```

#### Feedback After Action
```python
# Terminal UI - confirm action succeeded
result = await api.save_file(data)
self.notify(f"✓ Saved to {result.path}", severity="success", timeout=2)

# Web - show success with toast/banner
toast.success("Saved successfully")
// Auto-dismiss after 3 seconds
```

### ❌ DON'T: Anti-Patterns

#### ❌ Silent Failures
```python
# BAD: No feedback if operation fails
try:
    result = await api.analyze(file)
except Exception:
    pass  # User has no idea what happened!

# GOOD: Always provide feedback
except Exception as e:
    self.notify(f"Analysis failed: {e}", severity="error")
```

#### ❌ Blocking UI
```python
# BAD: Freezes terminal during file load
files = os.listdir(huge_folder)  # Blocks event loop

# GOOD: Load asynchronously
files = await self.load_files_async(huge_folder)
```

#### ❌ Inconsistent Keybindings
```python
# BAD: Different keybindings on each screen
# Screen 1: Ctrl+S to save
# Screen 2: Ctrl+W to save
# User is confused

# GOOD: Consistent keybindings across all screens
# All screens: Ctrl+S to save, Esc to cancel
```

#### ❌ Inaccessible Colors
```python
# BAD: Only uses color to convey meaning
<span className="text-green">Success</span>  # Colorblind can't tell

# GOOD: Use color + icon + text
<span className="text-green">✓ Success</span>
```

#### ❌ Hiding Important Information
```python
# BAD: User can't see what happened
Analysis complete

# GOOD: Show full results with context
Analysis complete
├─ Tempo: 120 BPM (±2)
├─ Key: C Major
└─ Genre: Electronic Dance Music
```

#### ❌ No Escape Hatch
```python
# BAD: Modal dialog with no way to cancel
"Are you sure?"
[OK] [OK]  # Only option is to proceed!

# GOOD: Always provide escape
"Delete file forever? (cannot undo)"
[Delete] [Cancel] [Help]
```

## Quick Reference for UI Development

### File Locations
- Terminal UI Components: `src/samplemind/interfaces/tui/components/`
- Web Components: `apps/web/src/components/`
- CSS/Styling: `*.css` alongside components
- Tests: `tests/unit/tui/` and `tests/unit/web/`

### Common Tasks
```bash
# Test Terminal UI
python main.py

# Test Web UI
npm run dev  # http://localhost:3000

# Run all tests
make test

# Check accessibility
npm run test:a11y  # web UI
python -m pytest tests/a11y/  # CLI

# Performance profiling
python -m cProfile main.py
npm run build && npm run analyze  # web bundle size
```

### Design Inspiration
- Check `docs/03-BUSINESS-STRATEGY/` for design inspiration
- Review existing components for patterns
- Test on actual target devices/terminals before shipping
