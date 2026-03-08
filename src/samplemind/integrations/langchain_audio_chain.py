#!/usr/bin/env python3
"""
SampleMind AI — LangGraph Audio Analysis Chain
Five-node StateGraph: analyze → classify → tag → embed → search

Uses ``langgraph ^0.2.0`` and ``langchain-core ^0.3.0`` to build a stateful,
Redis-checkpointed audio processing workflow.

Node responsibilities:
  analyze   — Extract musical features from audio feature dict using Anthropic.
  classify  — Classify genre and mood using Google Gemini (fast streaming).
  tag       — Generate semantic tags from classification result.
  embed     — Produce vector embedding via CLAP / NeuralFeatureExtractor.
  search    — Run vector similarity search in ChromaDB.
"""

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional imports — graceful degradation
# ---------------------------------------------------------------------------

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.redis import RedisSaver

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning(
        "langgraph not installed. Install with: poetry add 'langgraph ^0.2.0'"
    )

try:
    from langchain_core.messages import (
        HumanMessage as _HumanMessage,
        AIMessage as _AIMessage,
    )  # noqa: F401

    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False
    logger.warning(
        "langchain-core not installed. Install with: poetry add 'langchain-core ^0.3.0'"
    )


# ---------------------------------------------------------------------------
# Graph state schema
# ---------------------------------------------------------------------------


class AudioGraphState(TypedDict, total=False):
    """Shared state dictionary passed between graph nodes."""

    # Input
    audio_features: Dict[str, Any]
    audio_path: Optional[str]

    # Intermediate / output
    analysis_text: str
    genre: str
    sub_genres: List[str]
    mood: str
    semantic_tags: List[str]
    embedding: List[float]
    similar_samples: List[Dict[str, Any]]

    # Metadata
    errors: List[str]
    node_trace: List[str]


# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------


async def _node_analyze(state: AudioGraphState) -> AudioGraphState:
    """
    Node 1 — analyze
    Call Anthropic Claude to produce a detailed text analysis of the track.
    Falls back to a feature-dict summary if Anthropic is unavailable.
    """
    try:
        from samplemind.integrations.anthropic_integration import (
            AnthropicMusicProducer,
            AnthropicAnalysisType,
        )
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            producer = AnthropicMusicProducer(api_key=api_key)
            result = await producer.analyze_music_comprehensive(
                state.get("audio_features", {}),
                analysis_type=AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS,
            )
            analysis_text = f"{result.summary}\n\n{result.detailed_analysis}"
        else:
            features = state.get("audio_features", {})
            analysis_text = (
                f"Audio features — BPM: {features.get('tempo', '?')}, "
                f"Key: {features.get('key', '?')} {features.get('mode', '')}, "
                f"Duration: {features.get('duration', '?')}s"
            )
    except Exception as exc:
        analysis_text = f"Analysis unavailable: {exc}"
        state.setdefault("errors", []).append(f"analyze: {exc}")

    return {
        **state,
        "analysis_text": analysis_text,
        "node_trace": state.get("node_trace", []) + ["analyze"],
    }


async def _node_classify(state: AudioGraphState) -> AudioGraphState:
    """
    Node 2 — classify
    Use Google Gemini to classify genre and mood from the analysis text.
    """
    genre = ""
    sub_genres: List[str] = []
    mood = ""
    try:
        from samplemind.integrations.google_ai_integration import (
            GoogleAIMusicProducer,
            MusicAnalysisType,
        )
        import os

        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if api_key:
            producer = GoogleAIMusicProducer(api_key=api_key)
            result = await producer.analyze_music_comprehensive(
                state.get("audio_features", {}),
                analysis_type=MusicAnalysisType.GENRE_CLASSIFICATION,
            )
            genre = result.primary_genre
            sub_genres = result.secondary_genres
            mood = result.primary_mood
        else:
            genre = "Unknown"
            mood = "Neutral"
    except Exception as exc:
        genre = "Unknown"
        mood = "Neutral"
        state.setdefault("errors", []).append(f"classify: {exc}")

    return {
        **state,
        "genre": genre,
        "sub_genres": sub_genres,
        "mood": mood,
        "node_trace": state.get("node_trace", []) + ["classify"],
    }


async def _node_tag(state: AudioGraphState) -> AudioGraphState:
    """
    Node 3 — tag
    Generate semantic tags from genre, mood, and analysis text.
    Uses OpenAI GPT-4o-mini for speed and cost efficiency.
    """
    semantic_tags: List[str] = []
    try:
        from openai import AsyncOpenAI
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = AsyncOpenAI(api_key=api_key)
            prompt = (
                f"Generate 8–12 concise lowercase semantic tags for this audio sample. "
                f"Genre: {state.get('genre', 'unknown')}, Mood: {state.get('mood', 'unknown')}.\n"
                f"Analysis: {state.get('analysis_text', '')[:500]}\n"
                f'Return ONLY a JSON array of strings, e.g. ["tag1", "tag2"]'
            )
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            try:
                data = json.loads(content)
                # Handle both {"tags": [...]} and [...] responses
                if isinstance(data, list):
                    semantic_tags = data
                elif isinstance(data, dict):
                    semantic_tags = data.get(
                        "tags", list(data.values())[0] if data else []
                    )
            except json.JSONDecodeError:
                semantic_tags = []
        else:
            # Fallback: derive tags from genre and mood strings
            genre = state.get("genre", "")
            mood = state.get("mood", "")
            semantic_tags = [t for t in [genre.lower(), mood.lower()] if t]
    except Exception as exc:
        state.setdefault("errors", []).append(f"tag: {exc}")

    return {
        **state,
        "semantic_tags": semantic_tags,
        "node_trace": state.get("node_trace", []) + ["tag"],
    }


async def _node_embed(state: AudioGraphState) -> AudioGraphState:
    """
    Node 4 — embed
    Generate a CLAP embedding via NeuralFeatureExtractor.
    Falls back to a zero vector if the neural engine is unavailable.
    """
    embedding: List[float] = []
    audio_path = state.get("audio_path")
    try:
        from samplemind.core.engine.neural_engine import NeuralFeatureExtractor

        extractor = NeuralFeatureExtractor()
        if audio_path and not extractor.use_mock:
            emb = extractor.get_audio_embedding(str(audio_path))
            if emb is not None:
                embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
        if not embedding:
            # Use text-based embedding from tags
            tags = " ".join(state.get("semantic_tags", []))
            genre = state.get("genre", "")
            text = f"{genre} {tags}".strip()
            emb = extractor.get_text_embedding(text)
            if emb is not None:
                embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
    except Exception as exc:
        embedding = []
        state.setdefault("errors", []).append(f"embed: {exc}")

    return {
        **state,
        "embedding": embedding,
        "node_trace": state.get("node_trace", []) + ["embed"],
    }


async def _node_search(state: AudioGraphState) -> AudioGraphState:
    """
    Node 5 — search
    Run vector similarity search in ChromaDB using the produced embedding.
    """
    similar_samples: List[Dict[str, Any]] = []
    embedding = state.get("embedding", [])
    try:
        if embedding:
            from samplemind.core.search.vector_engine import VectorSearchEngine

            engine = VectorSearchEngine()
            results = await engine.search_by_embedding(embedding, top_k=5)
            similar_samples = results if isinstance(results, list) else []
    except Exception as exc:
        state.setdefault("errors", []).append(f"search: {exc}")

    return {
        **state,
        "similar_samples": similar_samples,
        "node_trace": state.get("node_trace", []) + ["search"],
    }


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


class AudioLangGraph:
    """
    LangGraph-based audio analysis pipeline.

    Builds a ``StateGraph`` with five nodes connected in sequence.
    Supports optional Redis checkpointing for resumable workflows.

    Usage::

        graph = AudioLangGraph()
        result = await graph.run(audio_features, audio_path="kick.wav")
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        enable_checkpointing: bool = True,
    ) -> None:
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "langgraph package required. "
                "Install with: poetry add 'langgraph ^0.2.0'"
            )
        self.redis_url = redis_url
        self.enable_checkpointing = enable_checkpointing
        self._graph = self._build_graph()
        logger.info("AudioLangGraph initialised")

    def _build_graph(self) -> Any:
        """Compile the StateGraph."""
        builder: StateGraph = StateGraph(AudioGraphState)

        # Register nodes
        builder.add_node("analyze", _node_analyze)
        builder.add_node("classify", _node_classify)
        builder.add_node("tag", _node_tag)
        builder.add_node("embed", _node_embed)
        builder.add_node("search", _node_search)

        # Linear edges
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "classify")
        builder.add_edge("classify", "tag")
        builder.add_edge("tag", "embed")
        builder.add_edge("embed", "search")
        builder.add_edge("search", END)

        # Attach Redis checkpointer if configured
        checkpointer = None
        if self.enable_checkpointing and self.redis_url:
            try:
                checkpointer = RedisSaver.from_conn_string(self.redis_url)
                logger.info(f"Redis checkpointing enabled: {self.redis_url}")
            except Exception as exc:
                logger.warning(f"Redis checkpointing unavailable: {exc}")

        return builder.compile(checkpointer=checkpointer)

    async def run(
        self,
        audio_features: Dict[str, Any],
        audio_path: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> AudioGraphState:
        """
        Execute the full analyse→classify→tag→embed→search pipeline.

        Args:
            audio_features: Feature dict from the audio engine.
            audio_path: Optional path to the source audio file (for CLAP embedding).
            thread_id: Optional checkpointing thread identifier for resumable runs.

        Returns:
            Final ``AudioGraphState`` after all nodes have executed.
        """
        initial_state: AudioGraphState = {
            "audio_features": audio_features,
            "audio_path": audio_path,
            "errors": [],
            "node_trace": [],
        }

        config = {}
        if thread_id:
            config["configurable"] = {"thread_id": thread_id}

        final_state: AudioGraphState = await self._graph.ainvoke(
            initial_state, config=config
        )

        logger.info(
            f"Graph complete — nodes: {final_state.get('node_trace', [])}, "
            f"tags: {len(final_state.get('semantic_tags', []))}, "
            f"similar: {len(final_state.get('similar_samples', []))}"
        )
        return final_state
