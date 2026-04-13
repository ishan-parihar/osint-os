"""
Comprehensive database performance optimization indexes for OSINT-OS platform.

This migration adds strategic indexes to optimize OSINT workloads and investigation queries.
Revision ID: 004_performance_indexes
Revises: 001_osint_models
Create Date: 2025-11-13 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# Revision identifiers
revision = '004_performance_indexes'
down_revision = '001_osint_models'
branch_labels = None
depends_on = None


def upgrade():
    """Add comprehensive performance indexes for OSINT workloads."""
    
    # Get database dialect to handle SQLite vs PostgreSQL differences
    connection = op.get_bind()
    dialect_name = connection.dialect.name
    
    # INVESTIGATION TABLE INDEXES
    # Primary query patterns: status filtering, priority sorting, phase tracking
    print("Adding investigation table indexes...")
    
    # Composite indexes for common investigation queries
    if dialect_name == 'postgresql':
        # PostgreSQL specific indexes
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_investigations_status_priority 
            ON investigations (status, priority DESC, created_at DESC)
        """)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_investigations_phase_status 
            ON investigations (current_phase, status, updated_at DESC)
        """)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_investigations_classification 
            ON investigations (classification, status)
        """)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_investigations_active_by_date 
            ON investigations (created_at DESC) WHERE status IN ('ACTIVE', 'PLANNING')
        """)
    else:
        # SQLite indexes
        op.create_index('idx_investigations_status_priority', 'investigations', 
                       ['status', 'priority', 'created_at'])
        op.create_index('idx_investigations_phase_status', 'investigations', 
                       ['current_phase', 'status', 'updated_at'])
        op.create_index('idx_investigations_classification', 'investigations', 
                       ['classification', 'status'])
    
    # INVESTIGATION TARGETS INDEXES
    # Query patterns: finding targets by investigation, type, status
    print("Adding investigation targets indexes...")
    op.create_index('idx_investigation_targets_investigation_uuid', 'investigation_targets', 
                   ['investigation_uuid'])
    op.create_index('idx_investigation_targets_type_status', 'investigation_targets', 
                   ['type', 'status'])
    op.create_index('idx_investigation_targets_priority', 'investigation_targets', 
                   ['priority', 'status'])
    
    # EVIDENCE COLLECTION INDEXES
    # Critical for OSINT evidence retrieval and analysis
    print("Adding evidence collection indexes...")
    op.create_index('idx_collected_evidence_investigation_uuid', 'collected_evidence', 
                   ['investigation_uuid'])
    op.create_index('idx_collected_evidence_source_type', 'collected_evidence', 
                   ['source_type', 'created_at DESC'])
    op.create_index('idx_collected_evidence_reliability', 'collected_evidence', 
                   ['reliability_score DESC', 'relevance_score DESC'])
    op.create_index('idx_collected_evidence_verified', 'collected_evidence', 
                   ['verified', 'created_at DESC'])
    
    # THREAT INDICATORS (IOC) INDEXES
    # Critical for threat intelligence lookups
    print("Adding threat indicators indexes...")
    op.create_index('idx_threat_indicators_type_value', 'threat_indicators', 
                   ['indicator_type', 'value'])
    op.create_index('idx_threat_indicators_active', 'threat_indicators', 
                   ['is_active', 'indicator_type'])
    op.create_index('idx_threat_indicators_severity', 'threat_indicators', 
                   ['severity DESC', 'confidence DESC'])
    op.create_index('idx_threat_indicators_source', 'threat_indicators', 
                   ['source', 'first_seen DESC'])
    
    # DATA SOURCES INDEXES
    # For source management and reliability tracking
    print("Adding data sources indexes...")
    op.create_index('idx_data_sources_type_active', 'data_sources', 
                   ['source_type', 'is_active'])
    op.create_index('idx_data_sources_reliability', 'data_sources', 
                   ['reliability_score DESC', 'access_count DESC'])
    op.create_index('idx_data_sources_last_accessed', 'data_sources', 
                   ['last_accessed DESC'])
    
    # EVIDENCE CHAIN INDEXES
    # For audit trail and chain of custody
    print("Adding evidence chain indexes...")
    op.create_index('idx_evidence_chains_evidence_uuid', 'evidence_chains', 
                   ['evidence_uuid'])
    op.create_index('idx_evidence_chains_handler_action', 'evidence_chains', 
                   ['handler', 'action', 'created_at DESC'])
    op.create_index('idx_evidence_chains_timestamp', 'evidence_chains', 
                   ['created_at DESC'])
    
    # THREAT ACTORS INDEXES
    # For threat intelligence analysis
    print("Adding threat actors indexes...")
    op.create_index('idx_threat_actors_type_level', 'threat_actors', 
                   ['actor_type', 'threat_level'])
    op.create_index('idx_threat_actors_last_seen', 'threat_actors', 
                   ['last_seen DESC'])
    op.create_index('idx_threat_actors_confidence', 'threat_actors', 
                   ['confidence DESC'])
    
    # COLLECTION JOBS INDEXES
    # For job scheduling and monitoring
    print("Adding collection jobs indexes...")
    op.create_index('idx_collection_jobs_status_priority', 'collection_jobs', 
                   ['status', 'priority DESC'])
    op.create_index('idx_collection_jobs_next_run', 'collection_jobs', 
                   ['next_run', 'is_active'])
    op.create_index('idx_collection_jobs_type', 'collection_jobs', 
                   ['job_type', 'status'])
    
    # ANALYSIS RESULTS INDEXES
    # For evidence analysis workflow
    print("Adding analysis results indexes...")
    op.create_index('idx_analysis_results_investigation_evidence', 'analysis_results', 
                   ['investigation_uuid', 'evidence_uuid'])
    op.create_index('idx_analysis_results_type', 'analysis_results', 
                   ['analysis_type', 'created_at DESC'])
    op.create_index('idx_analysis_results_confidence', 'analysis_results', 
                   ['confidence DESC'])
    
    # THREAT ASSESSMENTS INDEXES
    # For risk management and reporting
    print("Adding threat assessments indexes...")
    op.create_index('idx_threat_assessments_investigation', 'threat_assessments', 
                   ['investigation_uuid'])
    op.create_index('idx_threat_assessments_level_risk', 'threat_assessments', 
                   ['threat_level', 'risk_score DESC'])
    op.create_index('idx_threat_assessments_status', 'threat_assessments', 
                   ['status', 'created_at DESC'])
    
    # WORKFLOW TRANSITIONS INDEXES
    # For workflow state tracking
    print("Adding workflow transitions indexes...")
    op.create_index('idx_workflow_transitions_workflow', 'workflow_transitions', 
                   ['workflow_id'])
    op.create_index('idx_workflow_transitions_states', 'workflow_transitions', 
                   ['from_state', 'to_state', 'timestamp DESC'])
    op.create_index('idx_workflow_transitions_triggered', 'workflow_transitions', 
                   ['triggered_by', 'timestamp DESC'])
    
    # URL INFO INDEXES
    # For web scraping and URL analysis
    print("Adding URL info indexes...")
    op.create_index('idx_url_info_domain', 'url_info', 
                   ['domain', 'last_crawled DESC'])
    op.create_index('idx_url_info_status', 'url_info', 
                   ['status_code', 'last_crawled DESC'])
    op.create_index('idx_url_info_content_type', 'url_info', 
                   ['content_type', 'last_crawled DESC'])
    
    # APPROVAL REQUESTS INDEXES
    # For workflow approval processes
    print("Adding approval requests indexes...")
    op.create_index('idx_approval_requests_workflow_status', 'approval_requests', 
                   ['workflow_id', 'status'])
    op.create_index('idx_approval_requests_requested_by', 'approval_requests', 
                   ['requested_by', 'created_at DESC'])
    op.create_index('idx_approval_requests_type', 'approval_requests', 
                   ['request_type', 'status'])
    
    # AI INVESTIGATION INDEXES
    # For AI-driven investigation tracking
    print("Adding AI investigation indexes...")
    op.create_index('idx_ai_investigations_status', 'ai_investigations', 
                   ['status', 'created_at DESC'])
    op.create_index('idx_agent_execution_logs_investigation', 'agent_execution_logs', 
                   ['investigation_id', 'status'])
    op.create_index('idx_agent_execution_logs_agent', 'agent_execution_logs', 
                   ['agent_name', 'created_at DESC'])
    
    # AUDIT LOGS OPTIMIZATION INDEXES
    # Enhanced security monitoring indexes
    print("Adding audit logs optimization indexes...")
    if dialect_name == 'postgresql':
        # PostgreSQL partial indexes for better performance
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_security_events 
            ON audit_logs (timestamp DESC, user_id, event_type) 
            WHERE severity IN ('high', 'critical')
        """)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_recent 
            ON audit_logs (timestamp DESC) 
            WHERE timestamp >= NOW() - INTERVAL '30 days'
        """)
    else:
        # SQLite versions
        op.create_index('idx_audit_logs_security_events', 'audit_logs', 
                       ['timestamp', 'user_id', 'event_type'])
        op.create_index('idx_audit_logs_resource', 'audit_logs', 
                       ['resource_type', 'resource_id', 'timestamp DESC'])
    
    # SYSTEM EVENTS INDEXES
    print("Adding system events indexes...")
    op.create_index('idx_system_events_component_severity', 'system_events', 
                   ['component', 'severity', 'created_at DESC'])
    op.create_index('idx_system_events_resolved', 'system_events', 
                   ['resolved', 'resolved_at DESC'])
    op.create_index('idx_system_events_type_source', 'system_events', 
                   ['event_type', 'source'])
    
    # TASK RESULTS INDEXES
    print("Adding task results indexes...")
    op.create_index('idx_task_results_type_status', 'task_results', 
                   ['task_type', 'status'])
    op.create_index('idx_task_results_execution_time', 'task_results', 
                   ['execution_time DESC', 'completed_at DESC'])
    
    # WEBSOCKET CONNECTIONS INDEXES
    print("Adding WebSocket connections indexes...")
    op.create_index('idx_websocket_connections_activity', 'websocket_connections', 
                   ['last_activity DESC'])
    op.create_index('idx_connection_metadata_connection', 'connection_metadata', 
                   ['connection_id', 'key'])
    
    # PHASE TRANSITIONS INDEXES
    print("Adding phase transitions indexes...")
    op.create_index('idx_phase_transitions_investigation', 'phase_transitions', 
                   ['investigation_uuid', 'timestamp DESC'])
    op.create_index('idx_phase_transitions_phases', 'phase_transitions', 
                   ['from_phase', 'to_phase', 'timestamp DESC'])
    
    print("Performance indexes created successfully!")


def downgrade():
    """Remove all performance indexes."""
    
    connection = op.get_bind()
    dialect_name = connection.dialect.name
    
    # Drop Investigation indexes
    if dialect_name == 'postgresql':
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_investigations_status_priority")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_investigations_phase_status")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_investigations_classification")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_investigations_active_by_date")
    else:
        op.drop_index('idx_investigations_status_priority', table_name='investigations')
        op.drop_index('idx_investigations_phase_status', table_name='investigations')
        op.drop_index('idx_investigations_classification', table_name='investigations')
    
    # Drop Investigation Targets indexes
    op.drop_index('idx_investigation_targets_investigation_uuid', table_name='investigation_targets')
    op.drop_index('idx_investigation_targets_type_status', table_name='investigation_targets')
    op.drop_index('idx_investigation_targets_priority', table_name='investigation_targets')
    
    # Drop Evidence Collection indexes
    op.drop_index('idx_collected_evidence_investigation_uuid', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_source_type', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_reliability', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_verified', table_name='collected_evidence')
    
    # Drop Threat Indicators indexes
    op.drop_index('idx_threat_indicators_type_value', table_name='threat_indicators')
    op.drop_index('idx_threat_indicators_active', table_name='threat_indicators')
    op.drop_index('idx_threat_indicators_severity', table_name='threat_indicators')
    op.drop_index('idx_threat_indicators_source', table_name='threat_indicators')
    
    # Drop Data Sources indexes
    op.drop_index('idx_data_sources_type_active', table_name='data_sources')
    op.drop_index('idx_data_sources_reliability', table_name='data_sources')
    op.drop_index('idx_data_sources_last_accessed', table_name='data_sources')
    
    # Drop Evidence Chain indexes
    op.drop_index('idx_evidence_chains_evidence_uuid', table_name='evidence_chains')
    op.drop_index('idx_evidence_chains_handler_action', table_name='evidence_chains')
    op.drop_index('idx_evidence_chains_timestamp', table_name='evidence_chains')
    
    # Drop Threat Actors indexes
    op.drop_index('idx_threat_actors_type_level', table_name='threat_actors')
    op.drop_index('idx_threat_actors_last_seen', table_name='threat_actors')
    op.drop_index('idx_threat_actors_confidence', table_name='threat_actors')
    
    # Drop Collection Jobs indexes
    op.drop_index('idx_collection_jobs_status_priority', table_name='collection_jobs')
    op.drop_index('idx_collection_jobs_next_run', table_name='collection_jobs')
    op.drop_index('idx_collection_jobs_type', table_name='collection_jobs')
    
    # Drop Analysis Results indexes
    op.drop_index('idx_analysis_results_investigation_evidence', table_name='analysis_results')
    op.drop_index('idx_analysis_results_type', table_name='analysis_results')
    op.drop_index('idx_analysis_results_confidence', table_name='analysis_results')
    
    # Drop Threat Assessments indexes
    op.drop_index('idx_threat_assessments_investigation', table_name='threat_assessments')
    op.drop_index('idx_threat_assessments_level_risk', table_name='threat_assessments')
    op.drop_index('idx_threat_assessments_status', table_name='threat_assessments')
    
    # Drop Workflow Transitions indexes
    op.drop_index('idx_workflow_transitions_workflow', table_name='workflow_transitions')
    op.drop_index('idx_workflow_transitions_states', table_name='workflow_transitions')
    op.drop_index('idx_workflow_transitions_triggered', table_name='workflow_transitions')
    
    # Drop URL Info indexes
    op.drop_index('idx_url_info_domain', table_name='url_info')
    op.drop_index('idx_url_info_status', table_name='url_info')
    op.drop_index('idx_url_info_content_type', table_name='url_info')
    
    # Drop Approval Requests indexes
    op.drop_index('idx_approval_requests_workflow_status', table_name='approval_requests')
    op.drop_index('idx_approval_requests_requested_by', table_name='approval_requests')
    op.drop_index('idx_approval_requests_type', table_name='approval_requests')
    
    # Drop AI Investigation indexes
    op.drop_index('idx_ai_investigations_status', table_name='ai_investigations')
    op.drop_index('idx_agent_execution_logs_investigation', table_name='agent_execution_logs')
    op.drop_index('idx_agent_execution_logs_agent', table_name='agent_execution_logs')
    
    # Drop Audit Logs indexes
    if dialect_name == 'postgresql':
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_security_events")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_recent")
    else:
        op.drop_index('idx_audit_logs_security_events', table_name='audit_logs')
        op.drop_index('idx_audit_logs_resource', table_name='audit_logs')
    
    # Drop System Events indexes
    op.drop_index('idx_system_events_component_severity', table_name='system_events')
    op.drop_index('idx_system_events_resolved', table_name='system_events')
    op.drop_index('idx_system_events_type_source', table_name='system_events')
    
    # Drop Task Results indexes
    op.drop_index('idx_task_results_type_status', table_name='task_results')
    op.drop_index('idx_task_results_execution_time', table_name='task_results')
    
    # Drop WebSocket Connections indexes
    op.drop_index('idx_websocket_connections_activity', table_name='websocket_connections')
    op.drop_index('idx_connection_metadata_connection', table_name='connection_metadata')
    
    # Drop Phase Transitions indexes
    op.drop_index('idx_phase_transitions_investigation', table_name='phase_transitions')
    op.drop_index('idx_phase_transitions_phases', table_name='phase_transitions')
    
    print("Performance indexes dropped successfully!")