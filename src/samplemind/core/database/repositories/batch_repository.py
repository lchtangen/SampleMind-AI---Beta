"""Batch job repository"""

from datetime import datetime
from typing import Any

from samplemind.core.database.mongo import BatchJob


class BatchRepository:
    """Repository for batch job CRUD operations"""

    @staticmethod
    async def create(
        batch_id: str,
        total_files: int,
        file_ids: list[str],
        user_id: str | None = None,
    ) -> BatchJob:
        """Create new batch job"""
        batch = BatchJob(
            batch_id=batch_id,
            user_id=user_id,
            status="pending",
            total_files=total_files,
            file_ids=file_ids,
        )
        await batch.insert()
        return batch

    @staticmethod
    async def get_by_id(batch_id: str) -> BatchJob | None:
        """Get batch job by ID"""
        return await BatchJob.find_one(BatchJob.batch_id == batch_id)

    @staticmethod
    async def update_status(
        batch_id: str,
        status: str,
        completed: int = 0,
        failed: int = 0,
        results: dict[str, Any] | None = None,
    ) -> BatchJob | None:
        """Update batch job status"""
        batch = await BatchJob.find_one(BatchJob.batch_id == batch_id)
        if batch:
            batch.status = status
            batch.completed = completed
            batch.failed = failed
            if results:
                batch.results = results
            batch.updated_at = datetime.utcnow()
            await batch.save()
        return batch

    @staticmethod
    async def get_by_user(
        user_id: str, skip: int = 0, limit: int = 50
    ) -> list[BatchJob]:
        """Get all batch jobs for a user"""
        return (
            await BatchJob.find(BatchJob.user_id == user_id)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def delete(batch_id: str) -> bool:
        """Delete batch job"""
        batch = await BatchJob.find_one(BatchJob.batch_id == batch_id)
        if batch:
            await batch.delete()
            return True
        return False
