#!/usr/bin/env python3
"""
Performance benchmarking for PgVectorStore.

This script benchmarks various operations of the PgVectorStore with different
dataset sizes and configurations.

Usage:
    python -m benchmarks.vector_store_benchmark [--dataset-size N] [--batch-size N]
"""
import argparse
import logging
import time
import numpy as np
from pathlib import Path
import sys
from typing import List, Dict, Any, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from samplemind.core.vector_store.advanced_operations import AdvancedVectorOperations, AudioFeatureRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('benchmark')

class VectorStoreBenchmark:
    """Benchmark suite for PgVectorStore."""
    
    def __init__(
        self, 
        dataset_size: int = 1000,
        batch_size: int = 1000,
        embedding_dim: int = 1536,
        test_db: bool = True
    ):
        """Initialize the benchmark.
        
        Args:
            dataset_size: Number of records to use for testing
            batch_size: Batch size for batch operations
            embedding_dim: Dimensionality of the embedding vectors
            test_db: Whether to use a test database (will be dropped after tests)
        """
        self.dataset_size = dataset_size
        self.batch_size = batch_size
        self.embedding_dim = embedding_dim
        self.test_db = test_db
        
        # Initialize vector store
        db_name = "samplemind_benchmark" if test_db else "samplemind"
        self.store = AdvancedVectorOperations(
            connection_string=f"postgresql://postgres:postgres@localhost:5432/{db_name}",
            min_conn=5,
            max_conn=20
        )
        
        # Test data
        self.test_embeddings = None
        self.test_records = None
    
    def setup(self):
        """Set up test data and database."""
        logger.info(f"Generating test data for {self.dataset_size} records...")
        
        # Generate random embeddings
        rng = np.random.RandomState(42)
        self.test_embeddings = rng.randn(self.dataset_size, self.embedding_dim).astype(np.float32)
        
        # Generate test records
        self.test_records = []
        for i in range(self.dataset_size):
            record = AudioFeatureRecord(
                id=f"test_{i}",
                audio_path=f"/test/audio_{i}.wav",
                file_hash=f"hash_{i}",
                sample_rate=44100,
                duration=180.0,
                features={
                    "bpm": int(60 + (i % 120)),
                    "key": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][i % 12],
                    "genre": ["pop", "rock", "electronic", "jazz", "classical"][i % 5],
                    "energy": float(i % 100) / 100.0,
                    "danceability": float((i + 20) % 100) / 100.0
                },
                embedding=self.test_embeddings[i],
                metadata={
                    "artist": f"Artist_{i % 10}",
                    "album": f"Album_{i % 50}",
                    "year": 2020 + (i % 5),
                    "bitrate": 320000,
                    "channels": 2,
                    "tags": ["tag1", "tag2", f"tag{i%10}"],
                    "custom_metrics": {
                        "custom1": i % 100,
                        "custom2": (i * 3) % 100
                    }
                }
            )
            self.test_records.append(record)
        
        # Clear test database if needed
        if self.test_db:
            self._reset_test_database()
    
    def _reset_test_database(self):
        """Reset the test database."""
        logger.info("Resetting test database...")
        try:
            # Connect to postgres database to drop/create test database
            import psycopg2
            conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/postgres")
            conn.autocommit = True
            
            with conn.cursor() as cur:
                # Drop and recreate database
                cur.execute(f"DROP DATABASE IF EXISTS samplemind_benchmark")
                cur.execute(f"CREATE DATABASE samplemind_benchmark")
                
                # Enable extensions
                cur.execute("""
                    \c samplemind_benchmark
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE EXTENSION IF NOT EXISTS pg_trgm;
                    CREATE EXTENSION IF NOT EXISTS btree_gin;
                """)
                
            logger.info("Test database reset complete")
            
        except Exception as e:
            logger.error(f"Error resetting test database: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def run_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and return results."""
        logger.info("Starting benchmarks...")
        results = {
            "dataset_size": self.dataset_size,
            "batch_size": self.batch_size,
            "embedding_dim": self.embedding_dim,
            "benchmarks": {}
        }
        
        # 1. Batch insertion benchmark
        logger.info("Running batch insertion benchmark...")
        insert_results = self.benchmark_batch_insertion()
        results["benchmarks"]["batch_insertion"] = insert_results
        
        # 2. Similarity search benchmark
        logger.info("Running similarity search benchmark...")
        search_results = self.benchmark_similarity_search()
        results["benchmarks"]["similarity_search"] = search_results
        
        # 3. Metadata filtering benchmark
        logger.info("Running metadata filtering benchmark...")
        filter_results = self.benchmark_metadata_filtering()
        results["benchmarks"]["metadata_filtering"] = filter_results
        
        # 4. Mixed workload benchmark
        logger.info("Running mixed workload benchmark...")
        mixed_results = self.benchmark_mixed_workload()
        results["benchmarks"]["mixed_workload"] = mixed_results
        
        # 5. Database statistics
        logger.info("Collecting database statistics...")
        stats = self.store.get_database_stats()
        results["database_stats"] = stats
        
        logger.info("All benchmarks completed")
        return results
    
    def benchmark_batch_insertion(self) -> Dict[str, Any]:
        """Benchmark batch insertion performance."""
        results = {}
        
        # Test different batch sizes
        for batch_size in [1, 10, 100, 1000, 10000]:
            if batch_size > len(self.test_records):
                continue
                
            logger.info(f"Testing batch size: {batch_size}")
            
            # Reset database
            if self.test_db:
                self._reset_test_database()
            
            # Time batch insertion
            start_time = time.time()
            inserted = 0
            
            for i in range(0, len(self.test_records), batch_size):
                batch = self.test_records[i:i + batch_size]
                self.store.batch_add_audio_features(batch, batch_size=batch_size)
                inserted += len(batch)
                
                if inserted >= self.dataset_size:
                    break
            
            duration = time.time() - start_time
            records_per_second = inserted / duration if duration > 0 else 0
            
            results[f"batch_size_{batch_size}"] = {
                "records_inserted": inserted,
                "duration_seconds": duration,
                "records_per_second": records_per_second
            }
            
            logger.info(
                f"Inserted {inserted} records in {duration:.2f}s "
                f"({records_per_second:.2f} records/s)"
            )
        
        return results
    
    def benchmark_similarity_search(self) -> Dict[str, Any]:
        """Benchmark similarity search performance."""
        results = {}
        
        # Make sure we have data
        if not self.store.get_audio_features("test_0"):
            logger.info("Loading test data...")
            self.store.batch_add_audio_features(self.test_records, batch_size=self.batch_size)
        
        # Test different search scenarios
        test_cases = [
            ("exact_match", self.test_embeddings[0], 1, 0.0, 0.0),
            ("approximate_10", self.test_embeddings[0], 10, 0.3, 0.5),
            ("approximate_100", self.test_embeddings[0], 100, 0.5, 0.8),
        ]
        
        for name, query_embedding, k, min_similarity, max_similarity in test_cases:
            logger.info(f"Running search test: {name}")
            
            # Warmup
            for _ in range(2):
                self.store.find_similar(query_embedding, limit=k)
            
            # Benchmark
            start_time = time.time()
            
            # Run multiple queries for more accurate timing
            num_queries = 100
            distances = []
            
            for _ in range(num_queries):
                # Add some noise to the query
                noise = np.random.normal(0, 0.1, self.embedding_dim).astype(np.float32)
                noisy_embedding = query_embedding + noise
                noisy_embedding = noisy_embedding / np.linalg.norm(noisy_embedding)
                
                results = self.store.find_similar(noisy_embedding, limit=k)
                if results:
                    distances.extend(r['distance'] for r in results)
            
            duration = time.time() - start_time
            avg_time = (duration / num_queries) * 1000  # ms per query
            
            # Calculate statistics
            if distances:
                distances = np.array(distances)
                stats = {
                    "queries_per_second": num_queries / duration,
                    "avg_query_time_ms": avg_time,
                    "avg_distance": float(np.mean(distances)),
                    "min_distance": float(np.min(distances)),
                    "max_distance": float(np.max(distances)),
                    "num_results": len(distances) / num_queries
                }
            else:
                stats = {"error": "No results found"}
            
            results[name] = stats
            logger.info(f"Search {name}: {avg_time:.2f}ms/query")
        
        return results
    
    def benchmark_metadata_filtering(self) -> Dict[str, Any]:
        """Benchmark metadata filtering performance."""
        results = {}
        
        # Make sure we have data
        if not self.store.get_audio_features("test_0"):
            logger.info("Loading test data...")
            self.store.batch_add_audio_features(self.test_records, batch_size=self.batch_size)
        
        # Test different filter scenarios
        test_cases = [
            ("exact_match", {"genre": "rock"}),
            ("multiple_conditions", {"genre": "jazz", "year": 2022}),
            ("jsonb_contains", {"tags": ["tag1", "tag2"]}),
            ("range_query", {"bpm": {"gt": 100, "lt": 120}}),
        ]
        
        for name, filters in test_cases:
            logger.info(f"Running filter test: {name}")
            
            # Warmup
            for _ in range(2):
                self.store.query_by_metadata(filters, limit=10)
            
            # Benchmark
            start_time = time.time()
            num_queries = 100
            result_counts = []
            
            for _ in range(num_queries):
                results = self.store.query_by_metadata(filters, limit=100)
                result_counts.append(len(results))
            
            duration = time.time() - start_time
            avg_time = (duration / num_queries) * 1000  # ms per query
            
            stats = {
                "queries_per_second": num_queries / duration,
                "avg_query_time_ms": avg_time,
                "avg_results": float(np.mean(result_counts)),
                "filter": str(filters)
            }
            
            results[name] = stats
            logger.info(f"Filter {name}: {avg_time:.2f}ms/query, {stats['avg_results']:.1f} avg results")
        
        return results
    
    def benchmark_mixed_workload(self) -> Dict[str, Any]:
        """Benchmark mixed read/write workload."""
        results = {}
        
        # Reset database
        if self.test_db:
            self._reset_test_database()
        
        # Insert initial data (half the dataset)
        half_size = len(self.test_records) // 2
        self.store.batch_add_audio_features(
            self.test_records[:half_size], 
            batch_size=self.batch_size
        )
        
        # Define workload
        def mixed_workload():
            # 70% reads, 20% writes, 10% updates
            r = np.random.random()
            
            if r < 0.7:  # Read
                # Random similarity search
                idx = np.random.randint(0, half_size)
                self.store.find_similar(
                    self.test_embeddings[idx], 
                    limit=10
                )
                return "read"
                
            elif r < 0.9:  # Write
                # Insert new record
                idx = half_size + np.random.randint(0, len(self.test_records) - half_size)
                self.store.add_audio_features(self.test_records[idx])
                return "write"
                
            else:  # Update
                # Update existing record
                idx = np.random.randint(0, half_size)
                record = self.store.get_audio_features(f"test_{idx}")
                if record:
                    record.metadata["updated"] = True
                    self.store.add_audio_features(record)
                return "update"
        
        # Warmup
        for _ in range(10):
            mixed_workload()
        
        # Run benchmark
        num_operations = 1000
        operation_counts = {"read": 0, "write": 0, "update": 0}
        operation_times = {"read": [], "write": [], "update": []}
        
        logger.info(f"Running mixed workload ({num_operations} operations)...")
        
        for _ in range(num_operations):
            start_time = time.perf_counter()
            op_type = mixed_workload()
            duration = (time.perf_counter() - start_time) * 1000  # ms
            
            operation_counts[op_type] += 1
            operation_times[op_type].append(duration)
        
        # Calculate statistics
        stats = {
            "operations_per_second": num_operations / (sum(sum(times) for times in operation_times.values()) / 1000),
            "operation_counts": operation_counts,
            "operation_stats": {}
        }
        
        for op_type, times in operation_times.items():
            if times:
                stats["operation_stats"][op_type] = {
                    "count": len(times),
                    "avg_time_ms": np.mean(times),
                    "p50_ms": np.percentile(times, 50),
                    "p95_ms": np.percentile(times, 95),
                    "p99_ms": np.percentile(times, 99),
                    "max_ms": max(times)
                }
        
        results["mixed_workload"] = stats
        return results

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run PgVectorStore benchmarks")
    parser.add_argument(
        "--dataset-size", 
        type=int, 
        default=10000,
        help="Number of records to use for testing"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=1000,
        help="Batch size for batch operations"
    )
    parser.add_argument(
        "--embedding-dim", 
        type=int, 
        default=1536,
        help="Dimensionality of the embedding vectors"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="benchmark_results.json",
        help="Output file for benchmark results"
    )
    return parser.parse_args()

def main():
    """Run benchmarks and save results."""
    args = parse_args()
    
    # Initialize benchmark
    benchmark = VectorStoreBenchmark(
        dataset_size=args.dataset_size,
        batch_size=args.batch_size,
        embedding_dim=args.embedding_dim
    )
    
    try:
        # Set up test data
        benchmark.setup()
        
        # Run benchmarks
        results = benchmark.run_benchmarks()
        
        # Save results
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Benchmark results saved to {args.output}")
        
        # Print summary
        print("\n=== Benchmark Summary ===")
        print(f"Dataset size: {results['dataset_size']}")
        print(f"Batch size: {results['batch_size']}")
        print(f"Embedding dimension: {results['embedding_dim']}")
        
        print("\n=== Performance Metrics ===")
        for benchmark_name, metrics in results["benchmarks"].items():
            print(f"\n{benchmark_name.upper()}:")
            if isinstance(metrics, dict):
                for metric_name, value in metrics.items():
                    if isinstance(value, dict):
                        print(f"  {metric_name}:")
                        for k, v in value.items():
                            if isinstance(v, (int, float)):
                                if k.endswith("_ms"):
                                    print(f"    {k}: {v:.2f} ms")
                                elif k.endswith("_s"):
                                    print(f"    {k}: {v:.2f} s")
                                else:
                                    print(f"    {k}: {v}")
                            else:
                                print(f"    {k}: {v}")
                    else:
                        print(f"  {metric_name}: {value}")
        
        print("\n=== Database Statistics ===")
        stats = results.get("database_stats", {})
        print(f"Total records: {stats.get('total_records', 'N/A')}")
        print(f"Unique files: {stats.get('unique_files', 'N/A')}")
        print(f"Oldest record: {stats.get('oldest_record', 'N/A')}")
        print(f"Newest record: {stats.get('newest_record', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1
    finally:
        # Clean up
        if hasattr(benchmark, 'store'):
            benchmark.store.close_all_connections()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
