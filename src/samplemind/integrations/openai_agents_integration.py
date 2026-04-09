#!/usr/bin/env python3
"""
SampleMind AI — OpenAI Agents SDK Integration
Three-agent pipeline: AudioAnalysisAgent → TaggingAgent → OrganizationAgent

Uses ``openai-agents ^0.0.5`` to orchestrate a multi-step audio workflow with
full OpenAI Tracing enabled for observability.

Agent responsibilities:
- AudioAnalysisAgent: Extracts musical features, genre, mood, BPM, key.
- TaggingAgent:        Generates semantic tags from analysis output.
- OrganizationAgent:  Suggests optimal folder/library organisation.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

try:
    from agents import Agent, Runner, function_tool, trace

    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False
    logger.warning(
        "openai-agents not installed. Install with: "
        "poetry add 'openai-agents ^0.0.5'"
    )


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class AgentPipelineResult:
    """Collected output from the three-agent pipeline run."""

    # AudioAnalysisAgent output
    genre: str = ""
    sub_genres: list[str] = field(default_factory=list)
    mood: str = ""
    bpm: float = 0.0
    key: str = ""
    energy_level: str = ""
    production_notes: str = ""

    # TaggingAgent output
    semantic_tags: list[str] = field(default_factory=list)
    mood_tags: list[str] = field(default_factory=list)
    instrument_tags: list[str] = field(default_factory=list)

    # OrganizationAgent output
    suggested_folder: str = ""
    pack_name: str = ""
    organization_notes: str = ""

    # Pipeline metadata
    trace_url: str = ""
    total_tokens: int = 0


# ---------------------------------------------------------------------------
# Tool functions exposed to agents
# ---------------------------------------------------------------------------

if OPENAI_AGENTS_AVAILABLE:

    @function_tool
    def describe_audio_features(features_json: str) -> str:
        """
        Convert a JSON dict of raw audio features into a human-readable description.

        Args:
            features_json: JSON string with audio feature keys.

        Returns:
            A one-paragraph plain-English description of the track.
        """
        try:
            features = json.loads(features_json)
        except json.JSONDecodeError:
            return "Could not parse audio features."

        bpm = features.get("tempo", "unknown")
        key = features.get("key", "unknown")
        mode = features.get("mode", "major")
        duration = features.get("duration", "unknown")
        energy = features.get("energy", "unknown")
        return (
            f"The track runs at {bpm} BPM in {key} {mode}, "
            f"with a duration of {duration}s and an energy level of {energy}."
        )

    @function_tool
    def generate_semantic_tags(analysis_text: str) -> str:
        """
        Derive semantic tags from the analysis text produced by AudioAnalysisAgent.

        Args:
            analysis_text: Plain-text analysis from AudioAnalysisAgent.

        Returns:
            JSON array of lowercase tag strings.
        """
        # The model will fill this in; we provide the signature for tool routing.
        return json.dumps({"tags": [], "note": "Agent should generate tags from text."})

    @function_tool
    def suggest_folder_structure(tags_json: str, genre: str) -> str:
        """
        Suggest a folder path for organising the sample into a library.

        Args:
            tags_json: JSON string with ``tags`` array from TaggingAgent.
            genre: Primary genre string.

        Returns:
            JSON object with ``folder`` (string path) and ``pack_name``.
        """
        try:
            data = json.loads(tags_json)
            tags = data.get("tags", [])
        except json.JSONDecodeError:
            tags = []

        folder = f"Library/{genre.capitalize()}"
        if "drums" in tags or "percussion" in tags:
            folder += "/Drums"
        elif "bass" in tags:
            folder += "/Bass"
        elif "lead" in tags or "melody" in tags:
            folder += "/Melodic"

        return json.dumps({"folder": folder, "pack_name": f"{genre.capitalize()} Pack"})


# ---------------------------------------------------------------------------
# Agent pipeline class
# ---------------------------------------------------------------------------


class AudioAgentPipeline:
    """
    Three-agent OpenAI Agents SDK pipeline for audio analysis.

    Usage::

        pipeline = AudioAgentPipeline(api_key="sk-...")
        result = await pipeline.run(audio_features, sample_name="kick_001.wav")
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
        enable_tracing: bool = True,
    ) -> None:
        if not OPENAI_AGENTS_AVAILABLE:
            raise ImportError(
                "openai-agents package required. "
                "Install with: poetry add 'openai-agents ^0.0.5'"
            )
        import os

        if api_key:
            os.environ.setdefault("OPENAI_API_KEY", api_key)

        self.model = model
        self.enable_tracing = enable_tracing
        self._build_agents()
        logger.info(f"AudioAgentPipeline initialised (model={model})")

    def _build_agents(self) -> None:
        """Instantiate the three specialised agents."""

        self.analysis_agent = Agent(
            name="AudioAnalysisAgent",
            model=self.model,
            instructions=(
                "You are an expert audio engineer and music consultant. "
                "Given raw audio features, produce a concise but thorough analysis: "
                "genre, sub-genres, mood, BPM, key/scale, energy level, and production notes. "
                "Use the describe_audio_features tool to format the input first."
            ),
            tools=[describe_audio_features],
        )

        self.tagging_agent = Agent(
            name="TaggingAgent",
            model=self.model,
            instructions=(
                "You are a music cataloguing expert. "
                "Given an audio analysis, produce a structured set of semantic tags: "
                "mood tags, instrument tags, and general semantic tags. "
                "Use generate_semantic_tags to structure your output as a JSON array."
            ),
            tools=[generate_semantic_tags],
        )

        self.organisation_agent = Agent(
            name="OrganizationAgent",
            model=self.model,
            instructions=(
                "You are a professional sample library manager. "
                "Given tags and genre, suggest an optimal folder path and pack name "
                "for a sample library. Use suggest_folder_structure to format the result."
            ),
            tools=[suggest_folder_structure],
        )

    async def run(
        self,
        audio_features: dict[str, Any],
        sample_name: str = "sample",
    ) -> AgentPipelineResult:
        """
        Run the full three-agent pipeline for a single audio sample.

        Args:
            audio_features: Feature dict from the audio engine.
            sample_name: Human-readable filename for logging.

        Returns:
            AgentPipelineResult with combined output from all agents.
        """
        features_json = json.dumps(audio_features)
        result = AgentPipelineResult()
        total_tokens = 0

        ctx_manager = (
            trace(f"SampleMind:{sample_name}") if self.enable_tracing else _null_ctx()
        )

        async with ctx_manager as run_trace:
            if self.enable_tracing and hasattr(run_trace, "url"):
                result.trace_url = run_trace.url or ""

            # --- Step 1: audio analysis ---
            analysis_run = await Runner.run(
                self.analysis_agent,
                f"Analyse this audio sample named '{sample_name}'. Features:\n{features_json}",
            )
            analysis_text: str = analysis_run.final_output or ""
            if hasattr(analysis_run, "usage") and analysis_run.usage:
                total_tokens += analysis_run.usage.total_tokens or 0

            # Parse genre/mood/key from natural-language output (best-effort)
            result.production_notes = analysis_text
            for line in analysis_text.splitlines():
                lower = line.lower()
                if "genre:" in lower:
                    result.genre = line.split(":", 1)[-1].strip()
                elif "mood:" in lower:
                    result.mood = line.split(":", 1)[-1].strip()
                elif "key:" in lower:
                    result.key = line.split(":", 1)[-1].strip()
                elif "bpm:" in lower or "tempo:" in lower:
                    try:
                        result.bpm = float(
                            "".join(
                                c
                                for c in line.split(":", 1)[-1].strip()
                                if c.isdigit() or c == "."
                            )
                        )
                    except ValueError:
                        pass

            # --- Step 2: tagging ---
            tag_run = await Runner.run(
                self.tagging_agent,
                f"Generate tags for this track analysis:\n{analysis_text}",
            )
            tags_text: str = tag_run.final_output or ""
            if hasattr(tag_run, "usage") and tag_run.usage:
                total_tokens += tag_run.usage.total_tokens or 0

            # Try to extract JSON tags
            try:
                if "{" in tags_text:
                    start = tags_text.index("{")
                    end = tags_text.rindex("}") + 1
                    tags_data = json.loads(tags_text[start:end])
                    result.semantic_tags = tags_data.get("tags", [])
                    result.mood_tags = tags_data.get("mood_tags", [])
                    result.instrument_tags = tags_data.get("instrument_tags", [])
            except (ValueError, json.JSONDecodeError):
                # Fallback: split comma-separated tags
                result.semantic_tags = [
                    t.strip() for t in tags_text.split(",") if t.strip()
                ]

            # --- Step 3: organisation ---
            genre = result.genre or audio_features.get("genre", "Unknown")
            org_run = await Runner.run(
                self.organisation_agent,
                f"Suggest organisation for a {genre} sample with tags: {result.semantic_tags}",
            )
            org_text: str = org_run.final_output or ""
            if hasattr(org_run, "usage") and org_run.usage:
                total_tokens += org_run.usage.total_tokens or 0

            try:
                if "{" in org_text:
                    start = org_text.index("{")
                    end = org_text.rindex("}") + 1
                    org_data = json.loads(org_text[start:end])
                    result.suggested_folder = org_data.get("folder", "")
                    result.pack_name = org_data.get("pack_name", "")
                    result.organization_notes = org_text
            except (ValueError, json.JSONDecodeError):
                result.organization_notes = org_text

        result.total_tokens = total_tokens
        logger.info(
            f"Pipeline complete for '{sample_name}': "
            f"genre={result.genre}, tags={len(result.semantic_tags)}, "
            f"tokens={total_tokens}"
        )
        return result


# ---------------------------------------------------------------------------
# Null context manager for when tracing is disabled
# ---------------------------------------------------------------------------


class _null_ctx:
    async def __aenter__(self) -> "_null_ctx":
        return self

    async def __aexit__(self, *_: Any) -> None:
        pass
