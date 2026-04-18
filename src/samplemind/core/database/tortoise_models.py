"""
Tortoise ORM Models — SampleMind v0.3.0
=========================================

Async-first relational models for Phases 11–16.  Runs on **SQLite** in
development and **PostgreSQL** in production.  Migrations are managed by
**aerich** (``aerich upgrade``).

Coexistence:
  These models run alongside the legacy Beanie/MongoDB layer.  New features
  should use Tortoise; MongoDB will be phased out once migration is complete.

Models:
  ``TortoiseUser``            — user account (auth, billing, quotas).
  ``TortoiseLibrary``         — named sample collection owned by a user.
  ``TortoiseSample``          — audio sample with features, FAISS pointer, R2 key.
  ``TortoiseAnalysisResult``  — persisted analysis output for a sample.
  ``TortoisePack``            — sample pack (.smpack) for the marketplace.
  ``TortoisePlaylist``        — AI-curated playlist (Phase 12 curation engine).

Configuration:
  The ``TORTOISE_ORM`` dict at the bottom of this file is consumed by both
  ``aerich`` and ``init_tortoise()`` at FastAPI startup.

Usage::

    from samplemind.core.database.tortoise_models import TortoiseSample, init_tortoise

    await init_tortoise()
    sample = await TortoiseSample.create(filename="kick.wav", bpm=140.0, key="Am")
"""

from __future__ import annotations

import os

from tortoise import fields
from tortoise.models import Model

# ── Core domain models ────────────────────────────────────────────────────────
# Each model maps 1:1 to a ``*_v3`` table (the "v3" suffix avoids collisions
# with legacy MongoDB-era tables).


class TortoiseUser(Model):
    """User account — mirrors the UserInDB Pydantic schema used by FastAPI auth."""

    id = fields.CharField(max_length=100, pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    username = fields.CharField(max_length=100, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)

    role = fields.CharField(max_length=50, default="free", index=True)
    tier = fields.CharField(max_length=50, default="free")
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)

    # Usage tracking
    total_uploads = fields.IntField(default=0)
    storage_used_mb = fields.FloatField(default=0.0)
    api_calls_today = fields.IntField(default=0)
    api_calls_this_month = fields.IntField(default=0)

    # Billing
    stripe_customer_id = fields.CharField(max_length=255, null=True)
    supabase_user_id = fields.CharField(max_length=255, null=True, index=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login = fields.DatetimeField(null=True)

    # Reverse relations
    samples: fields.ReverseRelation[TortoiseSample]
    libraries: fields.ReverseRelation[TortoiseLibrary]

    class Meta:
        table = "users_v3"
        indexes = [("role", "is_active"), ("tier",)]  # compound indexes for common filters

    def __str__(self) -> str:
        return f"User({self.id}, {self.email})"


class TortoiseLibrary(Model):
    """Sample library — a named folder/collection owned by a user.

    ``sample_count`` and ``total_size_mb`` are denormalized for dashboard
    queries; they must be updated when samples are added/removed.
    """

    id = fields.CharField(max_length=100, pk=True)
    user: fields.ForeignKeyRelation[TortoiseUser] = fields.ForeignKeyField(
        "models.TortoiseUser", related_name="libraries", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=255)
    path = fields.CharField(max_length=1024)
    description = fields.TextField(default="")
    is_active = fields.BooleanField(default=True)

    # Stats (denormalized for fast queries)
    sample_count = fields.IntField(default=0)
    total_size_mb = fields.FloatField(default=0.0)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    samples: fields.ReverseRelation[TortoiseSample]

    class Meta:
        table = "libraries_v3"

    def __str__(self) -> str:
        return f"Library({self.name})"


class TortoiseSample(Model):
    """
    Audio sample with extracted features.

    Central table for Phase 11 (FAISS search) and Phase 12 (AI curation).
    The ``embedding_id`` links to the FAISS index for similarity search.
    ``r2_key`` / ``r2_public_url`` link to Cloudflare R2 cloud storage (Phase 13).
    """

    id = fields.CharField(max_length=100, pk=True)
    user: fields.ForeignKeyRelation[TortoiseUser] = fields.ForeignKeyField(
        "models.TortoiseUser", related_name="samples", on_delete=fields.CASCADE
    )
    library: fields.ForeignKeyRelation[TortoiseLibrary] = fields.ForeignKeyField(
        "models.TortoiseLibrary", related_name="samples", on_delete=fields.CASCADE
    )

    # File metadata
    filename = fields.CharField(max_length=512)
    file_path = fields.CharField(max_length=1024)
    file_size_bytes = fields.IntField(default=0)
    duration_s = fields.FloatField(default=0.0)
    sample_rate = fields.IntField(default=44100)
    channels = fields.IntField(default=2)
    format = fields.CharField(max_length=20, default="wav")

    # Audio features (from AudioEngine)
    bpm = fields.FloatField(null=True)
    key = fields.CharField(max_length=10, null=True)  # e.g. "Am", "C"
    camelot_key = fields.CharField(max_length=5, null=True)  # e.g. "8A"
    energy = fields.CharField(max_length=10, null=True)  # low/mid/high
    loudness_lufs = fields.FloatField(null=True)
    spectral_centroid = fields.FloatField(null=True)
    zero_crossing_rate = fields.FloatField(null=True)

    # AI classification (from ensemble, mood_detector, instrument_detector)
    genre_labels = fields.JSONField(default=list)  # e.g. ["trap", "dark", "hip-hop"]
    mood_labels = fields.JSONField(default=list)  # e.g. ["dark", "aggressive"]
    instrument_labels = fields.JSONField(default=list)  # e.g. ["kick", "808"]
    valence = fields.FloatField(null=True)  # Russell circumplex x-axis: -1..1
    arousal = fields.FloatField(null=True)  # Russell circumplex y-axis: -1..1

    # Fingerprint (from AudioFingerprinter)
    fingerprint_hash = fields.CharField(max_length=64, null=True, index=True)

    # FAISS index pointer (Phase 11)
    embedding_id = fields.IntField(null=True, index=True)

    # Cloudflare R2 storage (Phase 13)
    r2_key = fields.CharField(max_length=512, null=True)
    r2_public_url = fields.CharField(max_length=1024, null=True)

    # Tagging
    user_tags = fields.JSONField(default=list)
    auto_tags = fields.JSONField(default=list)

    # Processing status
    processing_status = fields.CharField(max_length=50, default="pending")

    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "samples_v3"
        indexes = [
            ("user_id", "created_at"),  # "my recent uploads" queries
            ("library_id", "bpm"),  # library browsing filtered by BPM
            ("key", "energy"),  # curation engine key+energy lookups
            ("fingerprint_hash",),  # duplicate detection
        ]

    def __str__(self) -> str:
        return f"Sample({self.filename}, bpm={self.bpm}, key={self.key})"


# ── Analysis results ──────────────────────────────────────────────────────────


class TortoiseAnalysisResult(Model):
    """Persisted analysis output — one row per (sample, analysis_type) pair."""

    id = fields.CharField(max_length=100, pk=True)
    sample: fields.ForeignKeyRelation[TortoiseSample] = fields.ForeignKeyField(
        "models.TortoiseSample",
        related_name="analysis_results",
        on_delete=fields.CASCADE,
    )

    analysis_type = fields.CharField(max_length=100, index=True)
    results = fields.JSONField(default=dict)
    model_version = fields.CharField(max_length=50, null=True)
    processing_time_ms = fields.FloatField(null=True)
    status = fields.CharField(max_length=50, default="completed")
    error = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "analysis_results_v3"


# ── Marketplace models ────────────────────────────────────────────────────────


class TortoisePack(Model):
    """
    Sample pack — a curated collection for distribution (.smpack format).
    Used in Phase 15 marketplace.
    """

    id = fields.CharField(max_length=100, pk=True)
    creator: fields.ForeignKeyRelation[TortoiseUser] = fields.ForeignKeyField(
        "models.TortoiseUser", related_name="created_packs", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=255)
    version = fields.CharField(max_length=20, default="1.0.0")
    description = fields.TextField(default="")
    tags = fields.JSONField(default=list)

    # Pack file
    smpack_path = fields.CharField(max_length=1024, null=True)
    r2_key = fields.CharField(max_length=512, null=True)
    r2_public_url = fields.CharField(max_length=1024, null=True)
    file_size_bytes = fields.IntField(default=0)

    # Marketplace
    is_published = fields.BooleanField(default=False, index=True)
    price_usd = fields.FloatField(null=True)
    stripe_price_id = fields.CharField(max_length=255, null=True)
    stripe_product_id = fields.CharField(max_length=255, null=True)
    stripe_account_id = fields.CharField(max_length=255, null=True)  # Connect

    # Stats
    download_count = fields.IntField(default=0)
    purchase_count = fields.IntField(default=0)

    # Samples in this pack (many-to-many)
    samples: fields.ManyToManyRelation[TortoiseSample] = fields.ManyToManyField(
        "models.TortoiseSample", related_name="packs", through="pack_samples_v3"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "packs_v3"

    def __str__(self) -> str:
        return f"Pack({self.name} v{self.version})"


# ── AI curation models ────────────────────────────────────────────────────────


class TortoisePlaylist(Model):
    """AI-curated playlist — output of Phase 12 curation engine."""

    id = fields.CharField(max_length=100, pk=True)
    user: fields.ForeignKeyRelation[TortoiseUser] = fields.ForeignKeyField(
        "models.TortoiseUser", related_name="playlists", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=255)
    mood = fields.CharField(max_length=50, null=True)
    energy_arc = fields.CharField(max_length=50, null=True)  # build/drop/plateau
    duration_s = fields.FloatField(default=0.0)
    description = fields.TextField(default="")

    # Ordered sample IDs
    ordered_sample_ids = fields.JSONField(default=list)

    # AI metadata
    generation_prompt = fields.TextField(null=True)
    model_used = fields.CharField(max_length=100, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "playlists_v3"


# ── Tortoise ORM config ───────────────────────────────────────────────────────
# Used by:
#   - aerich CLI for migration generation (``aerich.ini`` points here)
#   - ``init_tortoise()`` at FastAPI lifespan startup

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    },
    "apps": {
        "models": {
            "models": [
                "samplemind.core.database.tortoise_models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


# ── Lifecycle helpers ─────────────────────────────────────────────────────────


async def init_tortoise(db_url: str | None = None) -> None:
    """
    Initialize Tortoise ORM.

    Call during FastAPI lifespan startup before any DB queries.

    Args:
        db_url: Database URL (sqlite:///path, postgres://...).
                Defaults to DATABASE_URL env var, fallback to SQLite dev default.
    """
    from tortoise import Tortoise

    url = db_url or os.getenv("DATABASE_URL", "sqlite://db.sqlite3")

    await Tortoise.init(
        db_url=url,
        modules={
            "models": [
                "samplemind.core.database.tortoise_models",
                "aerich.models",
            ]
        },
    )
    await Tortoise.generate_schemas(safe=True)


async def close_tortoise() -> None:
    """Close all Tortoise ORM connections. Call on FastAPI shutdown."""
    from tortoise import Tortoise

    await Tortoise.close_connections()
