# Comprehensive CLI Command Test Suite

## Overview

This directory contains **130+ comprehensive unit tests** for all SampleMind AI CLI commands, organized into 5 test modules covering all major functionality areas.

## Test Coverage

### 1. Analyze Commands (`test_analyze_commands.py`) - **40+ tests**

Tests for audio analysis and feature extraction:

- **Core Analysis Commands (7 tests)**
  - `analyze:full` - Comprehensive DETAILED level analysis
  - `analyze:standard` - Standard analysis (recommended)
  - `analyze:basic` - Quick basic analysis
  - `analyze:professional` - Professional-grade analysis
  - `analyze:quick` - Ultra-fast analysis

- **Feature Extraction Commands (9 tests)**
  - `analyze:bpm` - BPM detection only
  - `analyze:key` - Key detection only
  - `analyze:mood` - Mood analysis
  - `analyze:genre` - Genre classification
  - `analyze:instrument` - Instrument recognition
  - `analyze:vocal` - Vocal detection
  - `analyze:quality` - Quality scoring
  - `analyze:energy` - Energy level detection

- **Advanced Analysis Commands (8 tests)**
  - `analyze:spectral` - Spectral analysis
  - `analyze:harmonic` - Harmonic/percussive separation
  - `analyze:percussive` - Percussive analysis
  - `analyze:mfcc` - MFCC extraction
  - `analyze:chroma` - Chroma features
  - `analyze:onset` - Onset detection
  - `analyze:beats` - Beat detection
  - `analyze:segments` - Segment detection

- **Output Format Tests (4 tests)**
  - JSON, CSV, YAML, table formats

- **Error Handling Tests (4 tests)**
  - File not found, unsupported format, corrupted audio, permission denied

- **Batch Commands (3 tests)**
  - `batch:analyze` - Batch processing with filters
  - Empty directory handling

- **Performance Tests (2 tests)**
  - Response time benchmarks
  - Target: <5s for basic, <10s for standard

### 2. Library Commands (`test_library_commands.py`) - **25+ tests**

Tests for library management and organization:

- **Organization Commands (6 tests)**
  - `library:scan` - Scan and index directory
  - `library:organize` - Auto-organize by metadata
  - `library:import` - Import with metadata
  - `library:export` - Export with metadata
  - `library:sync` - Cloud sync

- **Search & Filter Commands (6 tests)**
  - `library:search` - Full-text search
  - `library:filter:bpm` - Filter by BPM range
  - `library:filter:key` - Filter by key
  - `library:filter:genre` - Filter by genre
  - `library:filter:tag` - Filter by tag
  - `library:find-similar` - Find similar samples

- **Collection Commands (4 tests)**
  - `collection:create` - Create new collection
  - `collection:add` - Add sample to collection
  - `collection:list` - List collections
  - `collection:export` - Export collection

- **Cleanup Commands (4 tests)**
  - `library:dedupe` - Find duplicates
  - `library:cleanup` - Remove broken files
  - `library:verify` - Verify integrity
  - `library:rebuild-index` - Rebuild index

- **Error Handling Tests (3 tests)**
  - Invalid directory, empty query, collection not found, invalid BPM range

- **Performance Tests (2 tests)**
  - Scan performance (<30s for typical library)
  - Search performance (<2s for queries)

### 3. AI Commands (`test_ai_commands.py`) - **15+ tests**

Tests for AI-powered features:

- **AI Analysis Commands (6 tests)**
  - `ai:analyze` - AI-powered comprehensive analysis
  - `ai:classify` - AI classification
  - `ai:tag` - AI auto-tagging
  - `ai:suggest` - Similar sample suggestions
  - `ai:coach` - Production coaching
  - `ai:presets` - Generate EQ/compressor presets

- **Provider Configuration Commands (6 tests)**
  - `ai:provider` - Set AI provider (gemini, openai, ollama)
  - `ai:key` - Configure API key
  - `ai:model` - Set AI model
  - `ai:test` - Test AI connection

- **Offline Mode Tests (2 tests)**
  - Offline-first Ollama support
  - Fallback to Ollama on network error

- **Error Handling Tests (5 tests)**
  - Missing API key, network timeout, rate limit, invalid provider, invalid key format

- **Performance Tests (2 tests)**
  - AI response time benchmarks
  - Offline fast response (<2s for Ollama)

### 4. Error Handling (`test_cli_error_handling.py`) - **30+ tests**

Comprehensive error handling across all commands:

- **File Operation Errors (4 tests)**
  - File not found, permission denied, directory vs file mismatch, file too large

- **Audio Format Errors (4 tests)**
  - Unsupported format, corrupted audio, empty file, silent audio

- **Network & API Errors (5 tests)**
  - Network timeout, connection refused, rate limit, authentication error, server error

- **Configuration Errors (3 tests)**
  - Missing API key, invalid config file, invalid setting value

- **Resource Errors (3 tests)**
  - Disk full, out of memory, cache full

- **Input Validation Errors (5 tests)**
  - Invalid output format, invalid BPM range, invalid limit, empty query, missing argument

- **Keyboard Interrupt Handling (2 tests)**
  - Graceful Ctrl+C handling, batch operation interruption

- **Error Message Quality (3 tests)**
  - Helpful suggestions, no stack traces for user errors, verbose mode details

- **Error Recovery & Retry (2 tests)**
  - Transient error retry, exponential backoff

### 5. Output Formats (`test_output_formats.py`) - **20+ tests**

Tests for different output formats:

- **JSON Format (4 tests)**
  - Valid JSON output, all fields included, file output, nested structure preservation

- **CSV Format (4 tests)**
  - Valid CSV, header row, special character escaping, batch operations

- **YAML Format (3 tests)**
  - Valid YAML, parseable structure

- **Table Format (3 tests)**
  - Default format, human-readable, color formatting

- **Quiet & Verbose Modes (3 tests)**
  - Minimal quiet output, detailed verbose output, timing information

- **Output File Handling (3 tests)**
  - Save to file, existing file handling, permission denied

- **Streaming Output (3 tests)**
  - Batch streaming, progress indicators

## Running the Tests

### Run all CLI tests
```bash
pytest tests/unit/cli/ -v
```

### Run specific test module
```bash
pytest tests/unit/cli/test_analyze_commands.py -v
```

### Run specific test class
```bash
pytest tests/unit/cli/test_analyze_commands.py::TestAnalyzeCoreCommands -v
```

### Run specific test
```bash
pytest tests/unit/cli/test_analyze_commands.py::TestAnalyzeCoreCommands::test_analyze_full_valid_file -v
```

### Run with coverage
```bash
pytest tests/unit/cli/ --cov=src/samplemind/interfaces/cli --cov-report=html
```

### Run only performance tests
```bash
pytest tests/unit/cli/ -m performance -v
```

### Run only AI tests
```bash
pytest tests/unit/cli/ -m ai -v
```

### Run with specific markers
```bash
pytest tests/unit/cli/ -m "unit and cli" -v
```

## Test Fixtures

All tests use fixtures from `tests/conftest.py`:

- `typer_runner` - Typer CLI test runner
- `cli_app` - CLI application instance
- `test_audio_samples` - Sample audio files (120 BPM C major, 140 BPM A minor, noise)
- `temp_directory` - Temporary directory for test files
- `performance_timer` - Performance timing utilities
- `mock_cli_context` - Mock CLI context with directories
- `sample_cli_config` - Sample CLI configuration
- `clean_environment` - Clean environment variables

## Test Strategy

### Mocking Strategy
- Uses `unittest.mock` for mocking external dependencies
- Audio engine operations mocked to avoid processing overhead
- API calls mocked to avoid rate limits and network issues
- Database operations mocked for isolation

### Error Testing
- Tests both expected error cases and edge cases
- Validates error messages are user-friendly
- Checks error codes and exit statuses
- Tests error recovery and fallbacks

### Performance Testing
- Tests execution time meets targets
- Measures response times for critical operations
- Identifies performance regressions
- Includes batch operation throughput

## Test Statistics

| Category | Test Count | Coverage |
|----------|-----------|----------|
| Analyze Commands | 40+ | All 40 commands + edge cases |
| Library Commands | 25+ | All 50+ library commands |
| AI Commands | 15+ | All 15 AI commands |
| Error Handling | 30+ | Major error scenarios |
| Output Formats | 20+ | All formats + modes |
| **TOTAL** | **130+** | **All CLI functionality** |

## Success Criteria

✅ All 130+ tests pass
✅ 90%+ code coverage on CLI commands
✅ Performance targets met (basic <5s, standard <10s, search <2s)
✅ All error scenarios handled gracefully
✅ User-friendly error messages
✅ Output formats validated
✅ No memory leaks or resource issues

## Continuous Integration

Tests run automatically on:
- Every commit (via pre-commit hook)
- Every push to main branch
- Pull request validation
- Nightly full test run

See `.github/workflows/test.yml` for CI configuration.

## Maintenance

To add new CLI commands:

1. Create new test method in appropriate class
2. Use `@pytest.mark.unit @pytest.mark.cli` decorators
3. Mock external dependencies
4. Test both success and error cases
5. Update test count in this README

## Related Documentation

- [CLI Development Guide](../../docs/CLI_DEVELOPMENT.md)
- [Error Handling Guide](../../docs/ERROR_HANDLING.md)
- [Testing Guide](../../tests/README.md)
- [Pytest Configuration](../../pytest.ini)
