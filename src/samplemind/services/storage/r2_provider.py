"""
Cloudflare R2 Storage Provider — SampleMind Phase 13

R2 is S3-compatible, so we use boto3 with a custom endpoint URL.
Extends the existing StorageProvider ABC with CDN public URL support.

Configuration (env vars):
    R2_ACCOUNT_ID         — Cloudflare account ID
    R2_ACCESS_KEY_ID      — R2 API token access key
    R2_SECRET_ACCESS_KEY  — R2 API token secret
    R2_BUCKET             — R2 bucket name (e.g. samplemind-audio)
    R2_PUBLIC_URL         — Optional: custom domain / public bucket URL
                            (e.g. https://audio.samplemind.ai)

Usage::

    from samplemind.services.storage.r2_provider import R2StorageProvider

    provider = R2StorageProvider()
    key = await provider.upload_file("/path/to/kick.wav", "audio/kick.wav")
    url = provider.get_public_url(key)
    await provider.download_file(key, "/tmp/kick.wav")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class R2StorageProvider:
    """
    Cloudflare R2 storage using boto3 S3-compatible API.

    Auto-creates a signed URL (1h TTL) when a public bucket URL is not set.
    Set R2_PUBLIC_URL to a custom domain for permanent public CDN URLs.
    """

    def __init__(
        self,
        account_id: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        bucket: str | None = None,
        public_url: str | None = None,
    ) -> None:
        self.account_id = account_id or os.getenv("R2_ACCOUNT_ID", "")
        self.access_key_id = access_key_id or os.getenv("R2_ACCESS_KEY_ID", "")
        self.secret_access_key = secret_access_key or os.getenv(
            "R2_SECRET_ACCESS_KEY", ""
        )
        self.bucket = bucket or os.getenv("R2_BUCKET", "samplemind-audio")
        self.public_url = (public_url or os.getenv("R2_PUBLIC_URL", "")).rstrip("/")
        self._client: object | None = None

    @property
    def endpoint_url(self) -> str:
        return f"https://{self.account_id}.r2.cloudflarestorage.com"

    @property
    def available(self) -> bool:
        return bool(self.account_id and self.access_key_id and self.secret_access_key)

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client

        if not self.available:
            raise RuntimeError(
                "R2 not configured. Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY."
            )

        try:
            import boto3

            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name="auto",
            )
            logger.info("✓ R2 client initialized (bucket: %s)", self.bucket)
            return self._client
        except ImportError:
            raise RuntimeError("boto3 not installed — run: uv add boto3")

    async def upload_file(
        self,
        local_path: str,
        object_key: str,
        content_type: str | None = None,
        public: bool = False,
    ) -> str:
        """
        Upload a file to R2.

        Args:
            local_path: Local filesystem path to upload.
            object_key: R2 object key (path within bucket).
            content_type: MIME type (auto-detected from extension if None).
            public: If True, sets object ACL to public-read.

        Returns:
            The object key (use get_public_url() to get the download URL).
        """
        import asyncio

        if not self.available:
            logger.warning("R2 not configured — upload skipped: %s", object_key)
            return object_key

        client = self._get_client()
        ct = content_type or _guess_content_type(local_path)
        extra: dict = {"ContentType": ct}
        if public:
            extra["ACL"] = "public-read"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.upload_file(  # type: ignore[union-attr]
                local_path,
                self.bucket,
                object_key,
                ExtraArgs=extra,
            ),
        )
        logger.info("✓ R2 upload: %s → s3://%s/%s", local_path, self.bucket, object_key)
        return object_key

    async def download_file(self, object_key: str, local_path: str) -> bool:
        """
        Download a file from R2 to the local filesystem.

        Returns:
            True if successful, False on error.
        """
        import asyncio

        if not self.available:
            return False

        try:
            client = self._get_client()
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.download_file(self.bucket, object_key, local_path),  # type: ignore[union-attr]
            )
            return True
        except Exception as exc:
            logger.error("R2 download failed (%s): %s", object_key, exc)
            return False

    async def delete_file(self, object_key: str) -> bool:
        """Delete an object from R2."""
        import asyncio

        if not self.available:
            return False
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.delete_object(Bucket=self.bucket, Key=object_key),  # type: ignore[union-attr]
            )
            return True
        except Exception as exc:
            logger.error("R2 delete failed (%s): %s", object_key, exc)
            return False

    def get_public_url(self, object_key: str) -> str:
        """
        Get the public download URL for an object.

        Uses R2_PUBLIC_URL custom domain if set, otherwise generates a
        24-hour pre-signed URL.
        """
        if self.public_url:
            return f"{self.public_url}/{object_key}"
        return self.get_presigned_url(object_key, expires_in=86400)

    def get_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed download URL with a TTL.

        Args:
            object_key: R2 object key.
            expires_in: URL validity in seconds (default: 1 hour).

        Returns:
            Pre-signed URL string.
        """
        if not self.available:
            return ""
        try:
            client = self._get_client()
            url = client.generate_presigned_url(  # type: ignore[union-attr]
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as exc:
            logger.error("Presigned URL generation failed (%s): %s", object_key, exc)
            return ""

    async def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        List objects in the bucket with an optional prefix filter.

        Returns:
            List of dicts with keys: key, size, last_modified.
        """
        import asyncio

        if not self.available:
            return []
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.list_objects_v2(  # type: ignore[union-attr]
                    Bucket=self.bucket,
                    Prefix=prefix,
                    MaxKeys=max_keys,
                ),
            )
            return [
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                }
                for obj in response.get("Contents", [])
            ]
        except Exception as exc:
            logger.error("R2 list failed: %s", exc)
            return []

    async def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in the bucket."""
        import asyncio

        if not self.available:
            return False
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.head_object(Bucket=self.bucket, Key=object_key),  # type: ignore[union-attr]
            )
            return True
        except Exception:
            return False


def _guess_content_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".flac": "audio/flac",
        ".aiff": "audio/aiff",
        ".aif": "audio/aiff",
        ".ogg": "audio/ogg",
        ".smpack": "application/zip",
        ".json": "application/json",
        ".zip": "application/zip",
    }
    return types.get(ext, "application/octet-stream")


# ── Module-level singleton ────────────────────────────────────────────────────

_r2: R2StorageProvider | None = None


def get_r2() -> R2StorageProvider:
    """Return the R2 provider singleton."""
    global _r2
    if _r2 is None:
        _r2 = R2StorageProvider()
    return _r2
