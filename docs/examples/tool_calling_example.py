#!/usr/bin/env python3
"""
Example: Reliable AI Tool Calling with Multiple Providers

This example demonstrates how to use AI agents with tool calling
across OpenAI, Anthropic, and Google Gemini without degraded performance.
"""

import asyncio
import logging
from typing import List, Dict, Any

from samplemind.ai import (
    Provider,
    TaskType,
    build_openai_request,
    build_anthropic_request,
    build_gemini_request,
    optimize_for_tool_calling,
    make_ai_request,
    get_http_client,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Example Tool Definitions
# ============================================================================

def get_audio_analysis_tools() -> List[Dict[str, Any]]:
    """Define tools for audio analysis"""
    return [
        {
            "name": "detect_genre",
            "description": "Detect the music genre from audio features",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Primary genre classification"
                    },
                    "sub_genres": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sub-genre classifications"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score 0-1"
                    }
                },
                "required": ["genre", "confidence"]
            }
        },
        {
            "name": "extract_bpm",
            "description": "Extract beats per minute from audio",
            "parameters": {
                "type": "object",
                "properties": {
                    "bpm": {
                        "type": "number",
                        "description": "Detected BPM"
                    },
                    "time_signature": {
                        "type": "string",
                        "description": "Time signature (e.g., '4/4')"
                    }
                },
                "required": ["bpm"]
            }
        },
        {
            "name": "get_production_tips",
            "description": "Generate FL Studio production tips for the genre",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Music genre"
                    },
                    "tips": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of production tips"
                    }
                },
                "required": ["genre", "tips"]
            }
        }
    ]


# ============================================================================
# Tool Calling Examples
# ============================================================================

async def example_openai_tool_calling():
    """Example: OpenAI with parallel tool calls"""
    logger.info("🔷 OpenAI Tool Calling Example")
    
    tools = get_audio_analysis_tools()
    
    # Build request with our helper
    payload = build_openai_request(
        messages=[
            {
                "role": "system",
                "content": "You are an audio analysis assistant. Use the provided tools to analyze music."
            },
            {
                "role": "user",
                "content": "Analyze this EDM track: 128 BPM, heavy bass, energetic synths"
            }
        ],
        task_type=TaskType.TOOL_CALLING,
        functions=tools,
        parallel_tool_calls=True  # ✅ Enable parallel calls
    )
    
    # Optimize for tool calling
    payload = optimize_for_tool_calling(
        provider=Provider.OPENAI,
        payload=payload,
        num_tools=len(tools)
    )
    
    logger.info(f"Request payload: temperature={payload.get('temperature')}, stream={payload.get('stream')}")
    
    # Make request (simulated)
    logger.info("✅ OpenAI request optimized for reliable tool calling")
    return payload


async def example_claude_tool_calling():
    """Example: Claude with prompt caching"""
    logger.info("🟣 Anthropic Claude Tool Calling Example")
    
    tools = get_audio_analysis_tools()
    
    # Build request with prompt caching
    system_prompt = """You are an expert music producer and audio analyst.
Use the provided tools to analyze music tracks and provide production advice.
Focus on accuracy and detailed technical analysis."""
    
    payload = build_anthropic_request(
        messages=[
            {
                "role": "user",
                "content": "What genre is this track with heavy 808s and trap hi-hats?"
            }
        ],
        task_type=TaskType.TOOL_CALLING,
        system_prompt=system_prompt,
        enable_prompt_caching=True  # ✅ 60-90% cost reduction
    )
    
    # Note: Claude requires tools in a specific format
    # This would be handled by build_anthropic_request if extended
    
    # Optimize
    payload = optimize_for_tool_calling(
        provider=Provider.CLAUDE,
        payload=payload,
        num_tools=len(tools)
    )
    
    logger.info(f"Request payload: temperature={payload.get('temperature')}")
    logger.info("✅ Claude request optimized with prompt caching")
    return payload


async def example_gemini_tool_calling():
    """Example: Gemini with function declarations"""
    logger.info("🔴 Google Gemini Tool Calling Example")
    
    # Gemini uses slightly different format for tools
    tools = [
        {
            "name": "detect_genre",
            "description": "Detect music genre from audio features",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "genre": {
                        "type": "STRING",
                        "description": "Primary genre"
                    },
                    "confidence": {
                        "type": "NUMBER",
                        "description": "Confidence 0-1"
                    }
                },
                "required": ["genre", "confidence"]
            }
        }
    ]
    
    payload = build_gemini_request(
        messages=[
            {
                "role": "user",
                "content": "Classify this track: 140 BPM, wobble bass, aggressive drums"
            }
        ],
        task_type=TaskType.TOOL_CALLING,
        tools=tools,  # ✅ Tools now supported
        enable_json_mode=True  # ✅ Structured output
    )
    
    # Optimize
    payload = optimize_for_tool_calling(
        provider=Provider.GEMINI,
        payload=payload,
        num_tools=len(tools)
    )
    
    logger.info(f"Request payload: temperature={payload['generationConfig']['temperature']}")
    logger.info("✅ Gemini request optimized with function declarations")
    return payload


async def example_multi_provider_comparison():
    """Example: Compare tool calling across all providers"""
    logger.info("\n🔄 Multi-Provider Tool Calling Comparison\n")
    
    results = {}
    
    # Test each provider
    results['openai'] = await example_openai_tool_calling()
    print()
    results['claude'] = await example_claude_tool_calling()
    print()
    results['gemini'] = await example_gemini_tool_calling()
    
    # Summary
    logger.info("\n📊 Configuration Summary:")
    for provider, payload in results.items():
        if provider == 'gemini':
            temp = payload.get('generationConfig', {}).get('temperature', 'N/A')
        else:
            temp = payload.get('temperature', 'N/A')
        
        logger.info(f"  {provider}: temperature={temp}, optimized=✅")
    
    return results


# ============================================================================
# Best Practices Demo
# ============================================================================

async def demonstrate_best_practices():
    """Demonstrate all tool calling best practices"""
    logger.info("\n🎯 Tool Calling Best Practices Demo\n")
    
    logger.info("✅ Best Practice 1: Low Temperature")
    logger.info("   → Keep temperature ≤ 0.2 for reliable tool calls")
    
    logger.info("\n✅ Best Practice 2: Disable Streaming")
    logger.info("   → Streaming degrades structured output reliability")
    
    logger.info("\n✅ Best Practice 3: Use Latest Models")
    logger.info("   → GPT-4o, Claude 3.5 Sonnet, Gemini 2.5 Pro")
    
    logger.info("\n✅ Best Practice 4: Proper Tool Declarations")
    logger.info("   → Use provider-specific formats")
    
    logger.info("\n✅ Best Practice 5: Adequate Token Limits")
    logger.info("   → Set max_tokens ≥ 1000 for tool responses")
    
    logger.info("\n✅ Best Practice 6: Use Optimization Helper")
    logger.info("   → Call optimize_for_tool_calling() automatically")
    
    logger.info("\n✅ Best Practice 7: Enable Provider Features")
    logger.info("   → Parallel tools (OpenAI), Prompt caching (Claude)")
    
    logger.info("\n✅ Best Practice 8: Test Across Providers")
    logger.info("   → Verify reliability with all AI providers")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples"""
    print("=" * 70)
    print("  🛠️  AI Tool Calling Examples - Avoiding Degraded Performance")
    print("=" * 70)
    
    # Run demonstrations
    await demonstrate_best_practices()
    print()
    await example_multi_provider_comparison()
    
    print("\n" + "=" * 70)
    print("  ✅ All examples completed successfully!")
    print("  📚 See docs/AI_TOOL_CALLING_BEST_PRACTICES.md for details")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
