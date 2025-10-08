"""
MongoDB Index Management
Strategic index creation and optimization utilities

This module provides:
- Index creation and management
- Index usage statistics
- Index optimization recommendations
- Automated index maintenance
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING, TEXT, GEOSPHERE
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


# Index Definitions
INDEX_DEFINITIONS = {
    'users': [
        {
            'keys': [('email', ASCENDING)],
            'unique': True,
            'name': 'idx_users_email'
        },
        {
            'keys': [('username', ASCENDING)],
            'unique': True,
            'name': 'idx_users_username'
        },
        {
            'keys': [('user_id', ASCENDING)],
            'unique': True,
            'name': 'idx_users_user_id'
        },
        {
            'keys': [('created_at', DESCENDING)],
            'name': 'idx_users_created_at'
        },
        {
            'keys': [('is_active', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_users_active_created'
        }
    ],
    'audio_files': [
        {
            'keys': [('_id', ASCENDING)],
            'name': 'idx_audio_files_id'
        },
        {
            'keys': [('user_id', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_audio_files_user_created'
        },
        {
            'keys': [('file_hash', ASCENDING)],
            'unique': True,
            'name': 'idx_audio_files_hash'
        },
        {
            'keys': [('tags', ASCENDING)],
            'name': 'idx_audio_files_tags'
        },
        {
            'keys': [('metadata.duration', ASCENDING)],
            'name': 'idx_audio_files_duration'
        },
        {
            'keys': [('metadata.sample_rate', ASCENDING)],
            'name': 'idx_audio_files_sample_rate'
        },
        {
            'keys': [('user_id', ASCENDING), ('tags', ASCENDING)],
            'name': 'idx_audio_files_user_tags'
        },
        {
            'keys': [('status', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_audio_files_status_created'
        },
        {
            'keys': [
                ('filename', TEXT),
                ('tags', TEXT),
                ('description', TEXT)
            ],
            'name': 'idx_audio_files_text_search',
            'weights': {
                'filename': 10,
                'tags': 5,
                'description': 1
            }
        }
    ],
    'analyses': [
        {
            'keys': [('_id', ASCENDING)],
            'name': 'idx_analyses_id'
        },
        {
            'keys': [('audio_file_id', ASCENDING)],
            'name': 'idx_analyses_audio_file'
        },
        {
            'keys': [('user_id', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_analyses_user_created'
        },
        {
            'keys': [('status', ASCENDING)],
            'name': 'idx_analyses_status'
        },
        {
            'keys': [('user_id', ASCENDING), ('status', ASCENDING)],
            'name': 'idx_analyses_user_status'
        },
        {
            'keys': [('audio_file_id', ASCENDING), ('analysis_type', ASCENDING)],
            'name': 'idx_analyses_file_type'
        },
        {
            'keys': [('created_at', DESCENDING)],
            'name': 'idx_analyses_created',
            'expireAfterSeconds': 2592000  # 30 days TTL
        }
    ],
    'batch_jobs': [
        {
            'keys': [('_id', ASCENDING)],
            'name': 'idx_batch_jobs_id'
        },
        {
            'keys': [('user_id', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_batch_jobs_user_created'
        },
        {
            'keys': [('status', ASCENDING), ('created_at', DESCENDING)],
            'name': 'idx_batch_jobs_status_created'
        },
        {
            'keys': [('user_id', ASCENDING), ('status', ASCENDING)],
            'name': 'idx_batch_jobs_user_status'
        },
        {
            'keys': [('completed_at', ASCENDING)],
            'name': 'idx_batch_jobs_completed',
            'expireAfterSeconds': 604800  # 7 days TTL
        }
    ],
    'sessions': [
        {
            'keys': [('session_id', ASCENDING)],
            'unique': True,
            'name': 'idx_sessions_session_id'
        },
        {
            'keys': [('user_id', ASCENDING)],
            'name': 'idx_sessions_user_id'
        },
        {
            'keys': [('expires_at', ASCENDING)],
            'name': 'idx_sessions_expires',
            'expireAfterSeconds': 0  # Auto-delete at expires_at
        }
    ]
}


class IndexManager:
    """Manage MongoDB indexes"""

    def __init__(self, database: Database):
        """
        Initialize index manager

        Args:
            database: MongoDB database instance
        """
        self.db = database
        logger.info(f"IndexManager initialized for database: {database.name}")

    def create_all_indexes(self, drop_existing: bool = False) -> Dict[str, Any]:
        """
        Create all defined indexes

        Args:
            drop_existing: Whether to drop existing indexes first

        Returns:
            Summary of index creation
        """
        results = {
            'created': [],
            'failed': [],
            'skipped': [],
            'dropped': []
        }

        for collection_name, indexes in INDEX_DEFINITIONS.items():
            collection = self.db[collection_name]

            # Drop existing indexes if requested
            if drop_existing:
                try:
                    collection.drop_indexes()
                    results['dropped'].append(collection_name)
                    logger.info(f"Dropped indexes for: {collection_name}")
                except Exception as e:
                    logger.warning(f"Could not drop indexes for {collection_name}: {e}")

            # Create each index
            for index_def in indexes:
                try:
                    # Extract parameters
                    keys = index_def.pop('keys')
                    name = index_def.get('name')

                    # Create index
                    collection.create_index(keys, **index_def)
                    results['created'].append(f"{collection_name}.{name}")
                    logger.info(f"Created index: {collection_name}.{name}")

                except OperationFailure as e:
                    if 'already exists' in str(e):
                        results['skipped'].append(f"{collection_name}.{name}")
                        logger.debug(f"Index already exists: {collection_name}.{name}")
                    else:
                        results['failed'].append({
                            'collection': collection_name,
                            'index': name,
                            'error': str(e)
                        })
                        logger.error(f"Failed to create index {collection_name}.{name}: {e}")
                except Exception as e:
                    results['failed'].append({
                        'collection': collection_name,
                        'index': name,
                        'error': str(e)
                    })
                    logger.error(f"Error creating index {collection_name}.{name}: {e}")

        return results

    def get_index_stats(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        Get index statistics for a collection

        Args:
            collection_name: Collection name

        Returns:
            List of index statistics
        """
        try:
            collection = self.db[collection_name]
            stats = collection.aggregate([
                {'$indexStats': {}}
            ])

            return list(stats)

        except Exception as e:
            logger.error(f"Error getting index stats for {collection_name}: {e}")
            return []

    def analyze_index_usage(
        self,
        collection_name: str,
        min_accesses: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze index usage and provide recommendations

        Args:
            collection_name: Collection name
            min_accesses: Minimum accesses to consider index useful

        Returns:
            Analysis results with recommendations
        """
        stats = self.get_index_stats(collection_name)

        unused_indexes = []
        low_usage_indexes = []
        active_indexes = []

        for stat in stats:
            index_name = stat['name']
            accesses = stat.get('accesses', {}).get('ops', 0)

            if index_name == '_id_':
                # Skip default _id index
                continue

            if accesses == 0:
                unused_indexes.append({
                    'name': index_name,
                    'accesses': accesses,
                    'size_bytes': stat.get('size', 0)
                })
            elif accesses < min_accesses:
                low_usage_indexes.append({
                    'name': index_name,
                    'accesses': accesses,
                    'size_bytes': stat.get('size', 0)
                })
            else:
                active_indexes.append({
                    'name': index_name,
                    'accesses': accesses,
                    'size_bytes': stat.get('size', 0)
                })

        return {
            'collection': collection_name,
            'total_indexes': len(stats),
            'unused_indexes': unused_indexes,
            'low_usage_indexes': low_usage_indexes,
            'active_indexes': active_indexes,
            'recommendations': self._generate_recommendations(
                unused_indexes,
                low_usage_indexes
            )
        }

    def _generate_recommendations(
        self,
        unused: List[Dict],
        low_usage: List[Dict]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if unused:
            recommendations.append(
                f"Consider dropping {len(unused)} unused indexes to save space"
            )

        if low_usage:
            recommendations.append(
                f"Review {len(low_usage)} low-usage indexes - may be candidates for removal"
            )

        if not unused and not low_usage:
            recommendations.append("All indexes are actively used - good optimization!")

        return recommendations

    def get_all_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all indexes across all collections

        Returns:
            Dictionary mapping collection names to their indexes
        """
        all_indexes = {}

        for collection_name in INDEX_DEFINITIONS.keys():
            try:
                collection = self.db[collection_name]
                indexes = list(collection.list_indexes())
                all_indexes[collection_name] = indexes
            except Exception as e:
                logger.error(f"Error listing indexes for {collection_name}: {e}")
                all_indexes[collection_name] = []

        return all_indexes

    def verify_indexes(self) -> Dict[str, Any]:
        """
        Verify all defined indexes exist

        Returns:
            Verification results
        """
        results = {
            'verified': [],
            'missing': [],
            'extra': []
        }

        for collection_name, expected_indexes in INDEX_DEFINITIONS.items():
            try:
                collection = self.db[collection_name]
                existing = {idx['name'] for idx in collection.list_indexes()}
                expected = {idx['name'] for idx in expected_indexes}

                # Check each expected index
                for idx_name in expected:
                    if idx_name in existing:
                        results['verified'].append(f"{collection_name}.{idx_name}")
                    else:
                        results['missing'].append(f"{collection_name}.{idx_name}")

                # Check for extra indexes
                for idx_name in existing:
                    if idx_name not in expected and idx_name != '_id_':
                        results['extra'].append(f"{collection_name}.{idx_name}")

            except Exception as e:
                logger.error(f"Error verifying indexes for {collection_name}: {e}")

        return results

    def print_statistics(self):
        """Print formatted index statistics"""
        print("\n" + "="*60)
        print("📑 MONGODB INDEX STATISTICS")
        print("="*60)

        for collection_name in INDEX_DEFINITIONS.keys():
            print(f"\n Collection: {collection_name}")
            print("-" * 60)

            try:
                collection = self.db[collection_name]
                indexes = list(collection.list_indexes())

                for idx in indexes:
                    print(f"  • {idx['name']}")
                    print(f"    Keys: {idx.get('key', {})}")
                    if idx.get('unique'):
                        print(f"    Unique: Yes")
                    if idx.get('expireAfterSeconds') is not None:
                        print(f"    TTL: {idx['expireAfterSeconds']}s")

            except Exception as e:
                print(f"  Error: {e}")

        print("\n" + "="*60 + "\n")


def create_indexes_sync(database: Database, drop_existing: bool = False) -> Dict[str, Any]:
    """
    Convenience function to create all indexes synchronously

    Args:
        database: MongoDB database instance
        drop_existing: Whether to drop existing indexes

    Returns:
        Index creation summary
    """
    manager = IndexManager(database)
    return manager.create_all_indexes(drop_existing)


async def create_indexes_async(
    database: AsyncIOMotorDatabase,
    drop_existing: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to create all indexes asynchronously

    Args:
        database: Async MongoDB database instance
        drop_existing: Whether to drop existing indexes

    Returns:
        Index creation summary
    """
    # Note: For async, we need to use the sync client for index operations
    # as Motor doesn't fully support all index management operations
    logger.warning("Async index creation not fully supported, use sync version")
    return {
        'created': [],
        'failed': [],
        'skipped': [],
        'dropped': []
    }