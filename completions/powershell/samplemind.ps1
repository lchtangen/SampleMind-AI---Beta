# SampleMind AI - PowerShell Completion Script
#
# Installation:
#   1. Find your PowerShell profile location:
#      echo $PROFILE
#   2. Add this line to your profile:
#      . "C:\path\to\completions\powershell\samplemind.ps1"
#   3. Reload profile:
#      . $PROFILE
#
# Usage:
#   samplemind [TAB]              - Show all commands
#   samplemind analyze [TAB]      - Show analyze subcommands
#   samplemind -[TAB]             - Show global options

# Register argument completer for samplemind command
Register-ArgumentCompleter -CommandName samplemind -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $ast = $commandAst.ToString()
    $tokens = $ast -split '\s+'
    $cmdIndex = $tokens.IndexOf('samplemind')

    # Global options
    $globalOptions = @(
        [System.Management.Automation.CompletionResult]::new('--help', '--help', 'ParameterValue', 'Show help message')
        [System.Management.Automation.CompletionResult]::new('--version', '--version', 'ParameterValue', 'Show version')
        [System.Management.Automation.CompletionResult]::new('--verbose', '--verbose', 'ParameterValue', 'Verbose output')
        [System.Management.Automation.CompletionResult]::new('--quiet', '--quiet', 'ParameterValue', 'Quiet output')
        [System.Management.Automation.CompletionResult]::new('--config', '--config', 'ParameterValue', 'Configuration file')
        [System.Management.Automation.CompletionResult]::new('--log-level', '--log-level', 'ParameterValue', 'Log level')
    )

    # Main commands
    $mainCommands = @(
        [System.Management.Automation.CompletionResult]::new('analyze', 'analyze', 'ParameterValue', 'Audio analysis and feature extraction')
        [System.Management.Automation.CompletionResult]::new('batch', 'batch', 'ParameterValue', 'Batch processing')
        [System.Management.Automation.CompletionResult]::new('library', 'library', 'ParameterValue', 'Library management')
        [System.Management.Automation.CompletionResult]::new('collection', 'collection', 'ParameterValue', 'Collection management')
        [System.Management.Automation.CompletionResult]::new('ai', 'ai', 'ParameterValue', 'AI-powered features')
        [System.Management.Automation.CompletionResult]::new('audio', 'audio', 'ParameterValue', 'Audio processing')
        [System.Management.Automation.CompletionResult]::new('meta', 'meta', 'ParameterValue', 'Metadata operations')
        [System.Management.Automation.CompletionResult]::new('stems', 'stems', 'ParameterValue', 'Stem separation')
        [System.Management.Automation.CompletionResult]::new('viz', 'viz', 'ParameterValue', 'Visualization')
        [System.Management.Automation.CompletionResult]::new('report', 'report', 'ParameterValue', 'Reporting')
        [System.Management.Automation.CompletionResult]::new('health', 'health', 'ParameterValue', 'Health checks')
        [System.Management.Automation.CompletionResult]::new('debug', 'debug', 'ParameterValue', 'Debug tools')
        [System.Management.Automation.CompletionResult]::new('config', 'config', 'ParameterValue', 'Configuration')
        [System.Management.Automation.CompletionResult]::new('cache', 'cache', 'ParameterValue', 'Cache management')
        [System.Management.Automation.CompletionResult]::new('help', 'help', 'ParameterValue', 'Show help')
    )

    # Analyze subcommands
    $analyzeCommands = @(
        [System.Management.Automation.CompletionResult]::new('analyze:full', 'full', 'ParameterValue', 'Comprehensive DETAILED analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:standard', 'standard', 'ParameterValue', 'Standard analysis (recommended)')
        [System.Management.Automation.CompletionResult]::new('analyze:basic', 'basic', 'ParameterValue', 'Quick basic analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:professional', 'professional', 'ParameterValue', 'Professional-grade analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:quick', 'quick', 'ParameterValue', 'Ultra-fast analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:bpm', 'bpm', 'ParameterValue', 'BPM detection only')
        [System.Management.Automation.CompletionResult]::new('analyze:key', 'key', 'ParameterValue', 'Key detection only')
        [System.Management.Automation.CompletionResult]::new('analyze:mood', 'mood', 'ParameterValue', 'Mood analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:genre', 'genre', 'ParameterValue', 'Genre classification')
        [System.Management.Automation.CompletionResult]::new('analyze:instrument', 'instrument', 'ParameterValue', 'Instrument recognition')
        [System.Management.Automation.CompletionResult]::new('analyze:vocal', 'vocal', 'ParameterValue', 'Vocal detection')
        [System.Management.Automation.CompletionResult]::new('analyze:quality', 'quality', 'ParameterValue', 'Quality scoring')
        [System.Management.Automation.CompletionResult]::new('analyze:energy', 'energy', 'ParameterValue', 'Energy level detection')
        [System.Management.Automation.CompletionResult]::new('analyze:spectral', 'spectral', 'ParameterValue', 'Spectral analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:harmonic', 'harmonic', 'ParameterValue', 'Harmonic/percussive separation')
        [System.Management.Automation.CompletionResult]::new('analyze:percussive', 'percussive', 'ParameterValue', 'Percussive analysis')
        [System.Management.Automation.CompletionResult]::new('analyze:mfcc', 'mfcc', 'ParameterValue', 'MFCC extraction')
        [System.Management.Automation.CompletionResult]::new('analyze:chroma', 'chroma', 'ParameterValue', 'Chroma features')
        [System.Management.Automation.CompletionResult]::new('analyze:onset', 'onset', 'ParameterValue', 'Onset detection')
        [System.Management.Automation.CompletionResult]::new('analyze:beats', 'beats', 'ParameterValue', 'Beat detection')
        [System.Management.Automation.CompletionResult]::new('analyze:segments', 'segments', 'ParameterValue', 'Segment detection')
    )

    # Library subcommands
    $libraryCommands = @(
        [System.Management.Automation.CompletionResult]::new('library:scan', 'scan', 'ParameterValue', 'Scan and index directory')
        [System.Management.Automation.CompletionResult]::new('library:organize', 'organize', 'ParameterValue', 'Auto-organize by metadata')
        [System.Management.Automation.CompletionResult]::new('library:import', 'import', 'ParameterValue', 'Import with metadata')
        [System.Management.Automation.CompletionResult]::new('library:export', 'export', 'ParameterValue', 'Export with metadata')
        [System.Management.Automation.CompletionResult]::new('library:sync', 'sync', 'ParameterValue', 'Cloud sync')
        [System.Management.Automation.CompletionResult]::new('library:search', 'search', 'ParameterValue', 'Full-text search')
        [System.Management.Automation.CompletionResult]::new('library:find-similar', 'find-similar', 'ParameterValue', 'Find similar samples')
        [System.Management.Automation.CompletionResult]::new('library:dedupe', 'dedupe', 'ParameterValue', 'Find duplicates')
        [System.Management.Automation.CompletionResult]::new('library:cleanup', 'cleanup', 'ParameterValue', 'Remove broken files')
        [System.Management.Automation.CompletionResult]::new('library:verify', 'verify', 'ParameterValue', 'Verify file integrity')
        [System.Management.Automation.CompletionResult]::new('library:rebuild-index', 'rebuild-index', 'ParameterValue', 'Rebuild library index')
    )

    # AI subcommands
    $aiCommands = @(
        [System.Management.Automation.CompletionResult]::new('ai:analyze', 'analyze', 'ParameterValue', 'AI-powered analysis')
        [System.Management.Automation.CompletionResult]::new('ai:classify', 'classify', 'ParameterValue', 'AI classification')
        [System.Management.Automation.CompletionResult]::new('ai:tag', 'tag', 'ParameterValue', 'AI auto-tagging')
        [System.Management.Automation.CompletionResult]::new('ai:suggest', 'suggest', 'ParameterValue', 'Similar sample suggestions')
        [System.Management.Automation.CompletionResult]::new('ai:coach', 'coach', 'ParameterValue', 'Production coaching')
        [System.Management.Automation.CompletionResult]::new('ai:presets', 'presets', 'ParameterValue', 'Generate EQ/compressor presets')
        [System.Management.Automation.CompletionResult]::new('ai:provider', 'provider', 'ParameterValue', 'Set AI provider')
        [System.Management.Automation.CompletionResult]::new('ai:key', 'key', 'ParameterValue', 'Configure API key')
        [System.Management.Automation.CompletionResult]::new('ai:model', 'model', 'ParameterValue', 'Set AI model')
        [System.Management.Automation.CompletionResult]::new('ai:test', 'test', 'ParameterValue', 'Test AI connection')
    )

    # Batch subcommands
    $batchCommands = @(
        [System.Management.Automation.CompletionResult]::new('batch:analyze', 'analyze', 'ParameterValue', 'Batch analysis')
        [System.Management.Automation.CompletionResult]::new('batch:classify', 'classify', 'ParameterValue', 'Batch classification')
        [System.Management.Automation.CompletionResult]::new('batch:tag', 'tag', 'ParameterValue', 'Batch tagging')
        [System.Management.Automation.CompletionResult]::new('batch:export', 'export', 'ParameterValue', 'Batch export')
    )

    # Collection subcommands
    $collectionCommands = @(
        [System.Management.Automation.CompletionResult]::new('collection:create', 'create', 'ParameterValue', 'Create collection')
        [System.Management.Automation.CompletionResult]::new('collection:add', 'add', 'ParameterValue', 'Add to collection')
        [System.Management.Automation.CompletionResult]::new('collection:list', 'list', 'ParameterValue', 'List collections')
        [System.Management.Automation.CompletionResult]::new('collection:export', 'export', 'ParameterValue', 'Export collection')
    )

    # Meta subcommands
    $metaCommands = @(
        [System.Management.Automation.CompletionResult]::new('meta:show', 'show', 'ParameterValue', 'Display metadata')
        [System.Management.Automation.CompletionResult]::new('meta:edit', 'edit', 'ParameterValue', 'Edit metadata')
        [System.Management.Automation.CompletionResult]::new('meta:copy', 'copy', 'ParameterValue', 'Copy metadata')
        [System.Management.Automation.CompletionResult]::new('meta:clear', 'clear', 'ParameterValue', 'Clear metadata')
        [System.Management.Automation.CompletionResult]::new('meta:export', 'export', 'ParameterValue', 'Export to JSON/YAML')
        [System.Management.Automation.CompletionResult]::new('meta:import', 'import', 'ParameterValue', 'Import from JSON/YAML')
    )

    # Audio subcommands
    $audioCommands = @(
        [System.Management.Automation.CompletionResult]::new('audio:convert:wav', 'convert:wav', 'ParameterValue', 'Convert to WAV')
        [System.Management.Automation.CompletionResult]::new('audio:convert:mp3', 'convert:mp3', 'ParameterValue', 'Convert to MP3')
        [System.Management.Automation.CompletionResult]::new('audio:convert:flac', 'convert:flac', 'ParameterValue', 'Convert to FLAC')
        [System.Management.Automation.CompletionResult]::new('audio:convert:ogg', 'convert:ogg', 'ParameterValue', 'Convert to OGG')
        [System.Management.Automation.CompletionResult]::new('audio:normalize', 'normalize', 'ParameterValue', 'Normalize audio')
        [System.Management.Automation.CompletionResult]::new('audio:trim', 'trim', 'ParameterValue', 'Trim silence')
        [System.Management.Automation.CompletionResult]::new('audio:fade', 'fade', 'ParameterValue', 'Add fade in/out')
        [System.Management.Automation.CompletionResult]::new('audio:split', 'split', 'ParameterValue', 'Split audio')
        [System.Management.Automation.CompletionResult]::new('audio:join', 'join', 'ParameterValue', 'Join audio files')
    )

    # Stems subcommands
    $stemsCommands = @(
        [System.Management.Automation.CompletionResult]::new('stems:separate', 'separate', 'ParameterValue', 'Separate stems')
        [System.Management.Automation.CompletionResult]::new('stems:vocals', 'vocals', 'ParameterValue', 'Extract vocals only')
        [System.Management.Automation.CompletionResult]::new('stems:drums', 'drums', 'ParameterValue', 'Extract drums only')
        [System.Management.Automation.CompletionResult]::new('stems:bass', 'bass', 'ParameterValue', 'Extract bass only')
    )

    # Viz subcommands
    $vizCommands = @(
        [System.Management.Automation.CompletionResult]::new('viz:waveform', 'waveform', 'ParameterValue', 'Generate waveform image')
        [System.Management.Automation.CompletionResult]::new('viz:spectrogram', 'spectrogram', 'ParameterValue', 'Generate spectrogram')
        [System.Management.Automation.CompletionResult]::new('viz:chromagram', 'chromagram', 'ParameterValue', 'Generate chromagram')
        [System.Management.Automation.CompletionResult]::new('viz:mfcc', 'mfcc', 'ParameterValue', 'MFCC visualization')
    )

    # Report subcommands
    $reportCommands = @(
        [System.Management.Automation.CompletionResult]::new('report:library', 'library', 'ParameterValue', 'Library statistics')
        [System.Management.Automation.CompletionResult]::new('report:analysis', 'analysis', 'ParameterValue', 'Analysis report')
        [System.Management.Automation.CompletionResult]::new('report:batch', 'batch', 'ParameterValue', 'Batch report')
    )

    # Health subcommands
    $healthCommands = @(
        [System.Management.Automation.CompletionResult]::new('health:check', 'check', 'ParameterValue', 'Comprehensive health check')
        [System.Management.Automation.CompletionResult]::new('health:status', 'status', 'ParameterValue', 'Current system status')
        [System.Management.Automation.CompletionResult]::new('health:logs', 'logs', 'ParameterValue', 'Display recent logs')
        [System.Management.Automation.CompletionResult]::new('health:cache', 'cache', 'ParameterValue', 'Cache statistics')
        [System.Management.Automation.CompletionResult]::new('health:disk', 'disk', 'ParameterValue', 'Disk space information')
    )

    # Debug subcommands
    $debugCommands = @(
        [System.Management.Automation.CompletionResult]::new('debug:info', 'info', 'ParameterValue', 'Environment information')
        [System.Management.Automation.CompletionResult]::new('debug:diagnose', 'diagnose', 'ParameterValue', 'Diagnose audio file')
        [System.Management.Automation.CompletionResult]::new('debug:config', 'config', 'ParameterValue', 'Show configuration')
        [System.Management.Automation.CompletionResult]::new('debug:test', 'test', 'ParameterValue', 'Run diagnostic tests')
        [System.Management.Automation.CompletionResult]::new('debug:trace', 'trace', 'ParameterValue', 'Enable debug tracing')
    )

    # Config subcommands
    $configCommands = @(
        [System.Management.Automation.CompletionResult]::new('config:set', 'set', 'ParameterValue', 'Set configuration')
        [System.Management.Automation.CompletionResult]::new('config:get', 'get', 'ParameterValue', 'Get configuration')
        [System.Management.Automation.CompletionResult]::new('config:reset', 'reset', 'ParameterValue', 'Reset configuration')
        [System.Management.Automation.CompletionResult]::new('config:show', 'show', 'ParameterValue', 'Show all configuration')
    )

    # Cache subcommands
    $cacheCommands = @(
        [System.Management.Automation.CompletionResult]::new('cache:clear', 'clear', 'ParameterValue', 'Clear cache')
        [System.Management.Automation.CompletionResult]::new('cache:stats', 'stats', 'ParameterValue', 'Cache statistics')
        [System.Management.Automation.CompletionResult]::new('cache:optimize', 'optimize', 'ParameterValue', 'Optimize cache')
    )

    # Determine what completions to show based on current token
    $lastWord = if ($tokens.Count -gt $cmdIndex + 1) { $tokens[$cmdIndex + 1] } else { '' }

    if ($wordToComplete.StartsWith('-')) {
        return $globalOptions | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }

    if ($lastWord -eq '') {
        return $mainCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }

    if ($lastWord -eq 'analyze' -or $lastWord.StartsWith('analyze:')) {
        return $analyzeCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'library' -or $lastWord.StartsWith('library:')) {
        return $libraryCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'ai' -or $lastWord.StartsWith('ai:')) {
        return $aiCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'batch' -or $lastWord.StartsWith('batch:')) {
        return $batchCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'collection' -or $lastWord.StartsWith('collection:')) {
        return $collectionCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'meta' -or $lastWord.StartsWith('meta:')) {
        return $metaCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'audio' -or $lastWord.StartsWith('audio:')) {
        return $audioCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'stems' -or $lastWord.StartsWith('stems:')) {
        return $stemsCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'viz' -or $lastWord.StartsWith('viz:')) {
        return $vizCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'report' -or $lastWord.StartsWith('report:')) {
        return $reportCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'health' -or $lastWord.StartsWith('health:')) {
        return $healthCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'debug' -or $lastWord.StartsWith('debug:')) {
        return $debugCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'config' -or $lastWord.StartsWith('config:')) {
        return $configCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }
    elseif ($lastWord -eq 'cache' -or $lastWord.StartsWith('cache:')) {
        return $cacheCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }

    return $mainCommands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
}
