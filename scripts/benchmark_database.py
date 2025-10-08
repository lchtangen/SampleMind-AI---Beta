"""
Database Performance Benchmark Script
Measure and compare database performance metrics

This script benchmarks:
- Query execution times (with/without indexes)
- Connection pool performance
- Cache hit rates
- Concurrent query performance
- Batch operation performance
"""

import sys
import os
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pymongo import MongoClient
    from dotenv import load_dotenv
    import numpy as np
    
    # Load environment variables
    load_dotenv()
    
    MONGODB_AVAILABLE = True
except ImportError:
    print("❌ Required packages not available")
    print("Install with: pip install pymongo python-dotenv numpy")
    MONGODB_AVAILABLE = False
    sys.exit(1)


class DatabaseBenchmark:
    """Comprehensive database performance benchmark"""

    def __init__(self, mongodb_uri: str, database_name: str = "samplemind"):
        """
        Initialize database benchmark

        Args:
            mongodb_uri: MongoDB connection URI
            database_name: Database name to benchmark
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.database_name = database_name

        print(f"✅ Connected to MongoDB: {database_name}")

    def benchmark_single_query(
        self,
        collection_name: str,
        query: Dict,
        num_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark single query performance

        Args:
            collection_name: Collection to query
            query: Query to execute
            num_iterations: Number of times to run query

        Returns:
            Benchmark results
        """
        collection = self.db[collection_name]
        times = []

        print(f"\n🔍 Benchmarking: {collection_name}.find({query})")
        print(f"   Iterations: {num_iterations}")

        for i in range(num_iterations):
            start_time = time.time()
            list(collection.find(query).limit(10))
            elapsed = (time.time() - start_time) * 1000  # ms
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/{num_iterations}", end='\r')

        print()  # New line after progress

        return {
            'collection': collection_name,
            'query': str(query),
            'iterations': num_iterations,
            'min_ms': round(min(times), 2),
            'max_ms': round(max(times), 2),
            'mean_ms': round(np.mean(times), 2),
            'median_ms': round(np.median(times), 2),
            'p95_ms': round(np.percentile(times, 95), 2),
            'p99_ms': round(np.percentile(times, 99), 2),
            'std_ms': round(np.std(times), 2)
        }

    def benchmark_index_impact(
        self,
        collection_name: str,
        query: Dict,
        index_keys: List[tuple]
    ) -> Dict[str, Any]:
        """
        Benchmark query performance with/without index

        Args:
            collection_name: Collection to query
            query: Query to execute
            index_keys: Index keys to create

        Returns:
            Comparison results
        """
        collection = self.db[collection_name]

        print(f"\n📊 Index Impact Test: {collection_name}")
        print(f"   Query: {query}")
        print(f"   Index: {index_keys}")

        # Benchmark without index
        print("\n   Testing WITHOUT index...")
        without_index = self.benchmark_single_query(
            collection_name, query, num_iterations=50
        )

        # Create index
        print(f"\n   Creating index...")
        index_name = f"bench_{int(time.time())}"
        collection.create_index(index_keys, name=index_name)

        # Benchmark with index
        print(f"\n   Testing WITH index...")
        with_index = self.benchmark_single_query(
            collection_name, query, num_iterations=50
        )

        # Clean up - drop benchmark index
        collection.drop_index(index_name)

        speedup = without_index['mean_ms'] / max(with_index['mean_ms'], 0.001)

        return {
            'without_index': without_index,
            'with_index': with_index,
            'speedup': round(speedup, 2),
            'improvement_pct': round((1 - with_index['mean_ms'] / without_index['mean_ms']) * 100, 2)
        }

    def benchmark_concurrent_queries(
        self,
        collection_name: str,
        query: Dict,
        num_concurrent: int = 10,
        queries_per_thread: int = 10
    ) -> Dict[str, Any]:
        """
        Benchmark concurrent query performance

        Args:
            collection_name: Collection to query
            query: Query to execute
            num_concurrent: Number of concurrent threads
            queries_per_thread: Queries per thread

        Returns:
            Concurrent benchmark results
        """
        print(f"\n🔀 Concurrent Query Benchmark: {collection_name}")
        print(f"   Concurrent threads: {num_concurrent}")
        print(f"   Queries per thread: {queries_per_thread}")

        def run_queries(thread_id: int) -> List[float]:
            """Run queries in a thread"""
            client = MongoClient(self.client.HOST, self.client.PORT)
            db = client[self.database_name]
            collection = db[collection_name]

            times = []
            for _ in range(queries_per_thread):
                start_time = time.time()
                list(collection.find(query).limit(10))
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)

            client.close()
            return times

        # Execute concurrent queries
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(run_queries, i) for i in range(num_concurrent)]

            all_times = []
            for future in as_completed(futures):
                all_times.extend(future.result())

        total_time = time.time() - start_time

        return {
            'collection': collection_name,
            'query': str(query),
            'concurrent_threads': num_concurrent,
            'queries_per_thread': queries_per_thread,
            'total_queries': len(all_times),
            'total_time_sec': round(total_time, 2),
            'throughput_qps': round(len(all_times) / total_time, 2),
            'min_ms': round(min(all_times), 2),
            'max_ms': round(max(all_times), 2),
            'mean_ms': round(np.mean(all_times), 2),
            'median_ms': round(np.median(all_times), 2),
            'p95_ms': round(np.percentile(all_times, 95), 2),
            'p99_ms': round(np.percentile(all_times, 99), 2)
        }

    def benchmark_batch_operations(
        self,
        collection_name: str,
        batch_sizes: List[int] = [10, 50, 100]
    ) -> Dict[str, Any]:
        """
        Benchmark batch insert/update operations

        Args:
            collection_name: Collection for batch operations
            batch_sizes: List of batch sizes to test

        Returns:
            Batch operation results
        """
        print(f"\n📦 Batch Operations Benchmark: {collection_name}")

        collection = self.db[collection_name]
        results = {}

        for batch_size in batch_sizes:
            print(f"\n   Testing batch size: {batch_size}")

            # Generate test documents
            docs = [
                {
                    'benchmark_test': True,
                    'batch_id': int(time.time()),
                    'index': i,
                    'data': f"test_data_{i}"
                }
                for i in range(batch_size)
            ]

            # Benchmark insert
            start_time = time.time()
            collection.insert_many(docs)
            insert_time = (time.time() - start_time) * 1000

            # Benchmark update
            batch_id = docs[0]['batch_id']
            start_time = time.time()
            collection.update_many(
                {'batch_id': batch_id},
                {'$set': {'updated': True}}
            )
            update_time = (time.time() - start_time) * 1000

            # Benchmark delete
            start_time = time.time()
            collection.delete_many({'batch_id': batch_id})
            delete_time = (time.time() - start_time) * 1000

            results[f"batch_{batch_size}"] = {
                'batch_size': batch_size,
                'insert_ms': round(insert_time, 2),
                'update_ms': round(update_time, 2),
                'delete_ms': round(delete_time, 2),
                'total_ms': round(insert_time + update_time + delete_time, 2),
                'docs_per_sec': round(batch_size / ((insert_time + update_time + delete_time) / 1000), 2)
            }

            print(f"   Insert: {insert_time:.2f}ms")
            print(f"   Update: {update_time:.2f}ms")
            print(f"   Delete: {delete_time:.2f}ms")

        return results

    def benchmark_aggregation(
        self,
        collection_name: str,
        pipeline: List[Dict]
    ) -> Dict[str, Any]:
        """
        Benchmark aggregation pipeline performance

        Args:
            collection_name: Collection to aggregate
            pipeline: Aggregation pipeline

        Returns:
            Aggregation benchmark results
        """
        print(f"\n🔄 Aggregation Benchmark: {collection_name}")
        print(f"   Pipeline stages: {len(pipeline)}")

        collection = self.db[collection_name]
        times = []

        for i in range(20):  # 20 iterations
            start_time = time.time()
            list(collection.aggregate(pipeline))
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)

        return {
            'collection': collection_name,
            'pipeline_stages': len(pipeline),
            'iterations': 20,
            'min_ms': round(min(times), 2),
            'max_ms': round(max(times), 2),
            'mean_ms': round(np.mean(times), 2),
            'median_ms': round(np.median(times), 2)
        }

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive database benchmark"""
        print("\n" + "="*80)
        print("⚡ COMPREHENSIVE DATABASE BENCHMARK")
        print("="*80)
        print(f"Database: {self.database_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*80)

        results = {
            'timestamp': datetime.now().isoformat(),
            'database': self.database_name,
            'benchmarks': {}
        }

        # Single query benchmarks
        print("\n" + "="*80)
        print("1. SINGLE QUERY PERFORMANCE")
        print("="*80)

        if 'users' in self.db.list_collection_names():
            results['benchmarks']['query_users'] = self.benchmark_single_query(
                'users',
                {'is_active': True}
            )

        if 'audio_files' in self.db.list_collection_names():
            results['benchmarks']['query_audio'] = self.benchmark_single_query(
                'audio_files',
                {'status': 'completed'}
            )

        # Concurrent query benchmarks
        print("\n" + "="*80)
        print("2. CONCURRENT QUERY PERFORMANCE")
        print("="*80)

        if 'audio_files' in self.db.list_collection_names():
            results['benchmarks']['concurrent_audio'] = self.benchmark_concurrent_queries(
                'audio_files',
                {'status': 'completed'},
                num_concurrent=10
            )

        # Batch operations
        print("\n" + "="*80)
        print("3. BATCH OPERATIONS")
        print("="*80)

        # Use a test collection
        results['benchmarks']['batch_ops'] = self.benchmark_batch_operations(
            'benchmark_test',
            batch_sizes=[10, 50, 100]
        )

        # Print summary
        self.print_benchmark_summary(results)

        return results

    def print_benchmark_summary(self, results: Dict[str, Any]):
        """Print formatted benchmark summary"""
        print("\n" + "="*80)
        print("📊 BENCHMARK SUMMARY")
        print("="*80)

        benchmarks = results['benchmarks']

        # Query performance
        if 'query_users' in benchmarks:
            print("\n🔍 Single Query Performance (users):")
            q = benchmarks['query_users']
            print(f"   Mean:   {q['mean_ms']:.2f}ms")
            print(f"   P95:    {q['p95_ms']:.2f}ms")
            print(f"   P99:    {q['p99_ms']:.2f}ms")

        # Concurrent performance
        if 'concurrent_audio' in benchmarks:
            print("\n🔀 Concurrent Query Performance:")
            c = benchmarks['concurrent_audio']
            print(f"   Throughput: {c['throughput_qps']:.2f} queries/sec")
            print(f"   Mean:       {c['mean_ms']:.2f}ms")
            print(f"   P95:        {c['p95_ms']:.2f}ms")

        # Batch operations
        if 'batch_ops' in benchmarks:
            print("\n📦 Batch Operations (batch_100):")
            b = benchmarks['batch_ops'].get('batch_100', {})
            if b:
                print(f"   Insert: {b['insert_ms']:.2f}ms")
                print(f"   Update: {b['update_ms']:.2f}ms")
                print(f"   Delete: {b['delete_ms']:.2f}ms")
                print(f"   Rate:   {b['docs_per_sec']:.2f} docs/sec")

        print("\n" + "="*80 + "\n")

    def export_results(self, results: Dict[str, Any], output_file: str = "database_benchmark_results.json"):
        """Export benchmark results to JSON"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"📄 Results exported to: {output_file}\n")


def main():
    """Run database benchmark"""
    print("\n" + "="*80)
    print("⚡ SAMPLEMIND AI - DATABASE PERFORMANCE BENCHMARK")
    print("="*80)

    # Get MongoDB URI from environment
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    database_name = os.getenv('MONGODB_DATABASE', 'samplemind')

    print(f"\nConnecting to: {mongodb_uri}")
    print(f"Database: {database_name}")

    try:
        benchmark = DatabaseBenchmark(mongodb_uri, database_name)

        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()

        # Export results
        benchmark.export_results(results)

        print("="*80)
        print("✅ BENCHMARK COMPLETE!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if not MONGODB_AVAILABLE:
        print("❌ Required packages not available")
        sys.exit(1)

    main()