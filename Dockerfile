FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
ENV POETRY_CACHE_DIR=/root/.cache/pypoetry
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry config virtualenvs.create false \
    && poetry install --without dev --no-root

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 samplemind
USER samplemind

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "samplemind.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
