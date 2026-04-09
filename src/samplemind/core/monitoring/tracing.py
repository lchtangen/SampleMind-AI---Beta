"""
OpenTelemetry distributed tracing for SampleMind v3.0 (Step 22).

Instruments:
  - FastAPI (HTTP spans)
  - LangGraph agent pipeline (custom spans per agent node)
  - AI provider calls (Anthropic, Gemini, OpenAI, Ollama)
  - Redis cache operations

Start tracing by calling `setup_tracing()` in the FastAPI lifespan or
at the top of main.py before any imports that create connections.

Export destinations (configured via env vars):
  - OTEL_EXPORTER_OTLP_ENDPOINT  → OTLP/gRPC (Grafana Tempo, Jaeger, etc.)
  - SENTRY_DSN                   → Sentry (if sentry-sdk[opentelemetry] installed)

Grafana Tempo dashboard:
  Add a Tempo datasource pointing to http://tempo:4317 and query by trace_id.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional

logger = logging.getLogger(__name__)

# ── OpenTelemetry availability ─────────────────────────────────────────────────

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    trace = None  # type: ignore[assignment]

_tracer: Optional[object] = None


def setup_tracing(
    service_name: str = "samplemind-api",
    service_version: str = "3.0.0",
    otlp_endpoint: Optional[str] = None,
) -> bool:
    """
    Initialize OpenTelemetry tracing.

    Args:
        service_name: Logical service name (appears in Grafana/Jaeger).
        service_version: Service version string.
        otlp_endpoint: OTLP gRPC endpoint (e.g. "http://localhost:4317").
                       Falls back to OTEL_EXPORTER_OTLP_ENDPOINT env var.
                       If neither is set, logs spans to console (dev mode).

    Returns:
        True if tracing was configured successfully, False otherwise.
    """
    global _tracer

    if not _OTEL_AVAILABLE:
        logger.warning(
            "OpenTelemetry SDK not installed — tracing disabled. "
            "Install with: pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc"
        )
        return False

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        }
    )

    provider = TracerProvider(resource=resource)

    # ── OTLP exporter (Grafana Tempo, Jaeger, etc.) ───────────────────────────
    endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("OpenTelemetry → OTLP endpoint: %s", endpoint)
        except ImportError:
            logger.warning(
                "opentelemetry-exporter-otlp-proto-grpc not installed. "
                "Run: pip install opentelemetry-exporter-otlp-proto-grpc"
            )
    else:
        # Dev fallback: log spans to console at DEBUG level
        if os.getenv("OTEL_CONSOLE_EXPORTER", "false").lower() == "true":
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
            logger.info("OpenTelemetry → console (dev mode)")

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name, service_version)

    # ── FastAPI auto-instrumentation ──────────────────────────────────────────
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor().instrument()
        logger.info("FastAPI auto-instrumented with OpenTelemetry")
    except ImportError:
        logger.debug("FastAPI OTel instrumentation not installed")

    # ── Redis auto-instrumentation ────────────────────────────────────────────
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
        logger.info("Redis auto-instrumented with OpenTelemetry")
    except ImportError:
        logger.debug("Redis OTel instrumentation not installed")

    # ── Sentry integration ────────────────────────────────────────────────────
    _setup_sentry()

    logger.info("OpenTelemetry tracing initialized for service=%s", service_name)
    return True


def _setup_sentry() -> None:
    """Configure Sentry if DSN is present in environment."""
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            release=f"samplemind@3.0.0",
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(level=logging.WARNING),
            ],
            send_default_pii=False,
        )
        logger.info("Sentry initialized (DSN configured)")
    except ImportError:
        logger.warning(
            "SENTRY_DSN set but sentry-sdk not installed. "
            "Run: pip install sentry-sdk[fastapi]"
        )
    except Exception as exc:
        logger.error("Sentry initialization failed: %s", exc)


# ── Manual span helpers ───────────────────────────────────────────────────────


@contextmanager
def agent_span(
    agent_name: str,
    file_path: str = "",
    session_id: str = "",
) -> Generator[None, None, None]:
    """
    Context manager that wraps a LangGraph agent node execution in a span.

    Usage (inside any agent node)::

        from samplemind.core.monitoring.tracing import agent_span

        def my_agent(state):
            with agent_span("my_agent", file_path=state.get("file_path", "")):
                ...  # agent logic here
    """
    if not _OTEL_AVAILABLE or _tracer is None:
        yield
        return

    with _tracer.start_as_current_span(  # type: ignore[union-attr]
        f"agent.{agent_name}",
        attributes={
            "agent.name": agent_name,
            "audio.file_path": file_path,
            "session.id": session_id,
        },
    ):
        yield


@contextmanager
def ai_provider_span(
    provider: str,
    model: str,
    analysis_type: str = "",
) -> Generator[None, None, None]:
    """
    Wrap an AI provider API call in a span for latency + token tracking.

    Usage::

        with ai_provider_span("anthropic", "claude-sonnet-4-6", "comprehensive"):
            result = await client.messages.create(...)
    """
    if not _OTEL_AVAILABLE or _tracer is None:
        yield
        return

    with _tracer.start_as_current_span(  # type: ignore[union-attr]
        f"ai.{provider}.call",
        attributes={
            "ai.provider": provider,
            "ai.model": model,
            "ai.analysis_type": analysis_type,
        },
    ):
        yield


def record_analysis_metric(
    analysis_type: str,
    duration_s: float,
    tokens: int = 0,
    provider: str = "",
    success: bool = True,
) -> None:
    """
    Record a custom metric span for an analysis run.

    Emits a span named `samplemind.analysis` with relevant attributes
    that Grafana Tempo / Prometheus can query.
    """
    if not _OTEL_AVAILABLE or _tracer is None:
        return

    with _tracer.start_as_current_span(  # type: ignore[union-attr]
        "samplemind.analysis",
        attributes={
            "analysis.type": analysis_type,
            "analysis.duration_s": round(duration_s, 3),
            "analysis.tokens": tokens,
            "analysis.provider": provider,
            "analysis.success": success,
        },
    ) as span:
        if not success:
            span.set_status(trace.StatusCode.ERROR)  # type: ignore[union-attr]
