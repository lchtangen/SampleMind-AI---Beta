#!/usr/bin/env python3
"""
SampleMind AI v6 - Anthropic (Claude) Integration
Specialized AI provider for production coaching and creative suggestions

This module provides Claude Sonnet 4.5 and Opus 4.1 integration optimized for:
- Production coaching and technique analysis (Sonnet 4.5)
- Creative arrangement suggestions (Sonnet 4.5)
- FL Studio optimization recommendations (Sonnet 4.5)
- Deep music theory explanations (Opus 4.1 for complex analysis)
- Advanced composition and harmonic analysis (Opus 4.1)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json

try:
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Available Claude models"""
    # Latest models (recommended) - October 2025
    CLAUDE_SONNET_4_5 = "claude-4-sonnet-20250514"  # Standard production workflows (200K context)
    CLAUDE_OPUS_4_1 = "claude-4-opus-20250514"      # Complex music theory and composition (200K context)

    # Legacy models (backwards compatibility)
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"  # Legacy Claude 3.5 Sonnet
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class AnthropicAnalysisType(Enum):
    """Analysis types optimized for Claude"""
    PRODUCTION_COACHING = "production_coaching"
    CREATIVE_SUGGESTIONS = "creative_suggestions"
    FL_STUDIO_OPTIMIZATION = "fl_studio_optimization"
    MUSIC_THEORY_ANALYSIS = "music_theory_analysis"
    ARRANGEMENT_ADVICE = "arrangement_advice"
    MIXING_MASTERING = "mixing_mastering"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"


@dataclass
class AnthropicMusicAnalysis:
    """Result from Claude music analysis"""

    # Core Analysis
    summary: str
    detailed_analysis: str

    # Production Coaching
    production_tips: List[str] = field(default_factory=list)
    technique_explanations: List[Dict[str, str]] = field(default_factory=list)
    workflow_optimizations: List[str] = field(default_factory=list)

    # Creative Suggestions
    creative_ideas: List[str] = field(default_factory=list)
    arrangement_suggestions: List[str] = field(default_factory=list)
    genre_fusion_ideas: List[str] = field(default_factory=list)

    # FL Studio Specific
    fl_studio_recommendations: List[str] = field(default_factory=list)
    plugin_chains: List[Dict[str, Any]] = field(default_factory=list)
    mixer_setup: Dict[str, Any] = field(default_factory=dict)

    # Music Theory
    harmonic_analysis: Dict[str, Any] = field(default_factory=dict)
    modal_analysis: List[str] = field(default_factory=list)
    chord_progressions: List[str] = field(default_factory=list)

    # Metadata
    model_used: ClaudeModel = ClaudeModel.CLAUDE_SONNET_4_5
    tokens_used: int = 0
    processing_time: float = 0.0
    timestamp: float = field(default_factory=time.time)
    confidence_score: float = 0.0


class AnthropicMusicProducer:
    """
    Claude-powered music production assistant

    Specializes in:
    - Production coaching with detailed explanations (Sonnet 4.5)
    - Creative suggestions and arrangement ideas (Sonnet 4.5)
    - FL Studio optimization and workflow tips (Sonnet 4.5)
    - Deep music theory analysis (Opus 4.1 for complex tasks)
    - Advanced composition and harmonic analysis (Opus 4.1)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: ClaudeModel = ClaudeModel.CLAUDE_SONNET_4_5,
        opus_model: ClaudeModel = ClaudeModel.CLAUDE_OPUS_4_1,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialize Anthropic Music Producer

        Args:
            api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY env var)
            default_model: Claude model for standard tasks (Sonnet 4.5)
            opus_model: Claude model for complex tasks (Opus 4.1)
            max_tokens: Maximum tokens per response
            temperature: Response creativity (0.0-1.0)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)
        self.default_model = default_model
        self.opus_model = opus_model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Performance tracking
        self.stats = {
            'total_analyses': 0,
            'total_tokens_used': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0,
            'success_count': 0,
            'error_count': 0
        }

        logger.info(f"✅ Anthropic Music Producer initialized")
        logger.info(f"   Standard model: {default_model.value}")
        logger.info(f"   Complex model: {opus_model.value}")

    async def analyze_music_comprehensive(
        self,
        audio_features: Dict[str, Any],
        analysis_type: AnthropicAnalysisType = AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS,
        user_context: Optional[Dict[str, Any]] = None
    ) -> AnthropicMusicAnalysis:
        """
        Perform comprehensive music analysis with Claude

        Args:
            audio_features: Audio features from audio engine
            analysis_type: Type of analysis to perform
            user_context: Additional user context

        Returns:
            AnthropicMusicAnalysis with detailed insights
        """
        start_time = time.time()

        try:
            # Build specialized prompt based on analysis type
            prompt = self._build_prompt(audio_features, analysis_type, user_context)

            # Call Claude API
            response = await self.async_client.messages.create(
                model=self.default_model.value,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            result = self._parse_response(response, analysis_type)

            # Update statistics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.tokens_used = response.usage.input_tokens + response.usage.output_tokens

            self._update_stats(result.tokens_used, processing_time, success=True)

            logger.info(
                f"✅ Claude analysis complete: {result.tokens_used} tokens, "
                f"{processing_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Claude analysis failed: {e}")
            self._update_stats(0, time.time() - start_time, success=False)
            raise

    def _build_prompt(
        self,
        audio_features: Dict[str, Any],
        analysis_type: AnthropicAnalysisType,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build specialized prompt for Claude based on analysis type"""

        # Extract key audio features
        tempo = audio_features.get('tempo', 'Unknown')
        key = audio_features.get('key', 'Unknown')
        mode = audio_features.get('mode', 'Unknown')
        energy = audio_features.get('energy', 'Unknown')
        duration = audio_features.get('duration', 'Unknown')

        # Base context
        base_context = f"""You are an expert music producer and audio engineer with deep knowledge of:
- Music production techniques and workflow optimization
- FL Studio and professional DAW usage
- Music theory, harmony, and composition
- Sound design and mixing/mastering
- Creative arrangement and genre exploration

Analyze the following audio track:

**Audio Features:**
- Tempo: {tempo} BPM
- Key: {key} {mode}
- Energy Level: {energy}
- Duration: {duration}s
"""

        if user_context:
            base_context += f"\n**User Context:** {json.dumps(user_context, indent=2)}\n"

        # Add specialized prompts based on analysis type
        if analysis_type == AnthropicAnalysisType.PRODUCTION_COACHING:
            specific_prompt = """
**Task: Production Coaching**

Provide detailed production coaching covering:

1. **Technical Analysis**: Mix balance, frequency spectrum, dynamics
2. **Production Techniques**: Specific techniques used and alternative approaches
3. **Workflow Optimization**: Tips to improve efficiency and creativity
4. **Common Mistakes**: Potential issues to avoid or fix
5. **Next Steps**: Actionable recommendations for improvement

Be specific, educational, and encouraging. Use analogies and examples.
"""

        elif analysis_type == AnthropicAnalysisType.CREATIVE_SUGGESTIONS:
            specific_prompt = """
**Task: Creative Suggestions**

Provide innovative creative suggestions:

1. **Arrangement Ideas**: Structural changes, build-ups, breakdowns
2. **Genre Fusion**: Ways to blend genres or add unexpected elements
3. **Instrumentation**: New instrument ideas or layering techniques
4. **Textural Variations**: Ways to add depth and interest
5. **Experimental Approaches**: Bold creative directions to explore

Think outside the box. Suggest unique, inspiring ideas.
"""

        elif analysis_type == AnthropicAnalysisType.FL_STUDIO_OPTIMIZATION:
            specific_prompt = """
**Task: FL Studio Optimization**

Provide FL Studio-specific recommendations:

1. **Native Plugins**: Which FL Studio plugins to use and why
2. **Mixer Setup**: Channel routing, send effects, and organization
3. **Effect Chains**: Step-by-step effect chain construction
4. **Automation**: Key parameters to automate for dynamics
5. **Project Template**: How to structure the project for this style
6. **Keyboard Shortcuts**: Workflow-boosting shortcuts and techniques

Be specific to FL Studio 21+. Include practical, implementable steps.
"""

        elif analysis_type == AnthropicAnalysisType.MUSIC_THEORY_ANALYSIS:
            specific_prompt = """
**Task: Music Theory Analysis**

Provide deep music theory analysis:

1. **Harmonic Analysis**: Chord progressions, voice leading, modal interchange
2. **Modal Context**: Scales, modes, and their emotional implications
3. **Rhythmic Structure**: Meter, syncopation, polyrhythms
4. **Melodic Construction**: Interval relationships, contour, motifs
5. **Form & Structure**: Phrase structure, sections, macro-organization
6. **Theory Applications**: How theory choices create the musical effect

Be thorough and educational. Explain complex concepts clearly.
"""

        elif analysis_type == AnthropicAnalysisType.MIXING_MASTERING:
            specific_prompt = """
**Task: Mixing & Mastering Analysis**

Provide mixing and mastering guidance:

1. **Frequency Balance**: EQ decisions and spectral analysis
2. **Dynamic Control**: Compression, limiting, and dynamics processing
3. **Spatial Design**: Panning, reverb, and stereo width
4. **Problem Frequencies**: Areas to address with EQ or multiband compression
5. **Mastering Chain**: Suggested mastering processing order
6. **Reference Tracks**: Commercial tracks to reference for this style

Provide specific frequency ranges, ratio settings, and processing tips.
"""

        else:  # COMPREHENSIVE_ANALYSIS or default
            specific_prompt = """
**Task: Comprehensive Music Analysis**

Provide a thorough analysis covering:

1. **Overview**: Genre, style, mood, and overall impression
2. **Production Quality**: Mix balance, sound design, technical execution
3. **Creative Elements**: Arrangement, instrumentation, unique features
4. **Music Theory**: Harmony, rhythm, melody, structure
5. **FL Studio Tips**: Specific plugin and technique recommendations
6. **Improvement Suggestions**: 3-5 actionable ways to enhance the track
7. **Creative Directions**: New ideas to explore

Be comprehensive, insightful, and constructive.
"""

        # Format output structure
        output_format = """
**Output Format:**
Provide your response as a structured JSON object with these keys:
{
    "summary": "Brief 2-3 sentence overview",
    "detailed_analysis": "Comprehensive analysis (2-3 paragraphs)",
    "production_tips": ["tip1", "tip2", ...],
    "creative_ideas": ["idea1", "idea2", ...],
    "fl_studio_recommendations": ["rec1", "rec2", ...],
    "arrangement_suggestions": ["suggestion1", "suggestion2", ...],
    "harmonic_analysis": {"key_info": "...", "progressions": [...]},
    "confidence_score": 0.0-1.0
}
"""

        return base_context + specific_prompt + output_format

    def _parse_response(
        self,
        response: Any,
        analysis_type: AnthropicAnalysisType
    ) -> AnthropicMusicAnalysis:
        """Parse Claude API response into structured analysis"""

        # Extract text content
        content = response.content[0].text

        try:
            # Try to parse as JSON
            if "{" in content and "}" in content:
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                data = json.loads(content)
            else:
                # Fallback: treat entire response as summary
                data = {
                    "summary": content[:500],
                    "detailed_analysis": content
                }

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback format")
            data = {
                "summary": content[:500],
                "detailed_analysis": content
            }

        # Build structured result
        return AnthropicMusicAnalysis(
            summary=data.get("summary", ""),
            detailed_analysis=data.get("detailed_analysis", content),
            production_tips=data.get("production_tips", []),
            technique_explanations=data.get("technique_explanations", []),
            workflow_optimizations=data.get("workflow_optimizations", []),
            creative_ideas=data.get("creative_ideas", []),
            arrangement_suggestions=data.get("arrangement_suggestions", []),
            genre_fusion_ideas=data.get("genre_fusion_ideas", []),
            fl_studio_recommendations=data.get("fl_studio_recommendations", []),
            plugin_chains=data.get("plugin_chains", []),
            mixer_setup=data.get("mixer_setup", {}),
            harmonic_analysis=data.get("harmonic_analysis", {}),
            modal_analysis=data.get("modal_analysis", []),
            chord_progressions=data.get("chord_progressions", []),
            model_used=self.default_model,
            confidence_score=data.get("confidence_score", 0.85)
        )

    def _update_stats(self, tokens_used: int, processing_time: float, success: bool):
        """Update performance statistics"""
        self.stats['total_analyses'] += 1

        if success:
            self.stats['success_count'] += 1
            self.stats['total_tokens_used'] += tokens_used

            # Calculate cost (Claude 3.5 Sonnet pricing)
            # Input: $3/MTok, Output: $15/MTok (approximate average: $9/MTok)
            cost = (tokens_used / 1000) * 0.009
            self.stats['total_cost'] += cost

            # Update average response time
            prev_avg = self.stats['avg_response_time']
            count = self.stats['success_count']
            self.stats['avg_response_time'] = (
                (prev_avg * (count - 1) + processing_time) / count
            )
        else:
            self.stats['error_count'] += 1

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['success_count'] / self.stats['total_analyses']
                if self.stats['total_analyses'] > 0 else 0.0
            ),
            'avg_tokens_per_analysis': (
                self.stats['total_tokens_used'] / self.stats['success_count']
                if self.stats['success_count'] > 0 else 0
            ),
            'cost_per_analysis': (
                self.stats['total_cost'] / self.stats['success_count']
                if self.stats['success_count'] > 0 else 0.0
            )
        }

    def shutdown(self):
        """Cleanup resources"""
        logger.info("🔄 Anthropic Music Producer shutting down")
        logger.info(f"📊 Final stats: {self.get_performance_stats()}")


# Convenience function for quick analysis
async def analyze_with_claude(
    audio_features: Dict[str, Any],
    api_key: Optional[str] = None,
    analysis_type: AnthropicAnalysisType = AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS
) -> AnthropicMusicAnalysis:
    """
    Quick analysis with Claude

    Args:
        audio_features: Audio features dictionary
        api_key: Anthropic API key (optional)
        analysis_type: Type of analysis

    Returns:
        AnthropicMusicAnalysis result
    """
    producer = AnthropicMusicProducer(api_key=api_key)
    result = await producer.analyze_music_comprehensive(audio_features, analysis_type)
    producer.shutdown()
    return result
