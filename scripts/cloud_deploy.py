#!/usr/bin/env python3
"""
Cloud Deployment Script for SampleMind Audio Processing

This script provides commands to deploy and manage the audio processing
application on cloud platforms.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from google.cloud import container_v1
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_CONTEXT = PROJECT_ROOT / "docker/audio-processor"
DOCKER_IMAGE = "samplemind/audio-processor"
DOCKER_TAG = "latest"


def build_docker_image() -> bool:
    """Build the Docker image for cloud deployment."""
    try:
        logger.info(f"Building Docker image {DOCKER_IMAGE}:{DOCKER_TAG}")
        
        # Build the Docker image
        cmd = [
            "docker", "build",
            "-t", f"{DOCKER_IMAGE}:{DOCKER_TAG}",
            "--build-arg", f"VERSION={DOCKER_TAG}",
            str(DOCKER_CONTEXT)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.debug(f"Docker build output: {result.stdout}")
        
        logger.success("Docker image built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Docker image: {e.stderr}")
        return False


def push_docker_image(registry: str = None) -> bool:
    """Push the Docker image to a container registry."""
    try:
        if registry:
            # Tag for the registry
            remote_image = f"{registry}/{DOCKER_IMAGE}"
            subprocess.run(
                ["docker", "tag", f"{DOCKER_IMAGE}:{DOCKER_TAG}", f"{remote_image}:{DOCKER_TAG}"],
                check=True
            )
            image_to_push = remote_image
        else:
            image_to_push = DOCKER_IMAGE
        
        logger.info(f"Pushing Docker image {image_to_push}:{DOCKER_TAG}")
        subprocess.run(
            ["docker", "push", f"{image_to_push}:{DOCKER_TAG}"],
            check=True
        )
        
        logger.success(f"Successfully pushed {image_to_push}:{DOCKER_TAG}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push Docker image: {e}")
        return False


def deploy_aws(cluster_name: str, region: str, node_count: int = 3) -> bool:
    """Deploy to AWS ECS/EKS."""
    try:
        logger.info(f"Deploying to AWS ECS in {region}")
        
        # Check if ECS cluster exists, create if not
        ecs = boto3.client('ecs', region_name=region)
        
        try:
            ecs.describe_clusters(clusters=[cluster_name])
            logger.info(f"Using existing ECS cluster: {cluster_name}")
        except ecs.exceptions.ClusterNotFoundException:
            logger.info(f"Creating ECS cluster: {cluster_name}")
            ecs.create_cluster(clusterName=cluster_name)
        
        # Deploy using AWS CDK or CloudFormation would go here
        # This is a simplified example
        logger.warning("AWS deployment not fully implemented. Manual deployment required.")
        logger.info("Please deploy using the AWS CDK or CloudFormation template.")
        
        return True
        
    except Exception as e:
        logger.error(f"AWS deployment failed: {e}")
        return False


def deploy_gcp(project_id: str, zone: str, cluster_name: str, node_count: int = 3) -> bool:
    """Deploy to Google Kubernetes Engine."""
    try:
        logger.info(f"Deploying to GKE in {zone}")
        
        # Initialize the GKE client
        client = container_v1.ClusterManagerClient()
        
        # Check if cluster exists
        parent = f"projects/{project_id}/locations/{zone}"
        clusters = client.list_clusters(parent=parent)
        
        cluster_exists = any(c.name == f"{parent}/clusters/{cluster_name}" for c in clusters.clusters)
        
        if not cluster_exists:
            # Create a new cluster
            logger.info(f"Creating GKE cluster: {cluster_name}")
            
            # Define the cluster
            cluster = {
                "name": cluster_name,
                "initial_node_count": node_count,
                "node_config": {
                    "machine_type": "e2-standard-4",
                    "oauth_scopes": [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                },
                "workload_identity_config": {
                    "workload_pool": f"{project_id}.svc.id.goog"
                }
            }
            
            # Create the cluster
            operation = client.create_cluster(
                parent=parent,
                cluster=cluster
            )
            
            # Wait for the operation to complete
            result = operation.result()
            logger.info(f"Cluster created: {result.name}")
        else:
            logger.info(f"Using existing GKE cluster: {cluster_name}")
        
        # Configure kubectl
        subprocess.run(
            ["gcloud", "container", "clusters", "get-credentials", 
             cluster_name, "--zone", zone, "--project", project_id],
            check=True
        )
        
        # Deploy the application (simplified)
        logger.warning("GKE deployment not fully implemented. Manual deployment required.")
        logger.info("Please deploy using the provided Kubernetes manifests.")
        
        return True
        
    except Exception as e:
        logger.error(f"GKE deployment failed: {e}")
        return False


def main():
    """Main function for the deployment script."""
    parser = argparse.ArgumentParser(description='Deploy SampleMind to the cloud')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the Docker image')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push the Docker image to a registry')
    push_parser.add_argument('--registry', help='Container registry URL')
    
    # AWS deploy command
    aws_parser = subparsers.add_parser('deploy-aws', help='Deploy to AWS')
    aws_parser.add_argument('--cluster', default='samplemind-cluster', help='ECS cluster name')
    aws_parser.add_argument('--region', default='us-west-2', help='AWS region')
    aws_parser.add_argument('--nodes', type=int, default=3, help='Number of nodes')
    
    # GCP deploy command
    gcp_parser = subparsers.add_parser('deploy-gcp', help='Deploy to Google Cloud')
    gcp_parser.add_argument('--project', required=True, help='GCP project ID')
    gcp_parser.add_argument('--zone', default='us-central1-a', help='GCP zone')
    gcp_parser.add_argument('--cluster', default='samplemind-cluster', help='GKE cluster name')
    gcp_parser.add_argument('--nodes', type=int, default=3, help='Number of nodes')
    
    args = parser.parse_args()
    
    # Execute the command
    if args.command == 'build':
        success = build_docker_image()
    elif args.command == 'push':
        success = push_docker_image(args.registry)
    elif args.command == 'deploy-aws':
        success = deploy_aws(args.cluster, args.region, args.nodes)
    elif args.command == 'deploy-gcp':
        success = deploy_gcp(args.project, args.zone, args.cluster, args.nodes)
    else:
        logger.error(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
