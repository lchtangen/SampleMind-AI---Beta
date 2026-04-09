"""
SampleMind AI — FastMCP Server (Phase 15 / v3.0)

Exposes SampleMind's core capabilities as MCP tools so Claude Code
(and any MCP-compatible client) can call them directly during a
music production session.

Tools available:
  - analyze_audio         Full pipeline analysis of an audio file
  - find_similar          Semantic similarity search across sample library
  - get_ai_coaching       Multi-provider AI music coaching
  - build_sample_pack     Automated sample pack manifest from a folder
  - tag_audio             Generate multi-label tags for a single file
  - get_analysis_status   Check async analysis job status

Start server:
    uvicorn samplemind.server.mcp_server:mcp_app --port 8001

Register in .mcp/config.json:
    {
      "servers": {
        "samplemind": {
          "url": "http://localhost:8001",
          "description": "SampleMind AI music production tools"
        }
      }
    }
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from fastmcp import FastMCP

    _FASTMCP_AVAILABLE = True
except ImportError:
    _FASTMCP_AVAILABLE = False
    logger.warning(
        "FastMCP not installed — MCP server unavailable. "
        "Install with: pip install fastmcp"
    )

if _FASTMCP_AVAILABLE:
    mcp = FastMCP(
        name="SampleMind AI",
        version="3.0.0",
        description=(
            "AI-powered music production tools: audio analysis, similarity search, "
            "AI coaching, sample pack building, and intelligent tagging."
        ),
    )

    # ── Tool: analyze_audio ──────────────────────────────────────────────────

    @mcp.tool()
    def analyze_audio(
        file_path: str,
        depth: str = "standard",
    ) -> Dict[str, Any]:
        """
        Run the full SampleMind analysis pipeline on an audio file.

        Args:
            file_path: Absolute path to a WAV, MP3, FLAC, or AIFF file.
            depth: Analysis depth — "quick", "standard", or "deep".
                   "quick" uses Ollama offline; "deep" uses Claude extended thinking.

        Returns:
            Full analysis report including BPM, key, genre tags, mood, mixing
            recommendations, similar samples, and AI coaching summary.
        """
        from samplemind.ai.agents import run_analysis_pipeline

        result = run_analysis_pipeline(file_path=file_path, analysis_depth=depth)
        return result.get("final_report", {"error": "Pipeline produced no output"})

    # ── Tool: find_similar ───────────────────────────────────────────────────

    @mcp.tool()
    def find_similar(
        file_path: str,
        top_k: int = 5,
        library_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find samples similar to the given audio file using vector embeddings.

        Args:
            file_path: Path to the reference audio file.
            top_k: Number of similar samples to return (default 5, max 20).
            library_dir: Optional directory to restrict the search to.

        Returns:
            List of similar samples with path, similarity score, BPM, and key.
        """
        top_k = min(top_k, 20)
        try:
            from samplemind.core.similarity.similarity import AudioEmbeddingEngine

            engine = AudioEmbeddingEngine()
            results = engine.find_similar(file_path, top_k=top_k) or []
            return [
                {
                    "path": str(r.path),
                    "score": round(r.score, 4),
                    "bpm": r.metadata.get("bpm"),
                    "key": r.metadata.get("key"),
                }
                for r in results
            ]
        except Exception as exc:
            logger.error("find_similar failed: %s", exc)
            return [{"error": str(exc)}]

    # ── Tool: get_ai_coaching ────────────────────────────────────────────────

    @mcp.tool()
    def get_ai_coaching(
        question: str,
        file_path: Optional[str] = None,
        provider: str = "auto",
    ) -> Dict[str, Any]:
        """
        Get AI music production coaching from Claude, Gemini, or GPT-4o.

        Args:
            question: Your music production question or request.
            file_path: Optional path to an audio file to include in the context.
            provider: AI provider — "auto", "anthropic", "google_ai", "openai", "ollama".

        Returns:
            AI coaching response with summary and detailed advice.
        """
        import asyncio

        from samplemind.integrations.ai_manager import AnalysisType, SampleMindAIManager

        audio_features: Dict[str, Any] = {"user_message": question}

        if file_path and Path(file_path).exists():
            try:
                from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine

                engine = AudioEngine()
                features = engine.analyze_file(file_path, level=AnalysisLevel.STANDARD)
                audio_features.update(
                    {
                        "bpm": features.bpm,
                        "key": features.key,
                        "scale": features.scale,
                        "duration": features.duration,
                    }
                )
            except Exception as exc:
                logger.warning("Audio context extraction failed: %s", exc)

        mgr = SampleMindAIManager()
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                mgr.analyze_music(
                    audio_features=audio_features,
                    analysis_type=AnalysisType.PRODUCTION_COACHING,
                    user_context={"prompt": question, "preferred_provider": provider},
                )
            )
        finally:
            loop.close()

        if result:
            return {
                "summary": result.summary,
                "detailed_analysis": result.detailed_analysis,
                "provider_used": result.provider_used,
                "tokens_used": result.tokens_used,
            }
        return {"error": "No response from AI providers"}

    # ── Tool: tag_audio ──────────────────────────────────────────────────────

    @mcp.tool()
    def tag_audio(file_path: str) -> Dict[str, Any]:
        """
        Generate multi-label genre, mood, energy, and instrument tags for an audio file.

        Args:
            file_path: Path to the audio file to tag.

        Returns:
            Tag dictionary with genre, mood, energy, bpm_range, instrument_hints,
            key_info, and raw_labels (flat list for embedding into file metadata).
        """
        from samplemind.ai.agents.state import AudioAnalysisState
        from samplemind.ai.agents.tagging_agent import tagging_agent
        from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine

        try:
            engine = AudioEngine()
            features = engine.analyze_file(file_path, level=AnalysisLevel.STANDARD)
            state: AudioAnalysisState = {
                "file_path": file_path,
                "audio_features": {
                    "bpm": features.bpm,
                    "key": features.key,
                    "scale": features.scale,
                    "rms_energy": features.rms_energy,
                    "spectral_centroid": features.spectral_centroid,
                    "duration": features.duration,
                },
                "messages": [],
                "errors": [],
            }
            result = tagging_agent(state)
            return result.get("tags", {})
        except Exception as exc:
            logger.error("tag_audio failed for %s: %s", file_path, exc)
            return {"error": str(exc)}

    # ── Tool: build_sample_pack ──────────────────────────────────────────────

    @mcp.tool()
    def build_sample_pack(
        folder_path: str,
        pack_name: str = "My Pack",
        max_files: int = 50,
    ) -> Dict[str, Any]:
        """
        Analyze a folder of samples and generate a structured pack manifest.

        Processes each audio file in the folder (up to max_files) through the
        tagging and pack-builder agents, then returns a unified pack manifest
        with metadata for all samples and suggested folder structure.

        Args:
            folder_path: Path to the folder containing audio files.
            pack_name: Name for the sample pack (used in manifest metadata).
            max_files: Maximum number of files to process (default 50).

        Returns:
            Pack manifest with per-file metadata and overall pack statistics.
        """
        from samplemind.ai.agents.pack_builder_agent import pack_builder_agent
        from samplemind.ai.agents.tagging_agent import tagging_agent
        from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine

        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {"error": f"Directory not found: {folder_path}"}

        audio_exts = {".wav", ".mp3", ".flac", ".aiff", ".ogg"}
        files = [f for f in folder.rglob("*") if f.suffix.lower() in audio_exts][
            :max_files
        ]

        engine = AudioEngine()
        manifests = []
        errors = []

        for audio_file in files:
            try:
                features = engine.analyze_file(
                    str(audio_file), level=AnalysisLevel.STANDARD
                )
                state = {
                    "file_path": str(audio_file),
                    "audio_features": {
                        "bpm": features.bpm,
                        "key": features.key,
                        "scale": features.scale,
                        "rms_energy": features.rms_energy,
                        "spectral_centroid": features.spectral_centroid,
                        "duration": features.duration,
                    },
                    "messages": [],
                    "errors": [],
                }
                state = tagging_agent(state)
                state = pack_builder_agent(state)
                manifests.append(state.get("pack_manifest", {}))
            except Exception as exc:
                errors.append({"file": str(audio_file), "error": str(exc)})

        return {
            "pack_name": pack_name,
            "folder": folder_path,
            "total_files": len(files),
            "processed": len(manifests),
            "errors": errors,
            "samples": manifests,
        }

    # ── Expose app object ─────────────────────────────────────────────────────
    mcp_app = mcp.get_asgi_app()

else:
    # Stub when FastMCP is not installed
    class _StubApp:
        async def __call__(self, scope, receive, send):
            from fastapi.responses import JSONResponse

            resp = JSONResponse(
                {"error": "FastMCP not installed. Run: pip install fastmcp"},
                status_code=503,
            )
            await resp(scope, receive, send)

    mcp_app = _StubApp()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp_app, host="0.0.0.0", port=8001, log_level="info")
