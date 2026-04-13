"""
Database performance optimization module for OSINT-OS platform.

Provides connection pooling, query optimization, slow query logging,
and performance monitoring for production workloads.
"""

import time
import logging
import asyncio
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Callable
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DatabasePerformanceManager:
    """Manages database performance optimization and monitoring."""
    
    def __init__(self, database_url: str, **kwargs):
        self.database_url = database_url
        self.engine_kwargs = kwargs
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        
        # Performance monitoring
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'max_time': 0.0,
            'min_time': float('inf'),
            'recent_times': deque(maxlen=100)
        })
        
        self.slow_queries = deque(maxlen=1000)
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
        
        # Performance thresholds
        self.slow_query_threshold = kwargs.get('slow_query_threshold', 1.0)  # seconds
        self.enable_query_logging = kwargs.get('enable_query_logging', True)
        self.enable_connection_pooling = kwargs.get('enable_connection_pooling', True)
        
        self._setup_engine()
        self._setup_monitoring()
    
    def _setup_engine(self):
        """Configure database engine with optimal settings."""
        engine_config = {
            'echo': False,  # Disable SQL echo in production
            'future': True,  # Use SQLAlchemy 2.0 style
        }
        
        # Configure based on database type
        if 'sqlite' in self.database_url.lower():
            # SQLite-specific optimizations
            engine_config.update({
                'poolclass': StaticPool,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 30,
                    'isolation_level': None,  # Autocommit mode for better performance
                },
                'pool_pre_ping': True,
            })
            
            # SQLite performance pragmas
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
                cursor.execute("PRAGMA cache_size=10000")  # 10MB cache
                cursor.execute("PRAGMA temp_store=MEMORY")  # Temporary tables in memory
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
                cursor.execute("PRAGMA optimize")  # Optimize database
                cursor.close()
                
        elif 'postgresql' in self.database_url.lower():
            # PostgreSQL-specific optimizations
            engine_config.update({
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 30,
                'pool_pre_ping': True,
                'pool_recycle': 3600,  # Recycle connections after 1 hour
                'connect_args': {
                    'application_name': 'osint_platform',
                    'connect_timeout': 10,
                    'command_timeout': 30,
                }
            })
            
        else:
            # Default configuration for other databases
            engine_config.update({
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
            })
        
        # Update with user-provided kwargs
        engine_config.update(self.engine_kwargs)
        
        self.engine = create_engine(self.database_url, **engine_config)
        self.session_factory = sessionmaker(bind=self.engine)
        
        logger.info(f"Database engine configured for {self.database_url.split('://')[0]}")
    
    def _setup_monitoring(self):
        """Setup performance monitoring and logging."""
        if not self.enable_query_logging:
            return
        
        # Query performance monitoring
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - context._query_start_time
            
            # Update query statistics
            query_key = self._normalize_query(statement)
            stats = self.query_stats[query_key]
            stats['count'] += 1
            stats['total_time'] += total
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['max_time'] = max(stats['max_time'], total)
            stats['min_time'] = min(stats['min_time'], total)
            stats['recent_times'].append(total)
            
            # Log slow queries
            if total > self.slow_query_threshold:
                slow_query = {
                    'timestamp': datetime.utcnow(),
                    'duration': total,
                    'statement': statement,
                    'parameters': str(parameters)[:200],  # Truncate long parameters
                }
                self.slow_queries.append(slow_query)
                logger.warning(f"Slow query ({total:.3f}s): {statement[:100]}...")
        
        # Connection pool monitoring
        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            self.connection_stats['total_connections'] += 1
            self.connection_stats['active_connections'] += 1
        
        @event.listens_for(self.engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            if hasattr(connection_record, 'info') and connection_record.info.get('from_pool'):
                self.connection_stats['pool_hits'] += 1
            else:
                self.connection_stats['pool_misses'] += 1
        
        @event.listens_for(self.engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            self.connection_stats['active_connections'] = max(0, self.connection_stats['active_connections'] - 1)
    
    def _normalize_query(self, statement: str) -> str:
        """Normalize SQL statement for grouping similar queries."""
        # Remove parameter values and normalize whitespace
        normalized = ' '.join(statement.split())
        # Replace common parameter patterns
        for char in ['?', '%s', ':1', ':2', ':3', ':4', ':5']:
            normalized = normalized.replace(char, '?')
        return normalized[:100]  # Truncate for grouping
    
    @contextmanager
    def get_session(self):
        """Get a database session with proper error handling."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a query with performance monitoring."""
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
            except SQLAlchemyError as e:
                logger.error(f"Query execution error: {e}")
                raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        # Calculate top slow queries
        top_slow_queries = list(self.slow_queries)
        top_slow_queries.sort(key=lambda x: x['duration'], reverse=True)
        top_slow_queries = top_slow_queries[:10]
        
        # Calculate top frequent queries
        top_frequent = sorted(
            self.query_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        # Calculate top slowest average queries
        top_slowest_avg = sorted(
            self.query_stats.items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        )[:10]
        
        return {
            'connection_stats': self.connection_stats.copy(),
            'query_count': len(self.query_stats),
            'slow_query_count': len(self.slow_queries),
            'slow_query_threshold': self.slow_query_threshold,
            'top_slow_queries': [
                {
                    'timestamp': q['timestamp'].isoformat(),
                    'duration': q['duration'],
                    'statement': q['statement'][:100]
                }
                for q in top_slow_queries
            ],
            'top_frequent_queries': [
                {
                    'query': query,
                    'count': stats['count'],
                    'avg_time': stats['avg_time'],
                    'max_time': stats['max_time']
                }
                for query, stats in top_frequent
            ],
            'top_slowest_avg_queries': [
                {
                    'query': query,
                    'avg_time': stats['avg_time'],
                    'count': stats['count'],
                    'max_time': stats['max_time']
                }
                for query, stats in top_slowest_avg
            ]
        }
    
    def analyze_table_performance(self, table_name: str) -> Dict[str, Any]:
        """Analyze performance for a specific table."""
        with self.get_session() as session:
            # Get table statistics (PostgreSQL specific, fallback for others)
            try:
                if 'postgresql' in self.database_url.lower():
                    result = session.execute(text(f"""
                        SELECT 
                            schemaname,
                            tablename,
                            attname,
                            n_distinct,
                            correlation
                        FROM pg_stats 
                        WHERE tablename = '{table_name}'
                        ORDER BY schemaname, tablename, attname
                    """))
                    stats = [dict(row._mapping) for row in result]
                else:
                    # SQLite fallback - basic table info
                    result = session.execute(text(f"SELECT COUNT(*) as row_count FROM {table_name}"))
                    row_count = result.fetchone()[0]
                    stats = [{'row_count': row_count}]
                
                # Get index usage if available
                try:
                    if 'postgresql' in self.database_url.lower():
                        index_result = session.execute(text(f"""
                            SELECT 
                                indexname,
                                idx_scan,
                                idx_tup_read,
                                idx_tup_fetch
                            FROM pg_stat_user_indexes 
                            WHERE tablename = '{table_name}'
                        """))
                        index_stats = [dict(row._mapping) for row in index_result]
                    else:
                        index_stats = []
                except:
                    index_stats = []
                
                return {
                    'table_name': table_name,
                    'column_stats': stats,
                    'index_stats': index_stats,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Table analysis failed for {table_name}: {e}")
                return {
                    'table_name': table_name,
                    'error': str(e),
                    'analyzed_at': datetime.utcnow().isoformat()
                }
    
    def optimize_database(self) -> Dict[str, Any]:
        """Run database optimization routines."""
        optimization_results = {}
        
        with self.get_session() as session:
            try:
                if 'sqlite' in self.database_url.lower():
                    # SQLite optimizations
                    session.execute(text("PRAGMA optimize"))
                    session.execute(text("VACUUM"))
                    session.execute(text("ANALYZE"))
                    optimization_results['sqlite'] = {
                        'vacuum': 'completed',
                        'analyze': 'completed',
                        'optimize': 'completed'
                    }
                
                elif 'postgresql' in self.database_url.lower():
                    # PostgreSQL optimizations
                    session.execute(text("ANALYZE"))
                    session.execute(text("VACUUM ANALYZE"))
                    optimization_results['postgresql'] = {
                        'analyze': 'completed',
                        'vacuum_analyze': 'completed'
                    }
                
                session.commit()
                optimization_results['status'] = 'success'
                optimization_results['timestamp'] = datetime.utcnow().isoformat()
                
            except Exception as e:
                optimization_results['status'] = 'error'
                optimization_results['error'] = str(e)
                logger.error(f"Database optimization failed: {e}")
        
        return optimization_results
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.query_stats.clear()
        self.slow_queries.clear()
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
        logger.info("Performance statistics reset")

# Global database performance manager instance
_db_manager: Optional[DatabasePerformanceManager] = None

def get_database_manager() -> DatabasePerformanceManager:
    """Get the global database performance manager."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_database_manager() first.")
    return _db_manager

def init_database_manager(database_url: str, **kwargs) -> DatabasePerformanceManager:
    """Initialize the global database performance manager."""
    global _db_manager
    _db_manager = DatabasePerformanceManager(database_url, **kwargs)
    return _db_manager

# Context manager for database operations
@contextmanager
def database_session():
    """Context manager for database sessions."""
    db_manager = get_database_manager()
    with db_manager.get_session() as session:
        yield session

# Decorator for monitoring function performance
def monitor_query_performance(func: Callable) -> Callable:
    """Decorator to monitor database query performance in functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"Function {func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper