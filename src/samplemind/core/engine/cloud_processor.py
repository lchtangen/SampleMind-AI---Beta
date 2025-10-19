"""
Cloud-based distributed audio processing.

This module provides support for running distributed audio processing
on cloud platforms like AWS and Google Cloud.
"""
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import dask.bag as db
from dask.distributed import Client
from loguru import logger

from .distributed_processor import DistributedAudioProcessor


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = 'aws'
    GCP = 'gcp'
    LOCAL = 'local'  # For local cluster


@dataclass
class CloudConfig:
    """Configuration for cloud processing."""
    provider: CloudProvider = CloudProvider.LOCAL
    region: str = 'us-west-2'
    instance_type: str = 't3.medium'
    min_workers: int = 1
    max_workers: int = 10
    worker_cpu: int = 2
    worker_memory: str = '4GB'
    use_spot: bool = True
    spot_price: Optional[float] = None
    docker_image: str = "samplemind/audio-processor:latest"
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


class CloudProcessor(ABC):
    """Base class for cloud-based audio processors."""
    
    def __init__(self, config: CloudConfig):
        """Initialize the cloud processor."""
        self.config = config
        self._client = None
        self._cluster = None
    
    @abstractmethod
    def start_cluster(self) -> None:
        """Start the cloud cluster."""
        pass
    
    @abstractmethod
    def stop_cluster(self) -> None:
        """Stop the cloud cluster."""
        pass
    
    def process_files(
        self,
        file_paths: List[Union[str, Path]],
        feature_type: str = 'all',
        level: str = 'standard',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process audio files using the cloud cluster.
        
        Args:
            file_paths: List of paths to audio files
            feature_type: Type of features to extract
            level: Analysis level
            **kwargs: Additional arguments for processing
            
        Returns:
            Dictionary mapping file paths to extracted features
        """
        if self._client is None:
            raise RuntimeError("Cluster not started. Call start_cluster() first.")
        
        # Create a distributed processor using the cluster
        with DistributedAudioProcessor(
            client=self._client,
            n_workers=self.config.max_workers,
            memory_limit=self.config.worker_memory
        ) as processor:
            return processor.process_audio_files(
                file_paths=file_paths,
                feature_type=feature_type,
                level=level,
                **kwargs
            )
    
    def __enter__(self):
        """Context manager entry."""
        self.start_cluster()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_cluster()


class AWSProcessor(CloudProcessor):
    """AWS-based distributed audio processing."""
    
    def start_cluster(self) -> None:
        """Start an AWS ECS or EKS cluster."""
        try:
            from dask_cloudprovider.aws import FargateCluster
            
            logger.info(f"Starting AWS Fargate cluster in {self.config.region}")
            
            self._cluster = FargateCluster(
                n_workers=self.config.min_workers,
                worker_cpu=self.config.worker_cpu,
                worker_mem=self.config.worker_memory,
                image=self.config.docker_image,
                region=self.config.region,
                cluster_arn=os.getenv('AWS_ECS_CLUSTER_ARN'),
                task_role_arn=os.getenv('AWS_TASK_ROLE_ARN'),
                execution_role_arn=os.getenv('AWS_EXECUTION_ROLE_ARN'),
                vpc=os.getenv('AWS_VPC_ID'),
                security_groups=[os.getenv('AWS_SECURITY_GROUP_ID')],
                environment=self.config.environment,
                tags=self.config.tags,
            )
            
            self._client = Client(self._cluster)
            logger.info(f"AWS cluster dashboard: {self._client.dashboard_link}")
            
        except ImportError:
            raise ImportError("dask-cloudprovider[aws] is required for AWS processing")
        except Exception as e:
            logger.error(f"Failed to start AWS cluster: {e}")
            raise
    
    def stop_cluster(self) -> None:
        """Stop the AWS cluster."""
        if self._cluster is not None:
            logger.info("Stopping AWS cluster")
            self._cluster.close()
            self._cluster = None
            self._client = None


class GCPProcessor(CloudProcessor):
    """Google Cloud-based distributed audio processing."""
    
    def start_cluster(self) -> None:
        """Start a GCP GKE cluster."""
        try:
            from dask_cloudprovider.gcp import GCPCluster
            
            logger.info(f"Starting GCP GKE cluster in {self.config.region}")
            
            self._cluster = GCPCluster(
                n_workers=self.config.min_workers,
                worker_cpu=self.config.worker_cpu,
                worker_mem=self.config.worker_memory,
                image=self.config.docker_image,
                zone=f"{self.config.region}-a",  # Use zone a in the region
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                cluster_name=f"samplemind-{int(time.time())}",
                machine_type=self.config.instance_type,
                source_image=None,
                docker_args='--privileged',
                env_vars=self.config.environment,
                docker_volumes=self.config.volumes,
                tags=self.config.tags,
            )
            
            # Scale to max workers
            if self.config.max_workers > self.config.min_workers:
                self._cluster.scale(self.config.max_workers)
            
            self._client = Client(self._cluster)
            logger.info(f"GCP cluster dashboard: {self._client.dashboard_link}")
            
        except ImportError:
            raise ImportError("dask-cloudprovider[gcp] is required for GCP processing")
        except Exception as e:
            logger.error(f"Failed to start GCP cluster: {e}")
            raise
    
    def stop_cluster(self) -> None:
        """Stop the GCP cluster."""
        if self._cluster is not None:
            logger.info("Stopping GCP cluster")
            self._cluster.close()
            self._cluster = None
            self._client = None


def create_cloud_processor(config: CloudConfig) -> CloudProcessor:
    """
    Create a cloud processor for the specified provider.
    
    Args:
        config: Cloud configuration
        
    Returns:
        An instance of the appropriate CloudProcessor subclass
    """
    if config.provider == CloudProvider.AWS:
        return AWSProcessor(config)
    elif config.provider == CloudProvider.GCP:
        return GCPProcessor(config)
    elif config.provider == CloudProvider.LOCAL:
        raise ValueError("Use LocalProcessor for local processing")
    else:
        raise ValueError(f"Unsupported cloud provider: {config.provider}")


def process_in_cloud(
    file_paths: List[Union[str, Path]],
    provider: Union[str, CloudProvider],
    output_file: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process audio files in the cloud.
    
    This is a convenience function that creates and manages a cloud processor
    for a single batch of files.
    
    Args:
        file_paths: List of paths to audio files
        provider: Cloud provider ('aws', 'gcp')
        output_file: Optional path to save results (JSON)
        **kwargs: Additional arguments for CloudConfig
        
    Returns:
        Dictionary mapping file paths to extracted features
    """
    # Convert string provider to enum
    if isinstance(provider, str):
        provider = CloudProvider(provider.lower())
    
    # Create configuration
    config = CloudConfig(provider=provider, **kwargs)
    
    # Process files in the cloud
    with create_cloud_processor(config) as processor:
        results = processor.process_files(file_paths)
    
    # Save results if output file is specified
    if output_file:
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    
    return results
