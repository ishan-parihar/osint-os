"""
CRITICAL DATABASE PERFORMANCE ANALYSIS AND OPTIMIZATION
========================================================

PRODUCTION READINESS ASSESSMENT - IMMEDIATE ACTION REQUIRED

This script performs comprehensive database performance analysis and implements
strategic optimizations for OSINT-OS platform production deployment.
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from app.core.database_performance import DatabasePerformanceManager
from app.models.sqlalchemy.base import Base
from app.models.sqlalchemy.investigation import (
    Investigation, InvestigationTarget, CollectedEvidence, 
    AnalysisResult, ThreatAssessment, AgentAssignment
)
from app.models.sqlalchemy.osint_core import (
    DataSource, EvidenceChain, ThreatIndicator, CollectionJob
)
from app.models.sqlalchemy.ai_investigation import (
    AIInvestigation, AgentExecutionLog, InvestigationState
)
from app.models.sqlalchemy.audit import (
    AuditLog, SystemEvent
)

class CriticalDatabaseOptimizer:
    """CRITICAL: Database performance optimizer for production readiness."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.inspector: Optional[inspect] = None
        self.db_manager: Optional[DatabasePerformanceManager] = None
        
        # Performance metrics
        self.analysis_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'database_type': database_url.split('://')[0] if '://' in database_url else 'unknown',
            'critical_issues': [],
            'missing_indexes': [],
            'slow_queries': [],
            'optimization_recommendations': [],
            'performance_metrics': {},
            'production_readiness': 'NOT_READY'
        }
        
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connections and managers."""
        print("🔧 SETTING UP DATABASE CONNECTIONS...")
        
        # Primary database connection
        self.engine = create_engine(self.database_url, echo=False)
        self.session_factory = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
        
        # Initialize performance manager
        self.db_manager = DatabasePerformanceManager(
            self.database_url,
            slow_query_threshold=0.5,  # 500ms threshold
            enable_query_logging=True,
            enable_connection_pooling=True
        )
        
        print("✅ Database connections established")
    
    def analyze_current_indexes(self) -> Dict[str, Any]:
        """CRITICAL: Analyze current database indexes."""
        print("\n🔍 ANALYZING CURRENT DATABASE INDEXES...")
        
        index_analysis = {}
        tables = self.inspector.get_table_names()
        
        for table_name in tables:
            try:
                indexes = self.inspector.get_indexes(table_name)
                columns = self.inspector.get_columns(table_name)
                
                index_analysis[table_name] = {
                    'indexes': indexes,
                    'columns': [col['name'] for col in columns],
                    'column_count': len(columns),
                    'index_count': len(indexes),
                    'has_primary_key': any(idx.get('primary_key', False) for idx in indexes)
                }
                
                # Check for critical missing indexes
                self._check_missing_indexes(table_name, columns, indexes)
                
            except Exception as e:
                print(f"⚠️  Error analyzing table {table_name}: {e}")
                index_analysis[table_name] = {'error': str(e)}
        
        self.analysis_results['index_analysis'] = index_analysis
        print(f"✅ Analyzed {len(tables)} tables")
        return index_analysis
    
    def _check_missing_indexes(self, table_name: str, columns: List[Dict], indexes: List[Dict]):
        """Check for critical missing indexes based on OSINT query patterns."""
        existing_index_columns = set()
        for idx in indexes:
            existing_index_columns.update(idx['column_names'])
        
        column_names = [col['name'] for col in columns]
        
        # Define critical index requirements for OSINT workloads
        critical_requirements = {
            'investigations': [
                'status', 'priority', 'current_phase', 'created_at', 'updated_at'
            ],
            'investigation_targets': [
                'investigation_uuid', 'type', 'status', 'priority', 'identifier'
            ],
            'collected_evidence': [
                'investigation_uuid', 'source_type', 'reliability_score', 
                'relevance_score', 'verified', 'created_at'
            ],
            'analysis_results': [
                'investigation_uuid', 'evidence_uuid', 'analysis_type', 
                'confidence', 'analyst_id', 'created_at'
            ],
            'threat_assessments': [
                'investigation_uuid', 'threat_level', 'risk_score', 
                'status', 'threat_type', 'created_at'
            ],
            'agent_assignments': [
                'investigation_uuid', 'agent_id', 'agent_type', 'status', 'assigned_at'
            ],
            'evidence_chains': [
                'evidence_uuid', 'handler', 'action', 'created_at'
            ],
            'threat_indicators': [
                'indicator_type', 'value', 'source', 'severity', 'is_active', 'created_at'
            ],
            'audit_logs': [
                'event_type', 'user_id', 'timestamp', 'severity', 'resource_type'
            ],
            'ai_investigations': [
                'investigation_id', 'status', 'created_at'
            ],
            'agent_execution_logs': [
                'investigation_id', 'agent_name', 'status', 'created_at'
            ]
        }
        
        # Check missing indexes for this table
        if table_name in critical_requirements:
            required_columns = critical_requirements[table_name]
            for required_col in required_columns:
                if required_col in column_names and required_col not in existing_index_columns:
                    missing_index = {
                        'table': table_name,
                        'column': required_col,
                        'priority': 'HIGH' if table_name in ['investigations', 'collected_evidence', 'investigation_targets'] else 'MEDIUM',
                        'reason': f'Critical for {table_name} query performance'
                    }
                    self.analysis_results['missing_indexes'].append(missing_index)
                    
                    if missing_index['priority'] == 'HIGH':
                        self.analysis_results['critical_issues'].append(
                            f"MISSING HIGH-PRIORITY INDEX: {table_name}.{required_col}"
                        )
    
    def analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow queries and performance bottlenecks."""
        print("\n⚡ ANALYZING SLOW QUERIES AND PERFORMANCE...")
        
        with self.db_manager.get_session() as session:
            # Test critical OSINT queries
            test_queries = [
                {
                    'name': 'Active Investigations Query',
                    'query': """
                        SELECT COUNT(*) FROM investigations 
                        WHERE status IN ('ACTIVE', 'PLANNING') 
                        AND created_at >= datetime('now', '-7 days')
                    """,
                    'expected_time': 0.1
                },
                {
                    'name': 'Evidence Collection Query',
                    'query': """
                        SELECT e.*, i.title 
                        FROM collected_evidence e 
                        JOIN investigations i ON e.investigation_uuid = i.uuid 
                        WHERE e.reliability_score > 0.7 
                        ORDER BY e.collected_at DESC 
                        LIMIT 100
                    """,
                    'expected_time': 0.2
                },
                {
                    'name': 'Threat Assessment Query',
                    'query': """
                        SELECT ta.*, i.title 
                        FROM threat_assessments ta 
                        JOIN investigations i ON ta.investigation_uuid = i.uuid 
                        WHERE ta.threat_level IN ('HIGH', 'CRITICAL') 
                        ORDER BY ta.risk_score DESC 
                        LIMIT 50
                    """,
                    'expected_time': 0.15
                },
                {
                    'name': 'Agent Performance Query',
                    'query': """
                        SELECT agent_type, status, COUNT(*) as count 
                        FROM agent_assignments 
                        WHERE assigned_at >= datetime('now', '-1 day') 
                        GROUP BY agent_type, status
                    """,
                    'expected_time': 0.1
                }
            ]
            
            query_results = []
            for test_query in test_queries:
                try:
                    start_time = time.time()
                    result = session.execute(text(test_query['query']))
                    rows = result.fetchall()
                    duration = time.time() - start_time
                    
                    performance_issue = duration > test_query['expected_time']
                    
                    query_result = {
                        'name': test_query['name'],
                        'duration': duration,
                        'expected_time': test_query['expected_time'],
                        'rows_returned': len(rows),
                        'performance_issue': performance_issue,
                        'slow_factor': duration / test_query['expected_time'] if performance_issue else 1.0
                    }
                    
                    query_results.append(query_result)
                    
                    if performance_issue:
                        self.analysis_results['slow_queries'].append(query_result)
                        self.analysis_results['critical_issues'].append(
                            f"SLOW QUERY: {test_query['name']} - {duration:.3f}s (expected {test_query['expected_time']}s)"
                        )
                    
                except Exception as e:
                    error_result = {
                        'name': test_query['name'],
                        'error': str(e),
                        'performance_issue': True
                    }
                    query_results.append(error_result)
                    self.analysis_results['critical_issues'].append(
                        f"QUERY ERROR: {test_query['name']} - {str(e)}"
                    )
        
        self.analysis_results['query_performance'] = query_results
        print(f"✅ Tested {len(test_queries)} critical queries")
        return query_results
    
    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic optimization recommendations."""
        print("\n💡 GENERATING OPTIMIZATION RECOMMENDATIONS...")
        
        recommendations = []
        
        # Index recommendations
        if self.analysis_results['missing_indexes']:
            high_priority_missing = [idx for idx in self.analysis_results['missing_indexes'] if idx['priority'] == 'HIGH']
            if high_priority_missing:
                recommendations.append({
                    'category': 'CRITICAL_INDEXES',
                    'priority': 'CRITICAL',
                    'action': 'IMMEDIATE_MIGRATION_REQUIRED',
                    'description': f"Add {len(high_priority_missing)} high-performance indexes",
                    'details': high_priority_missing,
                    'estimated_impact': '50-80% query performance improvement',
                    'implementation_time': '5-10 minutes'
                })
        
        # Query optimization
        if self.analysis_results['slow_queries']:
            recommendations.append({
                'category': 'QUERY_OPTIMIZATION',
                'priority': 'HIGH',
                'action': 'OPTIMIZE_SLOW_QUERIES',
                'description': f"Optimize {len(self.analysis_results['slow_queries'])} slow queries",
                'details': self.analysis_results['slow_queries'],
                'estimated_impact': '30-60% performance improvement',
                'implementation_time': '15-30 minutes'
            })
        
        # Connection pooling
        recommendations.append({
            'category': 'CONNECTION_OPTIMIZATION',
            'priority': 'HIGH',
            'action': 'CONFIGURE_CONNECTION_POOLING',
            'description': 'Optimize database connection pool settings',
            'details': {
                'recommended_pool_size': 20,
                'max_overflow': 30,
                'pool_recycle': 3600,
                'pool_pre_ping': True
            },
            'estimated_impact': '20-40% throughput improvement',
            'implementation_time': '2-5 minutes'
        })
        
        # Database-specific optimizations
        if 'sqlite' in self.database_url.lower():
            recommendations.append({
                'category': 'SQLITE_OPTIMIZATION',
                'priority': 'MEDIUM',
                'action': 'ENABLE_SQLITE_PERFORMANCE',
                'description': 'Enable SQLite performance pragmas',
                'details': {
                    'journal_mode': 'WAL',
                    'synchronous': 'NORMAL',
                    'cache_size': '10000',
                    'mmap_size': '268435456'
                },
                'estimated_impact': '15-25% performance improvement',
                'implementation_time': '1-2 minutes'
            })
        elif 'postgresql' in self.database_url.lower():
            recommendations.append({
                'category': 'POSTGRESQL_OPTIMIZATION',
                'priority': 'MEDIUM',
                'action': 'POSTGRESQL_TUNING',
                'description': 'Optimize PostgreSQL configuration',
                'details': {
                    'shared_buffers': '256MB',
                    'effective_cache_size': '1GB',
                    'work_mem': '4MB',
                    'maintenance_work_mem': '64MB'
                },
                'estimated_impact': '25-35% performance improvement',
                'implementation_time': '10-15 minutes'
            })
        
        # Monitoring setup
        recommendations.append({
            'category': 'MONITORING',
            'priority': 'HIGH',
            'action': 'SETUP_PERFORMANCE_MONITORING',
            'description': 'Configure comprehensive database monitoring',
            'details': {
                'slow_query_logging': True,
                'connection_pool_monitoring': True,
                'query_performance_tracking': True,
                'alert_threshold': '500ms'
            },
            'estimated_impact': 'Early detection of performance issues',
            'implementation_time': '5-10 minutes'
        })
        
        self.analysis_results['optimization_recommendations'] = recommendations
        print(f"✅ Generated {len(recommendations)} optimization recommendations")
        return recommendations
    
    def assess_production_readiness(self) -> str:
        """Assess overall production readiness."""
        print("\n🎯 ASSESSING PRODUCTION READINESS...")
        
        critical_count = len(self.analysis_results['critical_issues'])
        slow_query_count = len(self.analysis_results['slow_queries'])
        missing_index_count = len([idx for idx in self.analysis_results['missing_indexes'] if idx['priority'] == 'HIGH'])
        
        # Production readiness criteria
        if critical_count == 0 and slow_query_count == 0 and missing_index_count == 0:
            readiness = 'PRODUCTION_READY'
            status_icon = '✅'
        elif critical_count <= 2 and slow_query_count <= 1 and missing_index_count <= 3:
            readiness = 'READY_WITH_OPTIMIZATIONS'
            status_icon = '⚠️'
        else:
            readiness = 'NOT_READY'
            status_icon = '🚨'
        
        self.analysis_results['production_readiness'] = readiness
        self.analysis_results['readiness_score'] = max(0, 100 - (critical_count * 20) - (slow_query_count * 10) - (missing_index_count * 5))
        
        print(f"{status_icon} PRODUCTION READINESS: {readiness}")
        print(f"📊 READINESS SCORE: {self.analysis_results['readiness_score']}/100")
        print(f"🚨 CRITICAL ISSUES: {critical_count}")
        print(f"⚡ SLOW QUERIES: {slow_query_count}")
        print(f"📈 MISSING INDEXES: {missing_index_count}")
        
        return readiness
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        print("\n📋 GENERATING PERFORMANCE REPORT...")
        
        report = f"""
# 🚨 CRITICAL DATABASE PERFORMANCE OPTIMIZATION REPORT
## OSINT-OS Platform Production Readiness Assessment
**Generated: {datetime.utcnow().isoformat()}**

---

## 📊 EXECUTIVE SUMMARY
**Production Readiness: {self.analysis_results['production_readiness']}**
**Readiness Score: {self.analysis_results['readiness_score']}/100**
**Database Type: {self.analysis_results['database_type']}**

---

## 🚨 CRITICAL ISSUES ({len(self.analysis_results['critical_issues'])})
"""
        
        for issue in self.analysis_results['critical_issues']:
            report += f"- **{issue}**\n"
        
        report += f"""

---

## 📈 MISSING PERFORMANCE INDEXES ({len(self.analysis_results['missing_indexes'])})
"""
        
        high_priority = [idx for idx in self.analysis_results['missing_indexes'] if idx['priority'] == 'HIGH']
        medium_priority = [idx for idx in self.analysis_results['missing_indexes'] if idx['priority'] == 'MEDIUM']
        
        if high_priority:
            report += "\n### HIGH PRIORITY (Immediate Action Required)\n"
            for idx in high_priority:
                report += f"- **{idx['table']}.{idx['column']}** - {idx['reason']}\n"
        
        if medium_priority:
            report += "\n### MEDIUM PRIORITY\n"
            for idx in medium_priority:
                report += f"- **{idx['table']}.{idx['column']}** - {idx['reason']}\n"
        
        report += f"""

---

## ⚡ SLOW QUERY ANALYSIS ({len(self.analysis_results['slow_queries'])})
"""
        
        if self.analysis_results['slow_queries']:
            for query in self.analysis_results['slow_queries']:
                if 'duration' in query:
                    report += f"- **{query['name']}**: {query['duration']:.3f}s (expected {query['expected_time']}s) - {query['slow_factor']:.1f}x slower\n"
                else:
                    report += f"- **{query['name']}**: ERROR - {query['error']}\n"
        else:
            report += "✅ No slow queries detected\n"
        
        report += f"""

---

## 💡 OPTIMIZATION RECOMMENDATIONS
"""
        
        for rec in self.analysis_results['optimization_recommendations']:
            report += f"""
### {rec['category']} (Priority: {rec['priority']})
**Action**: {rec['action']}
**Description**: {rec['description']}
**Estimated Impact**: {rec['estimated_impact']}
**Implementation Time**: {rec['implementation_time']}

"""
        
        report += """

---

## 🎯 IMMEDIATE ACTION PLAN

### Phase 1: Critical Optimizations (5-15 minutes)
1. **Run performance index migration** - Add all missing high-priority indexes
2. **Configure connection pooling** - Optimize database connections
3. **Enable performance monitoring** - Setup slow query logging

### Phase 2: Query Optimization (15-30 minutes)
1. **Optimize slow queries** - Rewrite or add indexes for slow queries
2. **Database-specific tuning** - Apply SQLite/PostgreSQL optimizations
3. **Test query performance** - Verify improvements

### Phase 3: Monitoring & Maintenance (Ongoing)
1. **Setup performance alerts** - Monitor query times and connection health
2. **Regular performance audits** - Weekly performance reviews
3. **Index maintenance** - Periodic index analysis and optimization

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] **Run migration**: `alembic upgrade head`
- [ ] **Test performance**: Run query performance tests
- [ ] **Configure monitoring**: Enable slow query logging
- [ ] **Verify optimization**: Confirm performance improvements
- [ ] **Setup alerts**: Configure performance monitoring alerts
- [ ] **Document changes**: Update performance documentation

---

## 🚀 PRODUCTION DEPLOYMENT STATUS

"""
        
        if self.analysis_results['production_readiness'] == 'PRODUCTION_READY':
            report += "✅ **READY FOR PRODUCTION** - All critical optimizations complete\n"
        elif self.analysis_results['production_readiness'] == 'READY_WITH_OPTIMIZATIONS':
            report += "⚠️ **READY WITH MINOR OPTIMIZATIONS** - Implement recommended changes\n"
        else:
            report += "🚨 **NOT READY FOR PRODUCTION** - Critical optimizations required\n"
        
        # Save report to file
        report_filename = f"CRITICAL_DATABASE_PERFORMANCE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = Path(__file__).parent / report_filename
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved: {report_path}")
        self.analysis_results['report_file'] = str(report_path)
        
        return report
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete database performance analysis."""
        print("🚀 STARTING CRITICAL DATABASE PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        try:
            # Step 1: Analyze current indexes
            self.analyze_current_indexes()
            
            # Step 2: Test query performance
            self.analyze_slow_queries()
            
            # Step 3: Generate recommendations
            self.generate_optimization_recommendations()
            
            # Step 4: Assess production readiness
            self.assess_production_readiness()
            
            # Step 5: Generate report
            report = self.generate_performance_report()
            
            print("\n" + "=" * 60)
            print("🎯 CRITICAL DATABASE PERFORMANCE ANALYSIS COMPLETE")
            print("=" * 60)
            
            return self.analysis_results
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"🚨 {error_msg}")
            self.analysis_results['critical_issues'].append(error_msg)
            self.analysis_results['production_readiness'] = 'ANALYSIS_FAILED'
            return self.analysis_results


def main():
    """Main execution function."""
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./scrapecraft.db')
    
    print("🚨 CRITICAL DATABASE PERFORMANCE OPTIMIZATION")
    print("=" * 60)
    print(f"Database: {database_url}")
    print("Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = CriticalDatabaseOptimizer(database_url)
    
    # Run comprehensive analysis
    results = optimizer.run_comprehensive_analysis()
    
    # Print summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Production Readiness: {results['production_readiness']}")
    print(f"Readiness Score: {results.get('readiness_score', 0)}/100")
    print(f"Critical Issues: {len(results['critical_issues'])}")
    print(f"Missing Indexes: {len(results['missing_indexes'])}")
    print(f"Slow Queries: {len(results['slow_queries'])}")
    
    if results.get('report_file'):
        print(f"\n📋 Full Report: {results['report_file']}")
    
    # Exit with appropriate code
    if results['production_readiness'] == 'PRODUCTION_READY':
        print("\n✅ Database is PRODUCTION READY!")
        sys.exit(0)
    elif results['production_readiness'] == 'READY_WITH_OPTIMIZATIONS':
        print("\n⚠️ Database needs MINOR OPTIMIZATIONS")
        sys.exit(1)
    else:
        print("\n🚨 CRITICAL OPTIMIZATIONS REQUIRED")
        sys.exit(2)


if __name__ == "__main__":
    main()