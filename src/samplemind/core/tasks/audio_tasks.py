"""
Audio Processing Celery Tasks
Background tasks for audio analysis, batch processing, and embeddings
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from celery import Task, group
from celery.exceptions import SoftTimeLimitExceeded

from .celery_app import celery_app

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for progress tracking"""
    
    def on_success(self, retval: Any, task_id: Any, args: Any, kwargs: Any) -> None:
        """Called when task completes successfully"""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc: Any, task_id: Any, args: Any, kwargs: Any, einfo: Any) -> None:
        """Called when task fails"""
        logger.error(f"Task {task_id} failed: {exc}")
    
    def on_retry(self, exc: Any, task_id: Any, args: Any, kwargs: Any, einfo: Any) -> None:
        """Called when task is retried"""
        logger.warning(f"Task {task_id} retrying: {exc}")


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="samplemind.core.tasks.audio_tasks.process_audio_analysis",
    max_retries=3,
    default_retry_delay=60
)
def process_audio_analysis(
    self,
    file_id: str,
    file_path: str,
    user_id: Optional[str] = None,
    analysis_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process audio file analysis in background
    
    Args:
        file_id: Unique file identifier
        file_path: Path to audio file
        user_id: User who owns the file
        analysis_options: Optional analysis configuration
        
    Returns:
        Analysis results dictionary
    """
    try:
        logger.info(f"Starting audio analysis for file {file_id}")
        
        # Update task state to STARTED
        self.update_state(
            state="STARTED",
            meta={
                "file_id": file_id,
                "progress": 0,
                "status": "Initializing audio analysis..."
            }
        )
        
        # Import here to avoid circular dependencies
        from samplemind.core.engine.audio_engine import AudioEngine
        from samplemind.integrations.ai_manager import SampleMindAIManager
        
        # Initialize components
        audio_engine = AudioEngine()
        ai_manager = SampleMindAIManager()
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={
                "file_id": file_id,
                "progress": 20,
                "status": "Analyzing audio features..."
            }
        )
        
        # Load and analyze audio
        audio_data, sample_rate = audio_engine.load_audio(file_path)
        audio_features = audio_engine.extract_features(audio_data, sample_rate)
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={
                "file_id": file_id,
                "progress": 50,
                "status": "Running AI analysis..."
            }
        )
        
        # Run AI analysis
        analysis_result = asyncio.run(
            ai_manager.analyze_audio_with_ai(
                audio_features=audio_features,
                provider=analysis_options.get("ai_provider") if analysis_options else None
            )
        )
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={
                "file_id": file_id,
                "progress": 80,
                "status": "Saving results..."
            }
        )
        
        # Save to database
        from samplemind.core.database.repositories import AudioRepository, AnalysisRepository
        
        # Create analysis record
        analysis_id = f"analysis_{file_id}_{int(datetime.utcnow().timestamp())}"
        
        asyncio.run(
            AnalysisRepository.create(
                analysis_id=analysis_id,
                file_id=file_id,
                user_id=user_id,
                audio_features=audio_features,
                ai_analysis=analysis_result,
                analyzed_at=datetime.utcnow()
            )
        )
        
        # Update audio file record
        asyncio.run(
            AudioRepository.update(file_id, analysis_id=analysis_id)
        )
        
        # Cleanup
        asyncio.run(ai_manager.close())
        
        logger.info(f"Audio analysis completed for file {file_id}")
        
        return {
            "file_id": file_id,
            "analysis_id": analysis_id,
            "audio_features": audio_features,
            "ai_analysis": analysis_result,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {self.request.id} exceeded time limit")
        raise
        
    except Exception as e:
        logger.exception(f"Error processing audio analysis: {e}")
        
        # Retry the task
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "file_id": file_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="samplemind.core.tasks.audio_tasks.batch_process_audio_files",
)
def batch_process_audio_files(
    self,
    batch_id: str,
    file_infos: List[Dict[str, Any]],
    user_id: Optional[str] = None,
    analysis_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process multiple audio files in parallel
    
    Args:
        batch_id: Unique batch identifier
        file_infos: List of file information dicts
        user_id: User who owns the batch
        analysis_options: Optional analysis configuration
        
    Returns:
        Batch processing results
    """
    try:
        logger.info(f"Starting batch processing for {len(file_infos)} files")
        
        self.update_state(
            state="STARTED",
            meta={
                "batch_id": batch_id,
                "total_files": len(file_infos),
                "processed": 0,
                "status": "Starting batch processing..."
            }
        )
        
        # Create analysis tasks for each file
        job = group(
            process_audio_analysis.s(
                file_id=info["file_id"],
                file_path=info["file_path"],
                user_id=user_id,
                analysis_options=analysis_options
            )
            for info in file_infos
        )
        
        # Execute tasks in parallel
        result = job.apply_async()
        
        # Wait for all tasks to complete
        results = result.get()
        
        # Count successes and failures
        successful = sum(1 for r in results if r.get("status") == "completed")
        failed = len(results) - successful
        
        # Update batch status in database
        from samplemind.core.database.repositories import BatchRepository
        
        asyncio.run(
            BatchRepository.update(
                batch_id,
                status="completed" if failed == 0 else "partial",
                total_files=len(file_infos),
                processed_files=successful,
                failed_files=failed,
                completed_at=datetime.utcnow()
            )
        )
        
        logger.info(f"Batch processing completed: {successful} success, {failed} failed")
        
        return {
            "batch_id": batch_id,
            "total_files": len(file_infos),
            "successful": successful,
            "failed": failed,
            "results": results,
            "status": "completed" if failed == 0 else "partial",
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Error in batch processing: {e}")
        
        # Update batch status to failed
        try:
            asyncio.run(
                BatchRepository.update(
                    batch_id,
                    status="failed",
                    error=str(e)
                )
            )
        except Exception as update_error:
            logger.error(f"Failed to update batch status: {update_error}")
        
        return {
            "batch_id": batch_id,
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="samplemind.core.tasks.audio_tasks.generate_audio_embeddings",
)
def generate_audio_embeddings(
    self,
    file_id: str,
    file_path: str,
    audio_features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate and store audio embeddings for similarity search
    
    Args:
        file_id: Unique file identifier
        file_path: Path to audio file
        audio_features: Extracted audio features
        
    Returns:
        Embedding generation result
    """
    try:
        logger.info(f"Generating embeddings for file {file_id}")
        
        self.update_state(
            state="STARTED",
            meta={
                "file_id": file_id,
                "status": "Generating embeddings..."
            }
        )
        
        # Create embedding vector from features
        import numpy as np
        
        # Combine key features into embedding vector
        embedding_components = []
        
        if "tempo" in audio_features:
            embedding_components.append(audio_features["tempo"] / 200.0)
        
        if "key" in audio_features:
            # Convert key to numeric (C=0, C#=1, ..., B=11)
            key_map = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
                      "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
            key_value = key_map.get(audio_features["key"], 0) / 12.0
            embedding_components.append(key_value)
        
        # Add spectral features if available
        for feature in ["spectral_centroid", "spectral_bandwidth", "spectral_rolloff"]:
            if feature in audio_features:
                value = audio_features[feature]
                if isinstance(value, (list, np.ndarray)):
                    embedding_components.append(float(np.mean(value)))
                else:
                    embedding_components.append(float(value))
        
        # Pad or truncate to fixed size (e.g., 128 dimensions)
        target_size = 128
        embedding = np.zeros(target_size)
        embedding[:min(len(embedding_components), target_size)] = embedding_components[:target_size]
        
        # Normalize embedding
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        # Store in ChromaDB
        from samplemind.core.database.chroma import add_embedding
        
        metadata = {
            "tempo": audio_features.get("tempo"),
            "key": audio_features.get("key"),
            "duration": audio_features.get("duration"),
        }
        
        asyncio.run(
            add_embedding(
                file_id=file_id,
                embedding=embedding.tolist(),
                metadata=metadata
            )
        )
        
        logger.info(f"Embeddings generated and stored for file {file_id}")
        
        return {
            "file_id": file_id,
            "embedding_size": len(embedding),
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Error generating embeddings: {e}")
        return {
            "file_id": file_id,
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


@celery_app.task(name="samplemind.core.tasks.audio_tasks.cleanup_old_results")
def cleanup_old_results() -> None:
    """
    Periodic task to cleanup old analysis results
    Runs every hour via Celery Beat
    """
    try:
        logger.info("Running cleanup of old results")
        
        # Delete results older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        from samplemind.core.database.repositories import AnalysisRepository
        
        # This would need a method in the repository
        # For now, just log
        logger.info(f"Would cleanup results older than {cutoff_date}")
        
        return {
            "status": "completed",
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Error in cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }
