#!/usr/bin/env fish

# SampleMind AI - Fish Shell Completion Script
#
# Installation:
#   1. Copy this file to ~/.config/fish/completions/samplemind.fish
#      mkdir -p ~/.config/fish/completions
#      cp samplemind.fish ~/.config/fish/completions/
#   2. Restart fish or run: exec fish
#
# Usage:
#   samplemind [TAB]         - Show all commands
#   samplemind analyze [TAB]  - Show analyze subcommands
#   samplemind -[TAB]        - Show global options

# Utility function to check if command exists
function __fish_samplemind_no_subcommand_from_list
    set -l tokens (commandline -opc)
    set -e tokens[1]
    for arg in $argv
        if contains -- $arg $tokens
            return 1
        end
    end
    return 0
end

# Global options
complete -c samplemind -n '__fish_use_subcommand_from_list' -f
complete -c samplemind -s h -l help -d 'Show help message'
complete -c samplemind -s v -l version -d 'Show version'
complete -c samplemind -l verbose -d 'Verbose output'
complete -c samplemind -l quiet -d 'Quiet output'
complete -c samplemind -l config -d 'Configuration file' -r
complete -c samplemind -l log-level -d 'Log level' -xa 'DEBUG INFO WARNING ERROR CRITICAL'

# Main commands
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'analyze' -d 'Audio analysis and feature extraction'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'batch' -d 'Batch processing'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'library' -d 'Library management'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'collection' -d 'Collection management'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'ai' -d 'AI-powered features'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'audio' -d 'Audio processing'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'meta' -d 'Metadata operations'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'stems' -d 'Stem separation'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'viz' -d 'Visualization'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'report' -d 'Reporting'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'health' -d 'Health checks'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'debug' -d 'Debug tools'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'config' -d 'Configuration'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'cache' -d 'Cache management'
complete -c samplemind -n '__fish_samplemind_no_subcommand_from_list' -f -a 'help' -d 'Show help'

# Analyze subcommands
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'full' -d 'Comprehensive DETAILED analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'standard' -d 'Standard analysis (recommended)'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'basic' -d 'Quick basic analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'professional' -d 'Professional-grade analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'quick' -d 'Ultra-fast analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'bpm' -d 'BPM detection only'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'key' -d 'Key detection only'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'mood' -d 'Mood analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'genre' -d 'Genre classification'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'instrument' -d 'Instrument recognition'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'vocal' -d 'Vocal detection'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'quality' -d 'Quality scoring'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'energy' -d 'Energy level detection'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'spectral' -d 'Spectral analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'harmonic' -d 'Harmonic/percussive separation'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'percussive' -d 'Percussive analysis'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'mfcc' -d 'MFCC extraction'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'chroma' -d 'Chroma features'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'onset' -d 'Onset detection'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'beats' -d 'Beat detection'
complete -c samplemind -n '__fish_seen_subcommand_from analyze' -f -a 'segments' -d 'Segment detection'

# Library subcommands
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'scan' -d 'Scan and index directory'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'organize' -d 'Auto-organize by metadata'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'import' -d 'Import with metadata'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'export' -d 'Export with metadata'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'sync' -d 'Cloud sync'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'search' -d 'Full-text search'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'find-similar' -d 'Find similar samples'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'dedupe' -d 'Find duplicates'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'cleanup' -d 'Remove broken files'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'verify' -d 'Verify file integrity'
complete -c samplemind -n '__fish_seen_subcommand_from library' -f -a 'rebuild-index' -d 'Rebuild library index'

# AI subcommands
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'analyze' -d 'AI-powered analysis'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'classify' -d 'AI classification'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'tag' -d 'AI auto-tagging'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'suggest' -d 'Similar sample suggestions'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'coach' -d 'Production coaching'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'presets' -d 'Generate EQ/compressor presets'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'provider' -d 'Set AI provider'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'key' -d 'Configure API key'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'model' -d 'Set AI model'
complete -c samplemind -n '__fish_seen_subcommand_from ai' -f -a 'test' -d 'Test AI connection'

# Batch subcommands
complete -c samplemind -n '__fish_seen_subcommand_from batch' -f -a 'analyze' -d 'Batch analysis'
complete -c samplemind -n '__fish_seen_subcommand_from batch' -f -a 'classify' -d 'Batch classification'
complete -c samplemind -n '__fish_seen_subcommand_from batch' -f -a 'tag' -d 'Batch tagging'
complete -c samplemind -n '__fish_seen_subcommand_from batch' -f -a 'export' -d 'Batch export'

# Collection subcommands
complete -c samplemind -n '__fish_seen_subcommand_from collection' -f -a 'create' -d 'Create collection'
complete -c samplemind -n '__fish_seen_subcommand_from collection' -f -a 'add' -d 'Add to collection'
complete -c samplemind -n '__fish_seen_subcommand_from collection' -f -a 'list' -d 'List collections'
complete -c samplemind -n '__fish_seen_subcommand_from collection' -f -a 'export' -d 'Export collection'

# Audio subcommands
complete -c samplemind -n '__fish_seen_subcommand_from audio' -f -a 'normalize' -d 'Normalize audio'
complete -c samplemind -n '__fish_seen_subcommand_from audio' -f -a 'trim' -d 'Trim silence'
complete -c samplemind -n '__fish_seen_subcommand_from audio' -f -a 'fade' -d 'Add fade in/out'
complete -c samplemind -n '__fish_seen_subcommand_from audio' -f -a 'split' -d 'Split audio'
complete -c samplemind -n '__fish_seen_subcommand_from audio' -f -a 'join' -d 'Join audio files'

# Stems subcommands
complete -c samplemind -n '__fish_seen_subcommand_from stems' -f -a 'separate' -d 'Separate stems'
complete -c samplemind -n '__fish_seen_subcommand_from stems' -f -a 'vocals' -d 'Extract vocals only'
complete -c samplemind -n '__fish_seen_subcommand_from stems' -f -a 'drums' -d 'Extract drums only'
complete -c samplemind -n '__fish_seen_subcommand_from stems' -f -a 'bass' -d 'Extract bass only'

# Visualization subcommands
complete -c samplemind -n '__fish_seen_subcommand_from viz' -f -a 'waveform' -d 'Generate waveform image'
complete -c samplemind -n '__fish_seen_subcommand_from viz' -f -a 'spectrogram' -d 'Generate spectrogram'
complete -c samplemind -n '__fish_seen_subcommand_from viz' -f -a 'chromagram' -d 'Generate chromagram'
complete -c samplemind -n '__fish_seen_subcommand_from viz' -f -a 'mfcc' -d 'MFCC visualization'

# Report subcommands
complete -c samplemind -n '__fish_seen_subcommand_from report' -f -a 'library' -d 'Library statistics'
complete -c samplemind -n '__fish_seen_subcommand_from report' -f -a 'analysis' -d 'Analysis report'
complete -c samplemind -n '__fish_seen_subcommand_from report' -f -a 'batch' -d 'Batch report'

# Health subcommands
complete -c samplemind -n '__fish_seen_subcommand_from health' -f -a 'check' -d 'Comprehensive health check'
complete -c samplemind -n '__fish_seen_subcommand_from health' -f -a 'status' -d 'Current system status'
complete -c samplemind -n '__fish_seen_subcommand_from health' -f -a 'logs' -d 'Display recent logs'
complete -c samplemind -n '__fish_seen_subcommand_from health' -f -a 'cache' -d 'Cache statistics'
complete -c samplemind -n '__fish_seen_subcommand_from health' -f -a 'disk' -d 'Disk space information'

# Debug subcommands
complete -c samplemind -n '__fish_seen_subcommand_from debug' -f -a 'info' -d 'Environment information'
complete -c samplemind -n '__fish_seen_subcommand_from debug' -f -a 'diagnose' -d 'Diagnose audio file'
complete -c samplemind -n '__fish_seen_subcommand_from debug' -f -a 'config' -d 'Show configuration'
complete -c samplemind -n '__fish_seen_subcommand_from debug' -f -a 'test' -d 'Run diagnostic tests'
complete -c samplemind -n '__fish_seen_subcommand_from debug' -f -a 'trace' -d 'Enable debug tracing'

# Config subcommands
complete -c samplemind -n '__fish_seen_subcommand_from config' -f -a 'set' -d 'Set configuration'
complete -c samplemind -n '__fish_seen_subcommand_from config' -f -a 'get' -d 'Get configuration'
complete -c samplemind -n '__fish_seen_subcommand_from config' -f -a 'reset' -d 'Reset configuration'
complete -c samplemind -n '__fish_seen_subcommand_from config' -f -a 'show' -d 'Show all configuration'

# Cache subcommands
complete -c samplemind -n '__fish_seen_subcommand_from cache' -f -a 'clear' -d 'Clear cache'
complete -c samplemind -n '__fish_seen_subcommand_from cache' -f -a 'stats' -d 'Cache statistics'
complete -c samplemind -n '__fish_seen_subcommand_from cache' -f -a 'optimize' -d 'Optimize cache'

# Meta subcommands
complete -c samplemind -n '__fish_seen_subcommand_from meta' -f -a 'show' -d 'Display metadata'
complete -c samplemind -n '__fish_seen_subcommand_from meta' -f -a 'edit' -d 'Edit metadata'
complete -c samplemind -n '__fish_seen_subcommand_from meta' -f -a 'copy' -d 'Copy metadata'
complete -c samplemind -n '__fish_seen_subcommand_from meta' -f -a 'clear' -d 'Clear metadata'
