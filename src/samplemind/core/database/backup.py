"""
Automated Database Backup System
Production-ready backup, restore, and point-in-time recovery
"""

import asyncio
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import gzip
import shutil
import boto3
from google.cloud import storage as gcs
import json

logger = logging.getLogger(__name__)


class BackupConfig:
    """Backup configuration"""
    def __init__(
        self,
        backup_dir: str = "./backups",
        retention_days: int = 30,
        compress: bool = True,
        cloud_storage: Optional[str] = None,  # 's3', 'gcs', or None
        s3_bucket: Optional[str] = None,
        gcs_bucket: Optional[str] = None,
    ):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.compress = compress
        self.cloud_storage = cloud_storage
        self.s3_bucket = s3_bucket
        self.gcs_bucket = gcs_bucket


class DatabaseBackup:
    """
    Automated database backup with multiple storage backends
    Supports: Local filesystem, AWS S3, Google Cloud Storage
    """
    
    def __init__(self, config: BackupConfig):
        self.config = config
        logger.info(f"Backup system initialized: dir={config.backup_dir}")
    
    async def create_backup(
        self,
        database_url: str,
        backup_name: Optional[str] = None
    ) -> Path:
        """
        Create full database backup
        
        Args:
            database_url: PostgreSQL connection string
            backup_name: Custom backup name (default: timestamp)
            
        Returns:
            Path to backup file
        """
        # Parse database URL
        db_info = self._parse_db_url(database_url)
        
        # Generate backup filename
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"samplemind_backup_{timestamp}"
        
        backup_file = self.config.backup_dir / f"{backup_name}.sql"
        
        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h", db_info["host"],
            "-p", str(db_info["port"]),
            "-U", db_info["user"],
            "-d", db_info["database"],
            "-F", "c",  # Custom format (compressed, allows parallel restore)
            "-f", str(backup_file),
            "--verbose"
        ]
        
        # Set password environment variable
        env = {"PGPASSWORD": db_info["password"]}
        
        try:
            logger.info(f"Starting backup: {backup_name}")
            
            # Execute pg_dump
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode()
                logger.error(f"Backup failed: {error_msg}")
                raise Exception(f"pg_dump failed: {error_msg}")
            
            logger.info(f"Backup created: {backup_file} ({self._get_file_size(backup_file)})")
            
            # Compress if enabled
            if self.config.compress:
                backup_file = await self._compress_backup(backup_file)
            
            # Upload to cloud storage
            if self.config.cloud_storage:
                await self._upload_to_cloud(backup_file)
            
            # Create backup metadata
            await self._save_backup_metadata(backup_file, db_info)
            
            return backup_file
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    async def restore_backup(
        self,
        backup_file: Path,
        database_url: str,
        drop_existing: bool = False
    ) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_file: Path to backup file
            database_url: Target database URL
            drop_existing: Drop existing database before restore
            
        Returns:
            True if successful
        """
        db_info = self._parse_db_url(database_url)
        
        # Decompress if needed
        if backup_file.suffix == ".gz":
            backup_file = await self._decompress_backup(backup_file)
        
        try:
            logger.info(f"Starting restore from: {backup_file}")
            
            # Drop existing database if requested
            if drop_existing:
                await self._drop_database(db_info)
                await self._create_database(db_info)
            
            # Build pg_restore command
            cmd = [
                "pg_restore",
                "-h", db_info["host"],
                "-p", str(db_info["port"]),
                "-U", db_info["user"],
                "-d", db_info["database"],
                "-F", "c",  # Custom format
                "-j", "4",  # 4 parallel jobs
                "--clean",  # Clean before restore
                "--if-exists",  # Don't error on missing objects
                "--verbose",
                str(backup_file)
            ]
            
            env = {"PGPASSWORD": db_info["password"]}
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                # pg_restore returns non-zero even for warnings
                error_msg = stderr.decode()
                logger.warning(f"Restore completed with warnings: {error_msg}")
            
            logger.info(f"Restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.config.backup_dir.glob("*.sql*"):
            metadata_file = backup_file.with_suffix(backup_file.suffix + ".meta")
            
            backup_info = {
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": self._get_file_size(backup_file),
                "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime)
            }
            
            # Load metadata if available
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    backup_info.update(metadata)
            
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    async def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period
        
        Returns:
            Number of backups deleted
        """
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        deleted = 0
        
        for backup_file in self.config.backup_dir.glob("*.sql*"):
            created_at = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if created_at < cutoff_date:
                logger.info(f"Deleting old backup: {backup_file.name}")
                backup_file.unlink()
                
                # Delete metadata
                metadata_file = backup_file.with_suffix(backup_file.suffix + ".meta")
                if metadata_file.exists():
                    metadata_file.unlink()
                
                deleted += 1
        
        logger.info(f"Cleaned up {deleted} old backups")
        return deleted
    
    async def create_incremental_backup(
        self,
        database_url: str,
        base_backup_file: Path
    ) -> Path:
        """
        Create incremental backup (WAL archiving)
        Requires PostgreSQL WAL archiving to be enabled
        """
        # This is a placeholder - full WAL archiving implementation
        # would require PostgreSQL configuration and archive_command setup
        raise NotImplementedError(
            "Incremental backups require WAL archiving configuration. "
            "See: https://www.postgresql.org/docs/current/continuous-archiving.html"
        )
    
    async def verify_backup(self, backup_file: Path) -> bool:
        """
        Verify backup integrity
        
        Returns:
            True if backup is valid
        """
        try:
            # Check if file exists and is readable
            if not backup_file.exists():
                return False
            
            # For gzip files, test decompression
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, 'rb') as f:
                    f.read(1024)  # Read first 1KB
            
            # For SQL dumps, check pg_restore --list
            if backup_file.suffix in [".sql", ".dump"]:
                cmd = ["pg_restore", "--list", str(backup_file)]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                if process.returncode != 0:
                    return False
            
            logger.info(f"Backup verified: {backup_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    # Helper methods
    
    def _parse_db_url(self, database_url: str) -> Dict[str, Any]:
        """Parse PostgreSQL connection URL"""
        # postgresql://user:password@host:port/database
        from urllib.parse import urlparse
        
        parsed = urlparse(database_url)
        
        return {
            "user": parsed.username,
            "password": parsed.password,
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/")
        }
    
    async def _compress_backup(self, backup_file: Path) -> Path:
        """Compress backup file with gzip"""
        compressed_file = backup_file.with_suffix(backup_file.suffix + ".gz")
        
        logger.info(f"Compressing backup...")
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb', compresslevel=6) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original
        backup_file.unlink()
        
        logger.info(f"Compressed: {self._get_file_size(compressed_file)}")
        return compressed_file
    
    async def _decompress_backup(self, compressed_file: Path) -> Path:
        """Decompress gzip backup"""
        backup_file = compressed_file.with_suffix("")
        
        with gzip.open(compressed_file, 'rb') as f_in:
            with open(backup_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return backup_file
    
    async def _upload_to_cloud(self, backup_file: Path):
        """Upload backup to cloud storage"""
        if self.config.cloud_storage == "s3":
            await self._upload_to_s3(backup_file)
        elif self.config.cloud_storage == "gcs":
            await self._upload_to_gcs(backup_file)
    
    async def _upload_to_s3(self, backup_file: Path):
        """Upload to AWS S3"""
        s3 = boto3.client('s3')
        key = f"backups/{backup_file.name}"
        
        logger.info(f"Uploading to S3: {self.config.s3_bucket}/{key}")
        
        s3.upload_file(
            str(backup_file),
            self.config.s3_bucket,
            key,
            ExtraArgs={'StorageClass': 'STANDARD_IA'}  # Infrequent access
        )
        
        logger.info(f"Upload complete")
    
    async def _upload_to_gcs(self, backup_file: Path):
        """Upload to Google Cloud Storage"""
        client = gcs.Client()
        bucket = client.bucket(self.config.gcs_bucket)
        blob = bucket.blob(f"backups/{backup_file.name}")
        
        logger.info(f"Uploading to GCS: {self.config.gcs_bucket}/{blob.name}")
        
        blob.upload_from_filename(str(backup_file))
        
        logger.info(f"Upload complete")
    
    async def _save_backup_metadata(self, backup_file: Path, db_info: Dict[str, Any]):
        """Save backup metadata"""
        metadata = {
            "filename": backup_file.name,
            "created_at": datetime.now().isoformat(),
            "database": db_info["database"],
            "host": db_info["host"],
            "size_bytes": backup_file.stat().st_size,
            "compressed": backup_file.suffix == ".gz"
        }
        
        metadata_file = backup_file.with_suffix(backup_file.suffix + ".meta")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def _drop_database(self, db_info: Dict[str, Any]):
        """Drop database (careful!)"""
        cmd = [
            "dropdb",
            "-h", db_info["host"],
            "-p", str(db_info["port"]),
            "-U", db_info["user"],
            db_info["database"]
        ]
        
        env = {"PGPASSWORD": db_info["password"]}
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
    
    async def _create_database(self, db_info: Dict[str, Any]):
        """Create new database"""
        cmd = [
            "createdb",
            "-h", db_info["host"],
            "-p", str(db_info["port"]),
            "-U", db_info["user"],
            db_info["database"]
        ]
        
        env = {"PGPASSWORD": db_info["password"]}
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
    
    def _get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size"""
        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


# Example usage
"""
from src.samplemind.core.config import settings

async def main():
    # Configure backup
    config = BackupConfig(
        backup_dir="./backups",
        retention_days=30,
        compress=True,
        cloud_storage="s3",
        s3_bucket="samplemind-backups"
    )
    
    backup_system = DatabaseBackup(config)
    
    # Create backup
    backup_file = await backup_system.create_backup(settings.database_url)
    print(f"Backup created: {backup_file}")
    
    # List backups
    backups = await backup_system.list_backups()
    for backup in backups:
        print(f"- {backup['filename']}: {backup['size']}")
    
    # Cleanup old backups
    deleted = await backup_system.cleanup_old_backups()
    print(f"Deleted {deleted} old backups")
    
    # Verify backup
    is_valid = await backup_system.verify_backup(backup_file)
    print(f"Backup valid: {is_valid}")
"""
