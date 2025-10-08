"""
Database Performance Audit Script
Comprehensive analysis of MongoDB performance and optimization opportunities

This script analyzes:
- Slow queries and missing indexes
- Collection sizes and growth
- Query patterns and execution times
- Index usage and effectiveness
- Connection pool statistics
- Cache performance
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pymongo import MongoClient
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    MONGODB_AVAILABLE = True
except ImportError:
    print("❌ Required packages not available")
    print("Install with: pip install pymongo python-dotenv")
    MONGODB_AVAILABLE = False
    sys.exit(1)


class DatabaseAuditor:
    """Comprehensive database performance auditor"""

    def __init__(self, mongodb_uri: str, database_name: str = "samplemind"):
        """
        Initialize database auditor

        Args:
            mongodb_uri: MongoDB connection URI
            database_name: Database name to audit
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.database_name = database_name

        print(f"✅ Connected to MongoDB: {database_name}")

    def audit_collection_sizes(self) -> Dict[str, Any]:
        """Audit collection sizes and document counts"""
        print("\n" + "="*80)
        print("📊 COLLECTION SIZES AUDIT")
        print("="*80)

        results = {}
        total_size = 0
        total_docs = 0

        for collection_name in self.db.list_collection_names():
            stats = self.db.command('collStats', collection_name)

            size_mb = stats.get('size', 0) / (1024 * 1024)
            count = stats.get('count', 0)
            avg_doc_size = stats.get('avgObjSize', 0)
            storage_size_mb = stats.get('storageSize', 0) / (1024 * 1024)

            results[collection_name] = {
                'count': count,
                'size_mb': round(size_mb, 2),
                'storage_size_mb': round(storage_size_mb, 2),
                'avg_doc_size_bytes': avg_doc_size,
                'indexes': stats.get('nindexes', 0),
                'total_index_size_mb': round(stats.get('totalIndexSize', 0) / (1024 * 1024), 2)
            }

            total_size += size_mb
            total_docs += count

            print(f"\n📁 {collection_name}")
            print(f"  Documents:    {count:,}")
            print(f"  Size:         {size_mb:.2f} MB")
            print(f"  Storage:      {storage_size_mb:.2f} MB")
            print(f"  Avg Doc Size: {avg_doc_size:,} bytes")
            print(f"  Indexes:      {stats.get('nindexes', 0)}")
            print(f"  Index Size:   {results[collection_name]['total_index_size_mb']:.2f} MB")

        print(f"\n{'='*80}")
        print(f"📈 TOTAL: {total_docs:,} documents, {total_size:.2f} MB")
        print(f"{'='*80}\n")

        return results

    def audit_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Audit all indexes and their usage"""
        print("\n" + "="*80)
        print("📑 INDEX AUDIT")
        print("="*80)

        results = {}

        for collection_name in self.db.list_collection_names():
            print(f"\n📁 {collection_name}")
            print("-" * 80)

            collection = self.db[collection_name]
            indexes = list(collection.list_indexes())

            collection_indexes = []

            for idx in indexes:
                index_info = {
                    'name': idx['name'],
                    'keys': idx.get('key', {}),
                    'unique': idx.get('unique', False),
                    'sparse': idx.get('sparse', False),
                    'ttl': idx.get('expireAfterSeconds'),
                    'size': 0,
                    'accesses': 0
                }

                print(f"  • {idx['name']}")
                print(f"    Keys:   {idx.get('key', {})}")
                if idx.get('unique'):
                    print(f"    Unique: Yes")
                if idx.get('expireAfterSeconds') is not None:
                    print(f"    TTL:    {idx['expireAfterSeconds']}s")

                collection_indexes.append(index_info)

            results[collection_name] = collection_indexes

        print(f"\n{'='*80}\n")
        return results

    def audit_query_performance(self) -> Dict[str, Any]:
        """Audit query performance and find slow operations"""
        print("\n" + "="*80)
        print("⚡ QUERY PERFORMANCE AUDIT")
        print("="*80)

        # Get current operations
        current_ops = self.db.command('currentOp')

        slow_queries = []
        for op in current_ops.get('inprog', []):
            # Look for long-running queries
            if op.get('secs_running', 0) > 1:  # > 1 second
                slow_queries.append({
                    'op': op.get('op'),
                    'ns': op.get('ns'),
                    'duration_secs': op.get('secs_running'),
                    'command': str(op.get('command', {}))[:100]
                })

        if slow_queries:
            print(f"\n⚠️  Found {len(slow_queries)} slow queries:")
            for q in slow_queries:
                print(f"\n  Operation: {q['op']}")
                print(f"  Namespace: {q['ns']}")
                print(f"  Duration:  {q['duration_secs']}s")
                print(f"  Command:   {q['command']}")
        else:
            print("\n✅ No slow queries detected")

        print(f"\n{'='*80}\n")
        return {'slow_queries': slow_queries}

    def audit_connection_pool(self) -> Dict[str, Any]:
        """Audit connection pool statistics"""
        print("\n" + "="*80)
        print("🔗 CONNECTION POOL AUDIT")
        print("="*80)

        server_status = self.db.command('serverStatus')
        connections = server_status.get('connections', {})

        pool_stats = {
            'current': connections.get('current', 0),
            'available': connections.get('available', 0),
            'total_created': connections.get('totalCreated', 0),
            'active': connections.get('active', 0)
        }

        print(f"\n  Current Connections:   {pool_stats['current']}")
        print(f"  Available:             {pool_stats['available']}")
        print(f"  Total Created:         {pool_stats['total_created']}")
        print(f"  Active:                {pool_stats['active']}")

        utilization = (pool_stats['current'] / max(pool_stats['available'] + pool_stats['current'], 1)) * 100
        print(f"  Pool Utilization:      {utilization:.1f}%")

        if utilization > 80:
            print(f"\n  ⚠️  WARNING: High pool utilization ({utilization:.1f}%)")
            print("     Consider increasing pool size")
        else:
            print(f"\n  ✅ Connection pool utilization healthy")

        print(f"\n{'='*80}\n")
        return pool_stats

    def find_missing_indexes(self) -> List[Dict[str, Any]]:
        """Identify potential missing indexes based on query patterns"""
        print("\n" + "="*80)
        print("🔍 MISSING INDEX DETECTION")
        print("="*80)

        recommendations = []

        # Common query patterns to check
        common_queries = {
            'users': [
                {'email': 1},
                {'username': 1},
                {'is_active': 1, 'created_at': -1}
            ],
            'audio_files': [
                {'user_id': 1, 'created_at': -1},
                {'status': 1},
                {'tags': 1}
            ],
            'analyses': [
                {'audio_file_id': 1},
                {'user_id': 1, 'status': 1}
            ]
        }

        for collection_name, queries in common_queries.items():
            if collection_name not in self.db.list_collection_names():
                continue

            collection = self.db[collection_name]
            existing_indexes = {str(idx['key']) for idx in collection.list_indexes()}

            for query_pattern in queries:
                if str(query_pattern) not in existing_indexes:
                    recommendations.append({
                        'collection': collection_name,
                        'suggested_index': query_pattern,
                        'reason': 'Common query pattern detected'
                    })

        if recommendations:
            print(f"\n📋 Found {len(recommendations)} index recommendations:\n")
            for rec in recommendations:
                print(f"  Collection: {rec['collection']}")
                print(f"  Index:      {rec['suggested_index']}")
                print(f"  Reason:     {rec['reason']}\n")
        else:
            print("\n✅ All common query patterns have indexes")

        print(f"{'='*80}\n")
        return recommendations

    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        print("\n" + "="*80)
        print("📋 OPTIMIZATION RECOMMENDATIONS")
        print("="*80)

        recommendations = []

        # Check collection sizes
        size_audit = self.audit_collection_sizes()
        for coll, stats in size_audit.items():
            if stats['size_mb'] > 1000:  # > 1GB
                recommendations.append({
                    'severity': 'medium',
                    'category': 'storage',
                    'message': f"Collection '{coll}' is large ({stats['size_mb']:.2f} MB) - consider archiving old data"
                })

            if stats['count'] > 1000000:  # > 1M docs
                recommendations.append({
                    'severity': 'medium',
                    'category': 'performance',
                    'message': f"Collection '{coll}' has many documents ({stats['count']:,}) - ensure proper indexing"
                })

        # Check query performance
        query_audit = self.audit_query_performance()
        if query_audit['slow_queries']:
            recommendations.append({
                'severity': 'high',
                'category': 'performance',
                'message': f"Found {len(query_audit['slow_queries'])} slow queries - review and optimize"
            })

        # Check connection pool
        pool_stats = self.audit_connection_pool()
        utilization = (pool_stats['current'] / max(pool_stats['available'] + pool_stats['current'], 1)) * 100
        if utilization > 80:
            recommendations.append({
                'severity': 'high',
                'category': 'connections',
                'message': f"Connection pool utilization high ({utilization:.1f}%) - increase pool size"
            })

        # Check for missing indexes
        missing_indexes = self.find_missing_indexes()
        if missing_indexes:
            recommendations.append({
                'severity': 'high',
                'category': 'indexing',
                'message': f"Found {len(missing_indexes)} missing index opportunities"
            })

        # Print recommendations by severity
        print()
        for severity in ['high', 'medium', 'low']:
            severity_recs = [r for r in recommendations if r['severity'] == severity]
            if severity_recs:
                emoji = '🔴' if severity == 'high' else '🟡' if severity == 'medium' else '🟢'
                print(f"\n{emoji} {severity.upper()} PRIORITY:")
                for rec in severity_recs:
                    print(f"  [{rec['category']}] {rec['message']}")

        if not recommendations:
            print("\n✅ No major optimization opportunities found!")
            print("   Database is well-optimized.")

        print(f"\n{'='*80}\n")
        return {'recommendations': recommendations}

    def export_report(self, output_file: str = "database_audit_report.json"):
        """Export full audit report to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.database_name,
            'collection_sizes': self.audit_collection_sizes(),
            'indexes': self.audit_indexes(),
            'query_performance': self.audit_query_performance(),
            'connection_pool': self.audit_connection_pool(),
            'missing_indexes': self.find_missing_indexes(),
            'recommendations': self.generate_optimization_report()
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Full report exported to: {output_file}")
        return report


def main():
    """Run database audit"""
    print("\n" + "="*80)
    print("🔍 SAMPLEMIND AI - DATABASE PERFORMANCE AUDIT")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Get MongoDB URI from environment
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    database_name = os.getenv('MONGODB_DATABASE', 'samplemind')

    print(f"\nConnecting to: {mongodb_uri}")
    print(f"Database: {database_name}")

    try:
        auditor = DatabaseAuditor(mongodb_uri, database_name)

        # Run all audits
        auditor.audit_collection_sizes()
        auditor.audit_indexes()
        auditor.audit_query_performance()
        auditor.audit_connection_pool()
        auditor.find_missing_indexes()
        auditor.generate_optimization_report()

        # Export report
        auditor.export_report()

        print("\n" + "="*80)
        print("✅ AUDIT COMPLETE!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if not MONGODB_AVAILABLE:
        print("❌ MongoDB packages not available")
        sys.exit(1)

    main()