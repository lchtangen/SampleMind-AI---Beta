# SampleMind AI - Code Quality Report

**Generated:** 1770105079.2611232

**Total Issues:** 102

## Issues by Severity

- **Critical:** 0
- **High:** 0
- **Medium:** 102
- **Low:** 0

## Detailed Issues

### config.py:301
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'validate_secret_keys' missing type hints for: parameter 'info'
- **Suggestion:** Add type hints for all parameters and return values

### bridge.py:104
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'run_server' missing type hints for: return type, parameter 'host', parameter 'port'
- **Suggestion:** Add type hints for all parameters and return values

### generation_manager.py:352
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_suggest_transforms' missing type hints for: parameter 'features'
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:139
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'before_cursor_execute' missing type hints for: return type, parameter 'conn', parameter 'cursor', parameter 'statement', parameter 'parameters', parameter 'context', parameter 'executemany'
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:144
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'after_cursor_execute' missing type hints for: return type, parameter 'conn', parameter 'cursor', parameter 'statement', parameter 'parameters', parameter 'context', parameter 'executemany'
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:174
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'receive_connect' missing type hints for: return type, parameter 'dbapi_conn', parameter 'connection_record'
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:187
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'receive_checkout' missing type hints for: return type, parameter 'dbapi_conn', parameter 'connection_record', parameter 'connection_proxy'
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:192
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'receive_checkin' missing type hints for: return type, parameter 'dbapi_conn', parameter 'connection_record'
- **Suggestion:** Add type hints for all parameters and return values

### distributed_processor.py:276
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'time_feature_extraction' missing type hints for: return type, parameter 'feature_name', parameter 'extract_func'
- **Suggestion:** Add type hints for all parameters and return values

### layering_analyzer.py:266
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_onsets' missing type hints for: return type, parameter 'audio'
- **Suggestion:** Add type hints for all parameters and return values

### audio_effects.py:45
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### audio_effects.py:87
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### audio_effects.py:91
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'add_effect' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### audio_effects.py:95
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'clear' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### usage_patterns.py:306
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init_tracker' missing type hints for: parameter 'redis_cache'
- **Suggestion:** Add type hints for all parameters and return values

### usage_patterns.py:100
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__init__' missing type hints for: parameter 'redis_cache'
- **Suggestion:** Add type hints for all parameters and return values

### cache_warmer.py:356
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init_warmer' missing type hints for: parameter 'audio_engine', parameter 'cache', parameter 'markov_predictor'
- **Suggestion:** Add type hints for all parameters and return values

### cache_warmer.py:79
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__init__' missing type hints for: parameter 'audio_engine', parameter 'cache', parameter 'markov_predictor'
- **Suggestion:** Add type hints for all parameters and return values

### markov_predictor.py:336
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init_predictor' missing type hints for: parameter 'usage_tracker'
- **Suggestion:** Add type hints for all parameters and return values

### markov_predictor.py:72
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__init__' missing type hints for: parameter 'usage_tracker'
- **Suggestion:** Add type hints for all parameters and return values

### markov_predictor.py:93
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'set_usage_tracker' missing type hints for: parameter 'tracker'
- **Suggestion:** Add type hints for all parameters and return values

### cache_manager.py:381
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init_manager' missing type hints for: parameter 'redis_cache'
- **Suggestion:** Add type hints for all parameters and return values

### cache_manager.py:75
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__init__' missing type hints for: parameter 'redis_cache'
- **Suggestion:** Add type hints for all parameters and return values

### sync_manager.py:134
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__init__' missing type hints for: parameter 'mongodb_client', parameter 'redis_client', parameter 's3_client'
- **Suggestion:** Add type hints for all parameters and return values

### ableton_integration.py:54
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'connect' missing type hints for: parameter 'song'
- **Suggestion:** Add type hints for all parameters and return values

### ableton_integration.py:100
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_track_selected' missing type hints for: parameter 'track'
- **Suggestion:** Add type hints for all parameters and return values

### ableton_integration.py:126
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_clip_metadata' missing type hints for: parameter 'clip'
- **Suggestion:** Add type hints for all parameters and return values

### ableton_integration.py:141
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_clip_file_path' missing type hints for: parameter 'clip'
- **Suggestion:** Add type hints for all parameters and return values

### classifier.py:297
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_generate_tags' missing type hints for: parameter 'instrument', parameter 'genre', parameter 'mood', parameter 'quality', parameter 'tempo'
- **Suggestion:** Add type hints for all parameters and return values

### auto_tagger.py:96
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_generate_tags_from_classification' missing type hints for: parameter 'classification'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1698
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_analysis_results' missing type hints for: parameter 'ai_result', parameter 'loaded_audio', parameter 'features'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1768
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_batch_summary' missing type hints for: parameter 'results', parameter 'processing_time'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1808
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_directory_info' missing type hints for: parameter 'dir_info'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1834
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_save_analysis' missing type hints for: parameter 'ai_result', parameter 'loaded_audio', parameter 'features', parameter 'output_file'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1755
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_rating' missing type hints for: return type, parameter 'score'
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:93
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'interactive' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:116
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'menu' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:122
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'status' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:165
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'version' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:197
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'register_command_groups' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:231
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'create_progress_spinner' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:246
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'handle_command_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:290
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'help' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:370
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'list_commands' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:392
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'with_error_recovery' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:204
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'pick_file' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:196
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'set_theme' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:238
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'register_custom_shortcut' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:761
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_theme_selector' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:792
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_shortcuts_help' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:806
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_about' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:858
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'display_breadcrumb' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### modern_menu.py:863
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'display_status_bar' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### dependencies.py:9
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'set_app_state' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### dependencies.py:19
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_audio_engine' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### dependencies.py:24
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_ai_manager' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### daw.py:56
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'daw_status' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### theory.py:33
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_analyzer' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### utils.py:247
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'with_progress' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### metadata.py:57
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'meta_show_tags' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### metadata.py:72
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'meta_show_analysis' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### metadata.py:90
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'meta_show_custom' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### metadata.py:462
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'meta_snapshot' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### metadata.py:477
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'meta_snapshot_list' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### recent.py:248
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'stats_command' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### analyze.py:693
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'list' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### similarity.py:32
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_similarity_db' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### similarity.py:251
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'similar_stats' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### similarity.py:160
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'progress_callback' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:332
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_provider' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:350
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_provider_list' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:390
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_model' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:499
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_config' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:632
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_config_reset' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai.py:655
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'ai_features' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### mastering.py:312
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_targets' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:66
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_coach_widget.py:196
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### main_screen.py:52
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### results_screen.py:98
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### results_screen.py:367
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### batch_screen.py:94
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### batch_screen.py:172
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### batch_screen.py:501
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_key' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### favorites_screen.py:69
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### classification_screen.py:96
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### classification_screen.py:177
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### classification_screen.py:388
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_result_row' missing type hints for: parameter 'classification'
- **Suggestion:** Add type hints for all parameters and return values

### analyze_screen.py:96
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### analyze_screen.py:426
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_results' missing type hints for: parameter 'features'
- **Suggestion:** Add type hints for all parameters and return values

### analyze_screen.py:443
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_key' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### tagging_screen.py:97
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### tagging_screen.py:192
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### search_screen.py:91
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### search_screen.py:159
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### settings_screen.py:88
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### comparison_screen.py:268
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'compose' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### comparison_screen.py:394
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_button_pressed' missing type hints for: parameter 'event'
- **Suggestion:** Add type hints for all parameters and return values

### auth.py:20
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'username_alphanumeric' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### auth.py:28
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'password_strength' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### auth.py:67
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'password_strength' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### auth.py:103
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'username_alphanumeric' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

