"""
Storage Service
Handles file operations across different storage providers (Local, Cloud, etc.)
"""

import abc
import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import BinaryIO, List, Optional, TypedDict, Union

logger = logging.getLogger(__name__)

class FileMetadata(TypedDict):
    """Metadata for a stored file"""
    size: int
    mtime: float
    hash: Optional[str] = None

class StorageProvider(abc.ABC):
    """Abstract base class for storage providers"""

    @abc.abstractmethod
    async def get_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        """Get metadata for a file (size, mtime, hash). Returns None if not found."""
        pass

    @abc.abstractmethod
    async def upload_file(self, content: Union[BinaryIO, bytes, Path], remote_path: str) -> str:
        """Upload file to storage"""
        pass

    @abc.abstractmethod
    async def download_file(self, remote_path: str, local_path: Path) -> bool:
        """Download file from storage"""
        pass

    @abc.abstractmethod
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files in storage"""
        pass

    @abc.abstractmethod
    async def delete_file(self, remote_path: str) -> bool:
        """Delete file from storage"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem 'cloud' storage (for testing/dev)"""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    async def get_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        target_path = self.root_dir / remote_path
        if not target_path.exists() or not target_path.is_file():
            return None

        stat = target_path.stat()
        return FileMetadata(
            size=stat.st_size,
            mtime=stat.st_mtime,
            hash=None  # Hash is expensive, compute only if needed or cached
        )

    async def upload_file(self, content: Union[BinaryIO, bytes, Path], remote_path: str) -> str:
        dest_path = self.root_dir / remote_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, Path) or isinstance(content, str):
            shutil.copy2(content, dest_path)
        elif isinstance(content, bytes):
            with open(dest_path, "wb") as f:
                f.write(content)
        else:
            # BinaryIO
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(content, f)

        logger.info(f"Uploaded to local storage: {remote_path}")
        return str(dest_path)

    async def download_file(self, remote_path: str, local_path: Path) -> bool:
        src_path = self.root_dir / remote_path
        if not src_path.exists():
            return False

        local_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, local_path)
        return True

    async def list_files(self, prefix: str = "") -> List[str]:
        files = []
        search_dir = self.root_dir / prefix
        if not search_dir.exists():
            return []

        for path in search_dir.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(self.root_dir)
                files.append(str(rel_path))
        return files

    async def delete_file(self, remote_path: str) -> bool:
        path = self.root_dir / remote_path
        if path.exists():
            path.unlink()
            return True
        return False


class MockS3StorageProvider(StorageProvider):
    """Mock S3 Provider (Skeleton)"""

    def __init__(self, bucket_name: str, region: str = "us-east-1") -> None:
        self.bucket = bucket_name
        self.region = region
        logger.info(f"Initialized Mock S3 Provider: {bucket_name}")

    async def get_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        # In a real mock, this would check an internal dict
        return None

    async def upload_file(self, content: Union[BinaryIO, bytes, Path], remote_path: str) -> str:
        logger.info(f"[MOCK] Uploading to S3://{self.bucket}/{remote_path}")
        return f"s3://{self.bucket}/{remote_path}"

    async def download_file(self, remote_path: str, local_path: Path) -> bool:
        logger.info(f"[MOCK] Downloading from S3://{self.bucket}/{remote_path}")
        return True

    async def list_files(self, prefix: str = "") -> List[str]:
        return []

    async def delete_file(self, remote_path: str) -> bool:
        logger.info(f"[MOCK] Deleting s3://{self.bucket}/{remote_path}")
        return True


class S3StorageProvider(StorageProvider):
    """
    AWS S3 Storage Provider
    Requires: boto3, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    """

    def __init__(self, bucket_name: str, region: str = "us-east-1") -> None:
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError("boto3 is required for S3 storage. Install it with: pip install boto3")

        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region)
        self.ClientError = ClientError
        logger.info(f"Initialized S3 Provider: {bucket_name} ({region})")

    async def get_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        try:
            response = await asyncio.to_thread(
                self.s3_client.head_object, Bucket=self.bucket_name, Key=remote_path
            )
            return FileMetadata(
                size=response['ContentLength'],
                mtime=response['LastModified'].timestamp(),
                # ETag is often the MD5, but surrounded by quotes
                hash=response.get('ETag', '').strip('"')
            )
        except self.ClientError:
            # 404 or other error -> treat as not found for now
            return None

    async def upload_file(self, content: Union[BinaryIO, bytes, Path], remote_path: str) -> str:
        try:
            if isinstance(content, Path) or isinstance(content, str):
                await asyncio.to_thread(
                    self.s3_client.upload_file, str(content), self.bucket_name, remote_path
                )
            elif isinstance(content, bytes):
                 import io
                 f = io.BytesIO(content)
                 await asyncio.to_thread(
                     self.s3_client.upload_fileobj, f, self.bucket_name, remote_path
                 )
            else:
                 # BinaryIO
                 await asyncio.to_thread(
                     self.s3_client.upload_fileobj, content, self.bucket_name, remote_path
                 )
            return f"s3://{self.bucket_name}/{remote_path}"
        except self.ClientError as e:
            logger.error(f"S3 Upload Error: {e}")
            raise

    async def download_file(self, remote_path: str, local_path: Path) -> bool:
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(
                self.s3_client.download_file, self.bucket_name, remote_path, str(local_path)
            )
            return True
        except self.ClientError as e:
            # 404 check
            if e.response['Error']['Code'] == "404":
                return False
            logger.error(f"S3 Download Error: {e}")
            return False

    async def list_files(self, prefix: str = "") -> List[str]:
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            files = []

            # Use thread for blocking I/O
            def _list():
                for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            files.append(obj['Key'])
                return files

            return await asyncio.to_thread(_list)

        except self.ClientError as e:
            logger.error(f"S3 List Error: {e}")
            return []

    async def delete_file(self, remote_path: str) -> bool:
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object, Bucket=self.bucket_name, Key=remote_path
            )
            return True
        except self.ClientError as e:
            logger.error(f"S3 Delete Error: {e}")
            return False
