#!/usr/bin/env python3
"""
SampleMind AI v6 - Cache Warming Utility
Pre-fills Redis cache with common AI prompts to maximize cache hit rate
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from .cache import get_cached_response, cache_response, prompt_fingerprint, cache_key, get_cache_stats
from .router import Provider, TaskType, get_provider_model, get_provider_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Common prompts for music production tasks
COMMON_PROMPTS = {
    TaskType.GENRE_CLASSIFICATION: [
        {
            "messages": [
                {"role": "system", "content": "You are a music genre classification expert."},
                {"role": "user", "content": "Classify this track: EDM with heavy bass, 128 BPM, synth leads"}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        },
        {
            "messages": [
                {"role": "system", "content": "You are a music genre classification expert."},
                {"role": "user", "content": "Classify this track: Hip-hop beat, 85 BPM, trap drums, 808 bass"}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        },
        {
            "messages": [
                {"role": "system", "content": "You are a music genre classification expert."},
                {"role": "user", "content": "Classify this track: Rock guitar, live drums, 140 BPM, distorted vocals"}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
    ],
    
    TaskType.AUDIO_ANALYSIS: [
        {
            "messages": [
                {"role": "system", "content": "You are an audio analysis expert for music production."},
                {"role": "user", "content": "Analyze frequency spectrum: Strong low end 40-120Hz, mid scoop 400-800Hz, bright highs 8kHz+"}
            ],
            "max_tokens": 200,
            "temperature": 0.5
        },
        {
            "messages": [
                {"role": "system", "content": "You are an audio analysis expert for music production."},
                {"role": "user", "content": "Analyze dynamics: Peak at -6dB, RMS -18dB, high dynamic range, no compression"}
            ],
            "max_tokens": 200,
            "temperature": 0.5
        }
    ],
    
    TaskType.CREATIVE: [
        {
            "messages": [
                {"role": "system", "content": "You are a creative music production coach providing innovative ideas."},
                {"role": "user", "content": "Suggest creative variations for a lo-fi hip-hop beat"}
            ],
            "max_tokens": 300,
            "temperature": 0.8
        },
        {
            "messages": [
                {"role": "system", "content": "You are a creative music production coach providing innovative ideas."},
                {"role": "user", "content": "How can I make my EDM drop more impactful and unique?"}
            ],
            "max_tokens": 300,
            "temperature": 0.8
        }
    ],
    
    TaskType.FACTUAL: [
        {
            "messages": [
                {"role": "system", "content": "You are a music theory and production knowledge expert."},
                {"role": "user", "content": "Explain the circle of fifths in key modulation"}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        },
        {
            "messages": [
                {"role": "system", "content": "You are a music theory and production knowledge expert."},
                {"role": "user", "content": "What is side-chain compression and when should I use it?"}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }
    ],
    
    TaskType.SUMMARIZATION: [
        {
            "messages": [
                {"role": "system", "content": "You are an expert at summarizing music production sessions and feedback."},
                {"role": "user", "content": "Summarize: Track has good melody, weak drums, mix needs work on bass clarity, vocals sit too low"}
            ],
            "max_tokens": 100,
            "temperature": 0.4
        }
    ]
}


async def warm_cache_for_provider(
    provider: Provider,
    task_type: TaskType,
    prompts: List[Dict[str, Any]],
    simulate: bool = False
) -> Dict[str, Any]:
    """
    Warm cache for a specific provider and task type
    
    Args:
        provider: AI provider to warm cache for
        task_type: Type of task
        prompts: List of prompt payloads
        simulate: If True, only simulate without making real API calls
        
    Returns:
        Dictionary with warming statistics
    """
    model = get_provider_model(provider)
    url = get_provider_url(provider)
    
    stats = {
        "provider": provider.value,
        "task_type": task_type.value,
        "total_prompts": len(prompts),
        "cached": 0,
        "warmed": 0,
        "skipped": 0,
        "errors": 0,
        "start_time": datetime.now().isoformat()
    }
    
    logger.info(f"🔥 Warming cache for {provider.value} - {task_type.value} ({len(prompts)} prompts)")
    
    for i, payload in enumerate(prompts, 1):
        try:
            # Add model to payload
            full_payload = {**payload, "model": model}
            
            # Check if already cached
            cached = await get_cached_response(provider.value, full_payload)
            if cached:
                stats["cached"] += 1
                logger.debug(f"  [{i}/{len(prompts)}] Already cached: {prompt_fingerprint(full_payload)[:16]}...")
                continue
            
            if simulate:
                # In simulation mode, just create a mock response
                mock_response = {
                    "choices": [{"message": {"content": f"Simulated response for {task_type.value}"}}],
                    "usage": {"total_tokens": 100}
                }
                await cache_response(provider.value, full_payload, mock_response)
                stats["warmed"] += 1
                logger.info(f"  [{i}/{len(prompts)}] ✅ Simulated and cached")
            else:
                # TODO: Make real API call here when integrated with actual providers
                # For now, skip real API calls to avoid unnecessary costs during warmup
                stats["skipped"] += 1
                logger.debug(f"  [{i}/{len(prompts)}] ⏭️  Skipped (real API call needed)")
                
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"  [{i}/{len(prompts)}] ❌ Error: {e}")
    
    stats["end_time"] = datetime.now().isoformat()
    
    logger.info(
        f"✅ Completed {provider.value} warming: "
        f"{stats['cached']} cached, {stats['warmed']} warmed, "
        f"{stats['skipped']} skipped, {stats['errors']} errors"
    )
    
    return stats


async def warm_all_caches(
    providers: Optional[List[Provider]] = None,
    task_types: Optional[List[TaskType]] = None,
    simulate: bool = True
) -> Dict[str, Any]:
    """
    Warm caches for all providers and task types
    
    Args:
        providers: List of providers to warm (default: all)
        task_types: List of task types to warm (default: all in COMMON_PROMPTS)
        simulate: If True, use simulated responses instead of real API calls
        
    Returns:
        Overall warming statistics
    """
    if providers is None:
        providers = [Provider.OLLAMA, Provider.GEMINI, Provider.CLAUDE, Provider.OPENAI]
    
    if task_types is None:
        task_types = list(COMMON_PROMPTS.keys())
    
    overall_stats = {
        "total_providers": len(providers),
        "total_task_types": len(task_types),
        "total_prompts": sum(len(COMMON_PROMPTS.get(tt, [])) for tt in task_types),
        "provider_stats": [],
        "cache_stats_before": await get_cache_stats(),
        "start_time": datetime.now().isoformat()
    }
    
    logger.info("🚀 Starting cache warming...")
    logger.info(f"   Providers: {[p.value for p in providers]}")
    logger.info(f"   Task types: {[tt.value for tt in task_types]}")
    logger.info(f"   Simulate mode: {simulate}")
    logger.info(f"   Total prompts: {overall_stats['total_prompts']}")
    
    # Warm caches for each provider and task type
    for provider in providers:
        for task_type in task_types:
            prompts = COMMON_PROMPTS.get(task_type, [])
            if not prompts:
                continue
                
            provider_stats = await warm_cache_for_provider(
                provider=provider,
                task_type=task_type,
                prompts=prompts,
                simulate=simulate
            )
            overall_stats["provider_stats"].append(provider_stats)
    
    # Get final cache statistics
    overall_stats["cache_stats_after"] = await get_cache_stats()
    overall_stats["end_time"] = datetime.now().isoformat()
    
    # Calculate summary
    total_cached = sum(s["cached"] for s in overall_stats["provider_stats"])
    total_warmed = sum(s["warmed"] for s in overall_stats["provider_stats"])
    total_skipped = sum(s["skipped"] for s in overall_stats["provider_stats"])
    total_errors = sum(s["errors"] for s in overall_stats["provider_stats"])
    
    overall_stats["summary"] = {
        "cached": total_cached,
        "warmed": total_warmed,
        "skipped": total_skipped,
        "errors": total_errors,
        "cache_hit_improvement": (
            overall_stats["cache_stats_after"].get("hit_rate", 0) - 
            overall_stats["cache_stats_before"].get("hit_rate", 0)
        )
    }
    
    logger.info("=" * 60)
    logger.info("🎉 Cache warming complete!")
    logger.info(f"   Already cached: {total_cached}")
    logger.info(f"   Newly warmed: {total_warmed}")
    logger.info(f"   Skipped: {total_skipped}")
    logger.info(f"   Errors: {total_errors}")
    logger.info(f"   Cache hit rate: {overall_stats['cache_stats_after'].get('hit_rate', 0):.2%}")
    logger.info("=" * 60)
    
    return overall_stats


async def schedule_cache_warming(
    interval_hours: int = 24,
    run_immediately: bool = True,
    simulate: bool = True
):
    """
    Schedule periodic cache warming
    
    Args:
        interval_hours: Hours between cache warming runs
        run_immediately: Whether to run immediately on start
        simulate: Use simulated responses
    """
    logger.info(f"📅 Scheduling cache warming every {interval_hours} hours")
    
    if run_immediately:
        logger.info("▶️  Running immediate cache warming...")
        await warm_all_caches(simulate=simulate)
    
    while True:
        await asyncio.sleep(interval_hours * 3600)
        logger.info(f"⏰ Scheduled cache warming triggered")
        try:
            await warm_all_caches(simulate=simulate)
        except Exception as e:
            logger.error(f"Error during scheduled cache warming: {e}")


# CLI interface
async def main():
    """CLI entry point for manual cache warming"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SampleMind AI Cache Warming Utility")
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["ollama", "gemini", "claude", "openai"],
        help="Providers to warm (default: all)"
    )
    parser.add_argument(
        "--task-types",
        nargs="+",
        help="Task types to warm (default: all)"
    )
    parser.add_argument(
        "--no-simulate",
        action="store_true",
        help="Make real API calls (costs money!)"
    )
    parser.add_argument(
        "--schedule",
        type=int,
        metavar="HOURS",
        help="Schedule periodic warming every N hours"
    )
    
    args = parser.parse_args()
    
    # Parse providers
    providers = None
    if args.providers:
        provider_map = {
            "ollama": Provider.OLLAMA,
            "gemini": Provider.GEMINI,
            "claude": Provider.CLAUDE,
            "openai": Provider.OPENAI
        }
        providers = [provider_map[p] for p in args.providers]
    
    # Parse task types
    task_types = None
    if args.task_types:
        task_type_map = {
            "genre": TaskType.GENRE_CLASSIFICATION,
            "audio": TaskType.AUDIO_ANALYSIS,
            "creative": TaskType.CREATIVE,
            "factual": TaskType.FACTUAL,
            "tools": TaskType.TOOL_CALLING,
            "summary": TaskType.SUMMARIZATION,
            "transcription": TaskType.TRANSCRIPTION
        }
        task_types = [task_type_map.get(t) for t in args.task_types if task_type_map.get(t)]
    
    simulate = not args.no_simulate
    
    if args.schedule:
        # Run scheduled warming
        await schedule_cache_warming(
            interval_hours=args.schedule,
            run_immediately=True,
            simulate=simulate
        )
    else:
        # Run one-time warming
        stats = await warm_all_caches(
            providers=providers,
            task_types=task_types,
            simulate=simulate
        )
        
        # Print summary
        import json
        print("\n" + "=" * 60)
        print("CACHE WARMING SUMMARY")
        print("=" * 60)
        print(json.dumps(stats["summary"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
