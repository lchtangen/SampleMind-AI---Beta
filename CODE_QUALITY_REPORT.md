# SampleMind AI - Code Quality Report

**Generated:** 1770105079.2611232

**Total Issues:** 232

## Issues by Severity

- **Critical:** 0
- **High:** 0
- **Medium:** 232
- **Low:** 0

## Detailed Issues

### __init__.py:38
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__getattr__' missing type hints for: return type, parameter 'name'
- **Suggestion:** Add type hints for all parameters and return values

### config.py:301
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'validate_secret_keys' missing type hints for: parameter 'info'
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:253
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_tag' missing type hints for: parameter 'audio_file'
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:265
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_year' missing type hints for: parameter 'audio_file'
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:283
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_track_number' missing type hints for: parameter 'audio_file'
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:692
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_cache_audio' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:701
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_loading_stats' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:730
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'clear_cache' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### loader.py:738
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'shutdown' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### bridge.py:104
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'run_server' missing type hints for: return type, parameter 'host', parameter 'port'
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:314
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'with_logging' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:158
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:172
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:279
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:287
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:334
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'decorator' missing type hints for: return type, parameter 'func'
- **Suggestion:** Add type hints for all parameters and return values

### log_context.py:340
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'wrapper' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:97
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'handle_errors' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:282
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:287
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:154
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_logger' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:190
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:195
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:210
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'command_start' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:215
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'command_complete' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:223
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'command_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:235
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'analysis_start' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:243
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'analysis_complete' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:255
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'analysis_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:267
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'request_start' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:275
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'request_complete' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:290
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'request_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:298
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'fallback_triggered' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:313
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'query_start' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:318
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'query_complete' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:326
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'query_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:338
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'hit' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:346
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'miss' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:351
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'store' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:356
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'evict' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### logging_config.py:115
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'json_formatter' missing type hints for: return type, parameter 'record'
- **Suggestion:** Add type hints for all parameters and return values

### storage.py:219
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_list' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### anthropic_integration.py:403
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_stats' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### anthropic_integration.py:443
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'shutdown' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:195
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_request_count' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:230
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_initialize_providers' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:244
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_initialize_from_env' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:318
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_load_from_config' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:346
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_save_config' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:554
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_convert_to_google_type' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:613
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_convert_google_result' missing type hints for: parameter 'google_result'
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:693
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_provider_stats' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:754
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'set_provider_enabled' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### ai_manager.py:761
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'set_provider_priority' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### openai_integration.py:474
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'clear_cache' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### openai_integration.py:498
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_update_usage_stats' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### generation_manager.py:114
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'neural_engine' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### generation_manager.py:126
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'stem_engine' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### generation_manager.py:352
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_suggest_transforms' missing type hints for: parameter 'features'
- **Suggestion:** Add type hints for all parameters and return values

### audio_tasks.py:390
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'cleanup_old_results' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### audio_tasks.py:23
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_success' missing type hints for: return type, parameter 'retval', parameter 'task_id', parameter 'args', parameter 'kwargs'
- **Suggestion:** Add type hints for all parameters and return values

### audio_tasks.py:27
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_failure' missing type hints for: return type, parameter 'exc', parameter 'task_id', parameter 'args', parameter 'kwargs', parameter 'einfo'
- **Suggestion:** Add type hints for all parameters and return values

### audio_tasks.py:31
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'on_retry' missing type hints for: return type, parameter 'exc', parameter 'task_id', parameter 'args', parameter 'kwargs', parameter 'einfo'
- **Suggestion:** Add type hints for all parameters and return values

### redis_cache.py:344
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'cached' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### redis_cache.py:358
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'decorator' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### permissions.py:30
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'require_permission' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### permissions.py:50
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'require_any_permission' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### permissions.py:76
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'require_all_permissions' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### permissions.py:94
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'require_role' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### permissions.py:122
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'admin_only' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### jwt_handler.py:22
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'configure_jwt' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### chroma.py:44
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init_chromadb' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### chroma.py:81
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_chroma_client' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### chroma.py:88
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_collection' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### redis_client.py:164
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'redis_cache' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### redis_client.py:173
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'decorator' missing type hints for: return type, parameter 'func'
- **Suggestion:** Add type hints for all parameters and return values

### query_optimizer.py:345
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'optimized_query' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### query_optimizer.py:354
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'decorator' missing type hints for: return type, parameter 'func'
- **Suggestion:** Add type hints for all parameters and return values

### models.py:62
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__repr__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### connection_pool.py:135
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_register_event_listeners' missing type hints for: return type
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

### mongo.py:302
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_database' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### neural_engine.py:32
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_embedding_cache' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### neural_engine.py:84
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_init_device' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### neural_engine.py:92
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_load_model' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### cloud_processor.py:101
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### cloud_processor.py:106
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### distributed_processor.py:68
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### distributed_processor.py:73
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
- **Suggestion:** Add type hints for all parameters and return values

### distributed_processor.py:276
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'time_feature_extraction' missing type hints for: return type, parameter 'feature_name', parameter 'extract_func'
- **Suggestion:** Add type hints for all parameters and return values

### input_validation.py:168
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'sanitize_query' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### input_validation.py:178
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'sanitize_filename' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### input_validation.py:188
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'validate_username' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### input_validation.py:201
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'sanitize_field' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### xss_protection.py:231
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'sanitize_html' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### xss_protection.py:246
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'sanitize_url' missing type hints for: return type, parameter 'v'
- **Suggestion:** Add type hints for all parameters and return values

### layering_analyzer.py:266
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_onsets' missing type hints for: return type, parameter 'audio'
- **Suggestion:** Add type hints for all parameters and return values

### groove_extractor.py:51
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'save' missing type hints for: return type
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

### logic_pro_integration.py:57
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### vst3_plugin.py:64
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### vst3_plugin.py:277
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'do_GET' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### vst3_plugin.py:313
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'log_message' missing type hints for: return type, parameter 'format'
- **Suggestion:** Add type hints for all parameters and return values

### vst3_plugin.py:317
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_get_html' missing type hints for: return type
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

### fl_studio_plugin.py:291
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'init' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### fl_studio_plugin.py:297
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'destroy' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### fl_studio_plugin.py:41
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### processing_chain.py:34
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'add_eq' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### processing_chain.py:67
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'add_compressor' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### processing_chain.py:97
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'add_limiter' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### processing_chain.py:118
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'add_stereo_width' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### classifier.py:297
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_generate_tags' missing type hints for: parameter 'instrument', parameter 'genre', parameter 'mood', parameter 'quality', parameter 'tempo'
- **Suggestion:** Add type hints for all parameters and return values

### classifier.py:333
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_cache_result' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### auto_tagger.py:96
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_generate_tags_from_classification' missing type hints for: parameter 'classification'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:66
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'display_banner' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:169
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'display_main_menu' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:557
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'scan_and_preview' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:588
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_system_status' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:647
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'show_session_analytics' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1107
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_mixing_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1127
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_arrangement_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1147
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_mastering_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1167
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_sound_design_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1187
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_workflow_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1595
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_fl_tips' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1615
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_fl_workflow' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1647
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_show_export_settings' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1698
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_analysis_results' missing type hints for: return type, parameter 'ai_result', parameter 'loaded_audio', parameter 'features'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1768
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_batch_summary' missing type hints for: return type, parameter 'results', parameter 'processing_time'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1808
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_display_directory_info' missing type hints for: return type, parameter 'dir_info'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1834
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '_save_analysis' missing type hints for: return type, parameter 'ai_result', parameter 'loaded_audio', parameter 'features', parameter 'output_file'
- **Suggestion:** Add type hints for all parameters and return values

### menu.py:1755
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'get_rating' missing type hints for: return type, parameter 'score'
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:72
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'main_callback' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:92
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'interactive' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:115
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'menu' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:121
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'status' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:164
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'version' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:196
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'register_command_groups' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:227
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'create_progress_spinner' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:242
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'handle_command_error' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:254
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'completion' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:286
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'help' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### typer_app.py:366
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'list_commands' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:392
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'with_error_recovery' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:487
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### error_handler.py:490
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type, parameter 'exc_type', parameter 'exc_val', parameter 'exc_tb'
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

### modern_menu.py:841
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'display_banner' missing type hints for: return type
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

### app.py:85
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'main' missing type hints for: return type
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

### utils.py:153
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__enter__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### utils.py:162
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__exit__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### utils.py:223
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'wrapper' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### utils.py:234
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'wrapper' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### utils.py:252
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'wrapper' missing type hints for: return type
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

### library_browser.py:73
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### plugin_manager.py:232
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'plugin_hook_callback' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### plugin_base.py:54
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__post_init__' missing type hints for: return type
- **Suggestion:** Add type hints for all parameters and return values

### plugin_base.py:151
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function '__call__' missing type hints for: return type
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

### websocket.py:29
- **Severity:** medium
- **Category:** type_hints
- **Message:** Function 'disconnect' missing type hints for: return type
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

