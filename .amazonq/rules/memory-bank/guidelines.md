# SampleMind AI - Development Guidelines

## Code Quality Standards

### Documentation Style
- **Module-level docstrings**: Every module starts with a comprehensive docstring explaining purpose, capabilities, and design goals
- **Multi-line format**: Use triple-quoted strings with detailed descriptions
- **Professional tone**: Documentation reads like technical specifications with clear, actionable information
- **Example pattern**:
```python
"""
SampleMind AI v6 - Core Audio Engine
The heart of the AI music production platform

This module provides comprehensive audio analysis capabilities including:
- Real-time audio processing and analysis
- Feature extraction (tempo, pitch, rhythm, spectral features)
- Audio similarity comparison
- Music information retrieval

Designed specifically for professional music production and FL Studio integration.
"""
```

### Function/Method Documentation
- **Comprehensive docstrings**: Include Args, Returns, Raises sections
- **Type hints**: Always use type annotations for parameters and return values
- **Clear descriptions**: Explain what the function does, not just repeat the name
- **Example pattern**:
```python
def extract_spectral_features(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512
) -> Dict[str, np.ndarray]:
    """
    Extract spectral features from audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
        n_fft: FFT window size
        hop_length: Hop length for STFT
        
    Returns:
        Dictionary of spectral features
    """
```

### Code Formatting
- **Line length**: 88 characters (Black formatter standard)
- **Indentation**: 4 spaces (never tabs)
- **Import organization**: Standard library → Third-party → Local imports, separated by blank lines
- **Blank lines**: Two blank lines between top-level definitions, one between methods
- **String quotes**: Double quotes for docstrings, single or double for regular strings (consistent within file)

### Naming Conventions
- **Classes**: PascalCase (e.g., `AudioEngine`, `GoogleAIMusicProducer`, `BackupConfig`)
- **Functions/Methods**: snake_case (e.g., `analyze_audio`, `extract_spectral_features`, `create_backup`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `ROLE_PERMISSIONS`, `HARM_CATEGORY`)
- **Private methods**: Prefix with single underscore (e.g., `_generate_cache_key`, `_parse_db_url`)
- **Enums**: PascalCase for class, UPPER_CASE for values (e.g., `UserRole.FREE`, `Permission.AUDIO_UPLOAD`)

## Structural Conventions

### Class Organization
1. **Docstring** at the top
2. **Class attributes** (if any)
3. **__init__ method** with comprehensive initialization
4. **Public methods** (main functionality)
5. **Private/helper methods** (prefixed with _)
6. **Static methods** at the end (if applicable)

### Dataclass Usage
- Use `@dataclass` decorator for data-holding classes
- Use `field(default_factory=...)` for mutable defaults (lists, dicts, arrays)
- Include type hints for all fields
- Add helper methods like `to_dict()` and `from_dict()` for serialization
- **Example pattern**:
```python
@dataclass
class AudioFeatures:
    """Comprehensive audio feature representation"""
    duration: float
    sample_rate: int
    channels: int
    tempo: float = 0.0
    beats: List[float] = field(default_factory=list)
    mfccs: np.ndarray = field(default_factory=lambda: np.array([]))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert features to dictionary for JSON serialization"""
```

### Enum Usage
- Use `Enum` for fixed sets of values (models, analysis types, roles)
- Inherit from `str, Enum` for string-based enums
- Use descriptive value names
- **Example pattern**:
```python
class UserRole(str, Enum):
    """User role definitions"""
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"
```

## Semantic Patterns

### Error Handling Pattern
- Use try-except blocks with specific exception types
- Log errors with context using logger
- Provide fallback behavior or raise with enhanced error messages
- **Pattern frequency**: Found in 5/5 analyzed files
```python
try:
    # Operation
    result = perform_operation()
    logger.info(f"✅ Operation complete: {result}")
    return result
except Exception as e:
    logger.error(f"❌ Operation failed: {e}")
    raise
```

### Logging Pattern
- Use emoji prefixes for visual scanning (🎵 🎯 ✅ ❌ 📦 🔄)
- Include contextual information in log messages
- Use appropriate log levels (info, warning, error, debug)
- **Pattern frequency**: Found in 4/5 analyzed files
```python
logger.info(f"🎵 SampleMind Audio Engine initialized with {max_workers} workers")
logger.error(f"❌ Analysis failed for {file_path}: {e}")
logger.debug(f"Extracted rhythmic features in {processing_time:.3f}s")
```

### Async/Await Pattern
- Use `async def` for I/O-bound operations
- Use `await` for async calls
- Use `asyncio.gather()` for parallel execution
- Use `run_in_executor()` for CPU-bound operations in async context
- **Pattern frequency**: Found in 3/5 analyzed files
```python
async def analyze_music_comprehensive(
    self,
    audio_features: Dict[str, Any],
    analysis_type: MusicAnalysisType
) -> AdvancedMusicAnalysis:
    """Ultimate comprehensive music analysis"""
    response = await asyncio.get_event_loop().run_in_executor(
        self.executor,
        lambda: ai_model.generate_content(prompt)
    )
```

### Caching Pattern
- Generate cache keys using hash functions (MD5, SHA-256)
- Check cache before expensive operations
- Track cache hits/misses for performance monitoring
- Implement cache size limits with eviction policies
- **Pattern frequency**: Found in 3/5 analyzed files
```python
cache_key = self._generate_cache_key(file_path, level)
if use_cache and cache_key in self.feature_cache:
    self.cache_hits += 1
    logger.info(f"📦 Cache hit for {file_path.name}")
    return self.feature_cache[cache_key]
```

### Configuration Pattern
- Use Pydantic models or dataclasses for configuration
- Load from environment variables with defaults
- Validate configuration on initialization
- **Pattern frequency**: Found in 3/5 analyzed files
```python
class BackupConfig:
    """Backup configuration"""
    def __init__(
        self,
        backup_dir: str = "./backups",
        retention_days: int = 30,
        compress: bool = True
    ):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
```

### Performance Tracking Pattern
- Track operation counts and timing
- Calculate averages and aggregates
- Provide `get_performance_stats()` method
- **Pattern frequency**: Found in 3/5 analyzed files
```python
self.analysis_times.append(analysis_time)
self.cache_hits += 1

def get_performance_stats(self) -> Dict[str, Any]:
    """Get performance statistics"""
    return {
        'total_analyses': len(self.analysis_times),
        'avg_analysis_time': np.mean(self.analysis_times),
        'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses)
    }
```

## Internal API Usage Patterns

### Audio Processing with librosa
```python
# Standard pattern for audio feature extraction
y, sr = librosa.load(file_path, sr=target_sr)
spectral_centroid = librosa.feature.spectral_centroid(
    y=y, 
    sr=sr, 
    hop_length=hop_length
)
tempo, beat_frames = librosa.beat.beat_track(
    onset_envelope=onset_env,
    sr=sr,
    hop_length=hop_length
)
```

### NumPy Array Handling
```python
# Always validate array dimensions and handle edge cases
if not isinstance(y, np.ndarray) or y.ndim != 1:
    raise ValueError("Input must be a 1D numpy array")

# Use numpy operations for efficiency
mean_value = np.mean(features)
normalized = features / (np.max(np.abs(features)) + 1e-8)
```

### Path Handling
```python
# Use pathlib.Path for cross-platform compatibility
file_path = Path(file_path)
if not file_path.exists():
    raise FileNotFoundError(f"File not found: {file_path}")

backup_file = self.config.backup_dir / f"{backup_name}.sql"
```

### Dictionary Mapping Pattern
```python
# Use dictionaries for configuration and mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.FREE: {
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_ANALYZE,
    },
    UserRole.PRO: {
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_BATCH_PROCESS,
    }
}
```

### ThreadPoolExecutor Pattern
```python
# Initialize executor for parallel processing
self.executor = ThreadPoolExecutor(max_workers=max_workers)

# Submit tasks
future = self.executor.submit(self.analyze_audio, file_path, level)
result = future.result()

# Cleanup
self.executor.shutdown(wait=True)
```

## Common Code Idioms

### Safe Division with Epsilon
```python
# Prevent division by zero
normalized = value / (max_value + 1e-8)
ratio = numerator / (denominator + 1e-6)
```

### List Comprehension for Filtering
```python
# Efficient filtering and transformation
numpy_fields = ['chroma_features', 'mfccs', 'harmonic_content']
for field in numpy_fields:
    if field in data and isinstance(data[field], list):
        data[field] = np.array(data[field])
```

### Context Managers for Resources
```python
# File handling with automatic cleanup
with open(file_path, 'rb') as f:
    for chunk in iter(lambda: f.read(4096), b''):
        hash_sha256.update(chunk)

with gzip.open(compressed_file, 'wb', compresslevel=6) as f_out:
    shutil.copyfileobj(f_in, f_out)
```

### Enum Value Extraction
```python
# Convert enums to values for serialization
if isinstance(value, Enum):
    result[key] = value.value
```

### Optional Parameter Handling
```python
# Use None as default, then set actual default
def analyze_audio(
    self,
    file_path: Union[str, Path],
    level: AnalysisLevel = AnalysisLevel.STANDARD,
    use_cache: bool = True
) -> AudioFeatures:
    """Comprehensive audio analysis"""
```

## Frequently Used Annotations

### Type Hints
- `Optional[T]`: Value can be T or None
- `Union[T1, T2]`: Value can be T1 or T2
- `List[T]`: List of T items
- `Dict[K, V]`: Dictionary with K keys and V values
- `Tuple[T1, T2]`: Tuple with specific types
- `Any`: Any type (use sparingly)

### Dataclass Decorators
- `@dataclass`: Convert class to dataclass
- `field(default_factory=list)`: Mutable default value
- `field(default_factory=lambda: np.array([]))`: Complex default

### Property Decorators
```python
@property
def total_analyses(self) -> int:
    """Alias for analysis_count for backwards compatibility"""
    return self.analysis_count
```

### Static Method Decorator
```python
@staticmethod
def normalize_audio(y: np.ndarray, target_lufs: float = -23.0) -> np.ndarray:
    """Normalize audio to target LUFS level"""
```

## Best Practices Summary

1. **Always use type hints** for function parameters and return values
2. **Write comprehensive docstrings** with Args, Returns, Raises sections
3. **Use dataclasses** for data structures with many fields
4. **Implement caching** for expensive operations
5. **Track performance metrics** (timing, counts, cache hits)
6. **Use async/await** for I/O-bound operations
7. **Handle errors gracefully** with try-except and logging
8. **Use emoji in logs** for visual scanning (🎵 ✅ ❌ 📦)
9. **Validate inputs** before processing (type, shape, range)
10. **Use pathlib.Path** for file operations
11. **Add epsilon to denominators** to prevent division by zero
12. **Use enums** for fixed sets of values
13. **Implement to_dict/from_dict** for serialization
14. **Use ThreadPoolExecutor** for CPU-bound parallel tasks
15. **Clean up resources** with shutdown methods and context managers

## Testing Patterns

### Test File Organization
- Place tests in `tests/` directory mirroring source structure
- Use `test_` prefix for test files and functions
- Use `conftest.py` for shared fixtures

### Fixture Usage
```python
@pytest.fixture
def audio_engine():
    """Create audio engine for testing"""
    engine = AudioEngine(max_workers=2)
    yield engine
    engine.shutdown()
```

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_analysis():
    """Test asynchronous audio analysis"""
    result = await engine.analyze_audio_async(file_path)
    assert result.tempo > 0
```
