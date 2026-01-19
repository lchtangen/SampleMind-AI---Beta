#!/usr/bin/env bash

# SampleMind AI - Bash Completion Script
#
# Installation:
#   1. Copy this file to /usr/share/bash-completion.d/samplemind
#      sudo cp samplemind.bash /usr/share/bash-completion.d/samplemind
#   2. Or add to ~/.bashrc:
#      source /path/to/samplemind.bash
#   3. Restart bash or run: source ~/.bashrc
#
# Usage:
#   samplemind [TAB][TAB]         - Show all commands
#   samplemind analyze:[TAB][TAB]  - Show analyze subcommands
#   samplemind --[TAB][TAB]        - Show global options

_samplemind_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # All available commands (auto-generated from CLI)
    local commands="
        analyze analyze:full analyze:standard analyze:basic analyze:professional analyze:quick
        analyze:bpm analyze:key analyze:mood analyze:genre analyze:instrument analyze:vocal
        analyze:quality analyze:energy analyze:spectral analyze:harmonic analyze:percussive
        analyze:mfcc analyze:chroma analyze:onset analyze:beats analyze:segments
        batch:analyze batch:classify batch:tag batch:export
        library:scan library:organize library:import library:export library:sync
        library:search library:filter:bpm library:filter:key library:filter:genre library:filter:tag
        library:find-similar library:dedupe library:cleanup library:verify library:rebuild-index
        collection:create collection:add collection:list collection:export collection:remove
        ai:analyze ai:classify ai:tag ai:suggest ai:coach ai:presets
        ai:provider ai:key ai:model ai:test ai:offline
        meta:show meta:edit meta:copy meta:clear meta:export meta:import
        meta:batch:tag meta:batch:fix meta:batch:sync meta:recover meta:snapshot meta:restore
        audio:convert:wav audio:convert:mp3 audio:convert:flac audio:convert:ogg
        audio:normalize audio:trim audio:fade audio:split audio:join
        stems:separate stems:vocals stems:drums stems:bass stems:other
        viz:waveform viz:spectrogram viz:chromagram viz:mfcc viz:export
        report:library report:analysis report:batch report:export
        health:check health:status health:logs health:cache health:disk
        debug:info debug:diagnose debug:config debug:test debug:trace
        config:set config:get config:reset config:show
        cache:clear cache:stats cache:optimize
        help version
    "

    # Global options
    local global_opts="--help -h --version -v --verbose --quiet --config --log-level"

    # File/directory arguments for commands that need them
    case "${COMP_WORDS[1]}" in
        analyze*|audio:*|stems:*|viz:*)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "--output --format --profile --verbose" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            return 0
            ;;
        library:scan|library:organize|library:import|library:export|batch:*)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "--output --format --recursive --filter" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            return 0
            ;;
        library:search|library:filter:*)
            if [[ "${cur}" == -* ]]; then
                case "${COMP_WORDS[1]}" in
                    library:filter:bpm)
                        COMPREPLY=( $(compgen -W "--min --max --output" -- ${cur}) )
                        ;;
                    library:filter:key)
                        COMPREPLY=( $(compgen -W "--key --mode --output" -- ${cur}) )
                        ;;
                    library:filter:genre)
                        COMPREPLY=( $(compgen -W "--genre --confidence --output" -- ${cur}) )
                        ;;
                    library:filter:tag)
                        COMPREPLY=( $(compgen -W "--tag --output" -- ${cur}) )
                        ;;
                esac
            fi
            return 0
            ;;
        ai:provider)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "--provider" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "gemini openai ollama" -- ${cur}) )
            fi
            return 0
            ;;
        ai:key)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "--provider --key" -- ${cur}) )
            fi
            return 0
            ;;
        debug:diagnose)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "--verbose" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            return 0
            ;;
        config:set|config:get)
            if [[ "${COMP_CWORD}" -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "cache_size log_level ai_provider output_format" -- ${cur}) )
            fi
            return 0
            ;;
    esac

    # Subcommand completion
    if [[ "${cur}" == analyze:* ]]; then
        local analyze_cmds="full standard basic professional quick bpm key mood genre instrument vocal quality energy spectral harmonic percussive mfcc chroma onset beats segments"
        COMPREPLY=( $(compgen -W "$(echo $analyze_cmds | sed 's/^/analyze:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == library:* ]]; then
        local library_cmds="scan organize import export sync search filter:bpm filter:key filter:genre filter:tag find-similar dedupe cleanup verify rebuild-index"
        COMPREPLY=( $(compgen -W "$(echo $library_cmds | sed 's/^/library:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == ai:* ]]; then
        local ai_cmds="analyze classify tag suggest coach presets provider key model test offline"
        COMPREPLY=( $(compgen -W "$(echo $ai_cmds | sed 's/^/ai:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == meta:* ]]; then
        local meta_cmds="show edit copy clear export import batch:tag batch:fix batch:sync recover snapshot restore"
        COMPREPLY=( $(compgen -W "$(echo $meta_cmds | sed 's/^/meta:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == audio:* ]]; then
        local audio_cmds="convert:wav convert:mp3 convert:flac convert:ogg normalize trim fade split join"
        COMPREPLY=( $(compgen -W "$(echo $audio_cmds | sed 's/^/audio:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == stems:* ]]; then
        local stems_cmds="separate vocals drums bass other"
        COMPREPLY=( $(compgen -W "$(echo $stems_cmds | sed 's/^/stems:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == viz:* ]]; then
        local viz_cmds="waveform spectrogram chromagram mfcc export"
        COMPREPLY=( $(compgen -W "$(echo $viz_cmds | sed 's/^/viz:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == report:* ]]; then
        local report_cmds="library analysis batch export"
        COMPREPLY=( $(compgen -W "$(echo $report_cmds | sed 's/^/report:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == health:* ]]; then
        local health_cmds="check status logs cache disk"
        COMPREPLY=( $(compgen -W "$(echo $health_cmds | sed 's/^/health:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == debug:* ]]; then
        local debug_cmds="info diagnose config test trace"
        COMPREPLY=( $(compgen -W "$(echo $debug_cmds | sed 's/^/debug:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == config:* ]]; then
        local config_cmds="set get reset show"
        COMPREPLY=( $(compgen -W "$(echo $config_cmds | sed 's/^/config:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == cache:* ]]; then
        local cache_cmds="clear stats optimize"
        COMPREPLY=( $(compgen -W "$(echo $cache_cmds | sed 's/^/cache:/')" -- ${cur}) )
        return 0
    elif [[ "${cur}" == batch:* ]]; then
        local batch_cmds="analyze classify tag export"
        COMPREPLY=( $(compgen -W "$(echo $batch_cmds | sed 's/^/batch:/')" -- ${cur}) )
        return 0
    fi

    # Main command completion
    if [[ "${cur}" == -* ]]; then
        COMPREPLY=( $(compgen -W "${global_opts}" -- ${cur}) )
    else
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
    fi

    return 0
}

# Register the completion function
complete -o bashdefault -o default -o nospace -F _samplemind_completions samplemind
complete -o bashdefault -o default -o nospace -F _samplemind_completions smai
