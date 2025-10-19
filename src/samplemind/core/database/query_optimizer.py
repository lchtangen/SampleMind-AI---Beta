"""
Database Query Optimizer
Automatic query optimization and performance tuning
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QueryPlan:
    """Query execution plan analysis"""
    query: str
    plan: str
    total_cost: float
    execution_time_ms: float
    rows_estimated: int
    rows_actual: int
    uses_index: bool
    recommendations: List[str]


class QueryOptimizer:
    """
    Production query optimizer
    Analyzes and optimizes database queries automatically
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.slow_query_threshold_ms = 100.0
    
    async def analyze_query(self, query: str) -> QueryPlan:
        """
        Analyze query execution plan
        
        Args:
            query: SQL query to analyze
            
        Returns:
            QueryPlan with analysis and recommendations
        """
        # Get execution plan
        explain_result = await self.session.execute(
            text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
        )
        plan_json = explain_result.scalar()
        plan = plan_json[0]["Plan"]
        
        # Extract metrics
        total_cost = plan.get("Total Cost", 0)
        execution_time = plan_json[0].get("Execution Time", 0)
        rows_estimated = plan.get("Plan Rows", 0)
        rows_actual = plan.get("Actual Rows", 0)
        
        # Check if indexes are used
        uses_index = self._uses_index(plan)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(plan, query)
        
        return QueryPlan(
            query=query[:200],
            plan=str(plan),
            total_cost=total_cost,
            execution_time_ms=execution_time,
            rows_estimated=rows_estimated,
            rows_actual=rows_actual,
            uses_index=uses_index,
            recommendations=recommendations
        )
    
    def _uses_index(self, plan: Dict[str, Any]) -> bool:
        """Check if query uses index scan"""
        node_type = plan.get("Node Type", "")
        if "Index" in node_type:
            return True
        
        # Check child nodes
        for child in plan.get("Plans", []):
            if self._uses_index(child):
                return True
        
        return False
    
    def _generate_recommendations(self, plan: Dict[str, Any], query: str) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for sequential scans
        if "Seq Scan" in plan.get("Node Type", ""):
            recommendations.append(
                "Sequential scan detected. Consider adding an index on the filtered columns."
            )
        
        # Check for high cost
        if plan.get("Total Cost", 0) > 1000:
            recommendations.append(
                "High query cost detected. Review WHERE clauses and JOINs."
            )
        
        # Check for row estimation accuracy
        estimated = plan.get("Plan Rows", 0)
        actual = plan.get("Actual Rows", 0)
        if actual > 0 and abs(estimated - actual) / actual > 0.5:
            recommendations.append(
                "Row estimation is inaccurate. Run ANALYZE on the table."
            )
        
        # Check for nested loops with large datasets
        if plan.get("Node Type") == "Nested Loop" and actual > 1000:
            recommendations.append(
                "Nested loop with large dataset. Consider hash join or merge join."
            )
        
        return recommendations
    
    async def suggest_indexes(self, table_name: str) -> List[str]:
        """
        Suggest indexes based on query patterns
        
        Args:
            table_name: Table to analyze
            
        Returns:
            List of suggested CREATE INDEX statements
        """
        suggestions = []
        
        # Get table statistics
        stats_query = text("""
            SELECT 
                schemaname,
                tablename,
                attname as column_name,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE tablename = :table_name
            ORDER BY abs(correlation) DESC
        """)
        
        result = await self.session.execute(stats_query, {"table_name": table_name})
        stats = result.fetchall()
        
        # Suggest indexes for columns with high cardinality
        for row in stats:
            if row.n_distinct and abs(row.n_distinct) > 100:
                suggestions.append(
                    f"CREATE INDEX idx_{table_name}_{row.column_name} "
                    f"ON {table_name}({row.column_name});"
                )
        
        return suggestions
    
    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """
        Optimize table (VACUUM ANALYZE)
        
        Returns:
            Optimization results
        """
        logger.info(f"Optimizing table: {table_name}")
        
        # VACUUM ANALYZE
        await self.session.execute(text(f"VACUUM ANALYZE {table_name}"))
        
        # Get updated statistics
        stats = await self.get_table_stats(table_name)
        
        return {
            "table": table_name,
            "optimized_at": datetime.now().isoformat(),
            "stats": stats
        }
    
    async def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                n_live_tup as live_rows,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_analyze
            FROM pg_stat_user_tables
            WHERE tablename = :table_name
        """)
        
        result = await self.session.execute(query, {"table_name": table_name})
        row = result.fetchone()
        
        if row:
            return {
                "table": row.tablename,
                "total_size": row.total_size,
                "live_rows": row.live_rows,
                "dead_rows": row.dead_rows,
                "last_vacuum": row.last_vacuum,
                "last_analyze": row.last_analyze
            }
        
        return {}
    
    async def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get slowest queries from pg_stat_statements
        Requires pg_stat_statements extension
        """
        query = text("""
            SELECT 
                query,
                calls,
                total_exec_time / calls as avg_time_ms,
                total_exec_time,
                rows / calls as avg_rows
            FROM pg_stat_statements
            WHERE query NOT LIKE '%pg_stat_statements%'
            ORDER BY total_exec_time DESC
            LIMIT :limit
        """)
        
        try:
            result = await self.session.execute(query, {"limit": limit})
            return [
                {
                    "query": row.query[:200],
                    "calls": row.calls,
                    "avg_time_ms": float(row.avg_time_ms),
                    "total_time_ms": float(row.total_exec_time),
                    "avg_rows": int(row.avg_rows) if row.avg_rows else 0
                }
                for row in result.fetchall()
            ]
        except Exception as e:
            logger.warning(f"pg_stat_statements not available: {e}")
            return []
    
    async def get_missing_indexes(self) -> List[Dict[str, Any]]:
        """
        Find tables that might benefit from indexes
        Based on sequential scan statistics
        """
        query = text("""
            SELECT 
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                seq_tup_read / seq_scan as avg_seq_tup_read
            FROM pg_stat_user_tables
            WHERE seq_scan > 0
              AND idx_scan < seq_scan
            ORDER BY seq_tup_read DESC
            LIMIT 20
        """)
        
        result = await self.session.execute(query)
        
        return [
            {
                "table": f"{row.schemaname}.{row.tablename}",
                "seq_scans": row.seq_scan,
                "index_scans": row.idx_scan or 0,
                "avg_rows_per_scan": int(row.avg_seq_tup_read),
                "recommendation": "Consider adding index to reduce sequential scans"
            }
            for row in result.fetchall()
        ]
    
    async def get_index_usage(self) -> List[Dict[str, Any]]:
        """Get index usage statistics"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                indexrelname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)
        
        result = await self.session.execute(query)
        
        return [
            {
                "table": f"{row.schemaname}.{row.tablename}",
                "index": row.indexrelname,
                "scans": row.idx_scan,
                "tuples_read": row.idx_tup_read,
                "tuples_fetched": row.idx_tup_fetch,
                "size": row.index_size,
                "unused": row.idx_scan == 0
            }
            for row in result.fetchall()
        ]
    
    async def get_bloat_report(self) -> List[Dict[str, Any]]:
        """Get table bloat report"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                n_dead_tup,
                n_live_tup,
                CASE 
                    WHEN n_live_tup > 0 
                    THEN round(100.0 * n_dead_tup / n_live_tup, 2)
                    ELSE 0
                END as dead_tuple_percent
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 1000
            ORDER BY n_dead_tup DESC
        """)
        
        result = await self.session.execute(query)
        
        return [
            {
                "table": f"{row.schemaname}.{row.tablename}",
                "total_size": row.total_size,
                "dead_tuples": row.n_dead_tup,
                "live_tuples": row.n_live_tup,
                "bloat_percent": float(row.dead_tuple_percent),
                "needs_vacuum": row.dead_tuple_percent > 10
            }
            for row in result.fetchall()
        ]


# Automatic query optimization decorator
def optimized_query(cache_plan: bool = True):
    """
    Decorator to automatically optimize queries
    
    Usage:
        @optimized_query(cache_plan=True)
        async def get_users(session):
            return await session.execute(query)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute query
            result = await func(*args, **kwargs)
            
            # TODO: Add query plan caching and automatic optimization
            
            return result
        return wrapper
    return decorator


# Example usage
"""
async def optimize_database():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from src.samplemind.core.config import settings
    
    engine = create_async_engine(settings.database_url_async)
    
    async with AsyncSession(engine) as session:
        optimizer = QueryOptimizer(session)
        
        # Analyze a query
        query = "SELECT * FROM users WHERE email = 'test@example.com'"
        plan = await optimizer.analyze_query(query)
        print(f"Query cost: {plan.total_cost}")
        print(f"Uses index: {plan.uses_index}")
        for rec in plan.recommendations:
            print(f"- {rec}")
        
        # Get slow queries
        slow_queries = await optimizer.get_slow_queries()
        for q in slow_queries:
            print(f"{q['query']}: {q['avg_time_ms']:.2f}ms")
        
        # Find missing indexes
        missing_indexes = await optimizer.get_missing_indexes()
        for m in missing_indexes:
            print(f"{m['table']}: {m['recommendation']}")
        
        # Optimize table
        await optimizer.optimize_table('users')
"""
