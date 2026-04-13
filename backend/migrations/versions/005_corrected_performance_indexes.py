"""
CORRECTED database performance optimization indexes for OSINT-OS platform.

This migration adds strategic indexes to optimize OSINT workloads based on ACTUAL schema.
Revision ID: 005_corrected_performance_indexes
Revises: 004_performance_indexes
Create Date: 2025-11-13 12:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# Revision identifiers
revision = '005_corrected_performance_indexes'
down_revision = '002_data_persistence'
branch_labels = None
depends_on = None


def upgrade():
    """Add comprehensive performance indexes for OSINT workloads based on actual schema."""
    
    # Get database dialect to handle SQLite vs PostgreSQL differences
    connection = op.get_bind()
    dialect_name = connection.dialect.name
    
    print("=== CRITICAL DATABASE PERFORMANCE OPTIMIZATION ===")
    
    # INVESTIGATION TABLE INDEXES (Already have some, add missing ones)
    print("Adding missing investigation table indexes...")
    
    # Add missing indexes for investigations table
    op.create_index('idx_investigations_active_by_date', 'investigations', 
                   ['created_at'], 
                   unique=False, 
                   postgresql_where=sa.text("status IN ('ACTIVE', 'PLANNING')"))
    
    # INVESTIGATION TARGETS INDEXES (Critical - Missing!)
    print("Adding investigation targets indexes...")
    op.create_index('idx_investigation_targets_investigation_id', 'investigation_targets', 
                   ['investigation_id'])
    op.create_index('idx_investigation_targets_type_status', 'investigation_targets', 
                   ['type', 'status'])
    op.create_index('idx_investigation_targets_priority', 'investigation_targets', 
                   ['priority', 'status'])
    op.create_index('idx_investigation_targets_identifier', 'investigation_targets', 
                   ['identifier'])
    
    # EVIDENCE COLLECTION INDEXES (Critical - Missing!)
    print("Adding evidence collection indexes...")
    op.create_index('idx_collected_evidence_investigation_id', 'collected_evidence', 
                   ['investigation_id'])
    op.create_index('idx_collected_evidence_source_type', 'collected_evidence', 
                   ['source_type', 'collected_at DESC'])
    op.create_index('idx_collected_evidence_reliability', 'collected_evidence', 
                   ['reliability_score DESC', 'relevance_score DESC'])
    op.create_index('idx_collected_evidence_verified', 'collected_evidence', 
                   ['verified', 'collected_at DESC'])
    op.create_index('idx_collected_evidence_source', 'collected_evidence', 
                   ['source'])
    
    # AGENT ASSIGNMENTS INDEXES (Missing!)
    print("Adding agent assignments indexes...")
    op.create_index('idx_agent_assignments_investigation_id', 'agent_assignments', 
                   ['investigation_id'])
    op.create_index('idx_agent_assignments_agent_id', 'agent_assignments', 
                   ['agent_id'])
    op.create_index('idx_agent_assignments_status', 'agent_assignments', 
                   ['status', 'assigned_at DESC'])
    op.create_index('idx_agent_assignments_type', 'agent_assignments', 
                   ['agent_type', 'status'])
    
    # ANALYSIS RESULTS INDEXES (Missing!)
    print("Adding analysis results indexes...")
    op.create_index('idx_analysis_results_investigation_id', 'analysis_results', 
                   ['investigation_id'])
    op.create_index('idx_analysis_results_evidence_id', 'analysis_results', 
                   ['evidence_id'])
    op.create_index('idx_analysis_results_type', 'analysis_results', 
                   ['analysis_type', 'generated_at DESC'])
    op.create_index('idx_analysis_results_confidence', 'analysis_results', 
                   ['confidence DESC'])
    op.create_index('idx_analysis_results_analyst', 'analysis_results', 
                   ['analyst_id', 'generated_at DESC'])
    
    # THREAT ASSESSMENTS INDEXES (Missing!)
    print("Adding threat assessments indexes...")
    op.create_index('idx_threat_assessments_investigation_id', 'threat_assessments', 
                   ['investigation_id'])
    op.create_index('idx_threat_assessments_level_risk', 'threat_assessments', 
                   ['threat_level', 'risk_score DESC'])
    op.create_index('idx_threat_assessments_status', 'threat_assessments', 
                   ['status', 'created_at DESC'])
    op.create_index('idx_threat_assessments_type', 'threat_assessments', 
                   ['threat_type', 'threat_level'])
    
    # INTELLIGENCE REQUIREMENTS INDEXES (Missing!)
    print("Adding intelligence requirements indexes...")
    op.create_index('idx_intelligence_requirements_investigation_id', 'intelligence_requirements', 
                   ['investigation_id'])
    op.create_index('idx_intelligence_requirements_priority', 'intelligence_requirements', 
                   ['priority', 'status'])
    op.create_index('idx_intelligence_requirements_status', 'intelligence_requirements', 
                   ['status', 'created_at DESC'])
    
    # PHASE TRANSITIONS INDEXES (Missing!)
    print("Adding phase transitions indexes...")
    op.create_index('idx_phase_transitions_investigation_id', 'phase_transitions', 
                   ['investigation_id', 'timestamp DESC'])
    op.create_index('idx_phase_transitions_phases', 'phase_transitions', 
                   ['from_phase', 'to_phase', 'timestamp DESC'])
    op.create_index('idx_phase_transitions_triggered', 'phase_transitions', 
                   ['triggered_by', 'timestamp DESC'])
    
    # INVESTIGATION REPORTS INDEXES (Missing!)
    print("Adding investigation reports indexes...")
    op.create_index('idx_investigation_reports_investigation_id', 'investigation_reports', 
                   ['investigation_id'])
    op.create_index('idx_investigation_reports_status', 'investigation_reports', 
                   ['status', 'created_at DESC'])
    op.create_index('idx_investigation_reports_classification', 'investigation_reports', 
                   ['classification', 'status'])
    op.create_index('idx_investigation_reports_authors', 'investigation_reports', 
                   ['created_at DESC'])
    
    # FINAL ASSESSMENTS INDEXES (Missing!)
    print("Adding final assessments indexes...")
    op.create_index('idx_final_assessments_investigation_id', 'final_assessments', 
                   ['investigation_id'])
    op.create_index('idx_final_assessments_threat_level', 'final_assessments', 
                   ['overall_threat_level', 'confidence_level DESC'])
    op.create_index('idx_final_assessments_classification', 'final_assessments', 
                   ['classification'])
    
    # ENHANCED AUDIT LOGS INDEXES (Add missing ones)
    print("Adding enhanced audit logs indexes...")
    op.create_index('idx_audit_logs_resource', 'audit_logs', 
                   ['resource_type', 'resource_id', 'timestamp DESC'])
    op.create_index('idx_audit_logs_severity', 'audit_logs', 
                   ['severity', 'timestamp DESC'])
    op.create_index('idx_audit_logs_action', 'audit_logs', 
                   ['action', 'timestamp DESC'])
    
    # TASK RESULTS INDEXES (Add missing ones)
    print("Adding task results indexes...")
    op.create_index('idx_task_results_created_at', 'task_results', 
                   ['created_at DESC'])
    op.create_index('idx_task_results_updated_at', 'task_results', 
                   ['updated_at DESC'])
    
    # USER SESSIONS INDEXES (Add missing ones)
    print("Adding user sessions indexes...")
    op.create_index('idx_user_sessions_last_activity', 'user_sessions', 
                   ['last_activity DESC'])
    op.create_index('idx_user_sessions_active', 'user_sessions', 
                   ['is_active', 'expires_at'])
    
    # WEBSOCKET CONNECTIONS INDEXES (Add missing ones)
    print("Adding WebSocket connections indexes...")
    op.create_index('idx_websocket_connections_last_activity', 'websocket_connections', 
                   ['last_activity DESC'])
    op.create_index('idx_websocket_connections_pipeline', 'websocket_connections', 
                   ['pipeline_id', 'last_activity DESC'])
    
    # WORKFLOW STATES INDEXES (Add missing ones)
    print("Adding workflow states indexes...")
    op.create_index('idx_workflow_states_created_at', 'workflow_states', 
                   ['created_at DESC'])
    op.create_index('idx_workflow_states_updated_at', 'workflow_states', 
                   ['updated_at DESC'])
    
    # INVESTIGATION STATES INDEXES (Add missing ones)
    print("Adding investigation states indexes...")
    op.create_index('idx_investigation_states_created_at', 'investigation_states', 
                   ['created_at DESC'])
    op.create_index('idx_investigation_states_updated_at', 'investigation_states', 
                   ['updated_at DESC'])
    
    print("=== CRITICAL PERFORMANCE OPTIMIZATION COMPLETE ===")
    print("✅ All OSINT core tables now have strategic indexes!")
    print("✅ Database performance optimized for production workloads!")


def downgrade():
    """Remove all corrected performance indexes."""
    
    print("=== REMOVING PERFORMANCE INDEXES ===")
    
    # Investigation indexes
    op.drop_index('idx_investigations_active_by_date', table_name='investigations')
    
    # Investigation Targets indexes
    op.drop_index('idx_investigation_targets_investigation_id', table_name='investigation_targets')
    op.drop_index('idx_investigation_targets_type_status', table_name='investigation_targets')
    op.drop_index('idx_investigation_targets_priority', table_name='investigation_targets')
    op.drop_index('idx_investigation_targets_identifier', table_name='investigation_targets')
    
    # Evidence Collection indexes
    op.drop_index('idx_collected_evidence_investigation_id', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_source_type', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_reliability', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_verified', table_name='collected_evidence')
    op.drop_index('idx_collected_evidence_source', table_name='collected_evidence')
    
    # Agent Assignments indexes
    op.drop_index('idx_agent_assignments_investigation_id', table_name='agent_assignments')
    op.drop_index('idx_agent_assignments_agent_id', table_name='agent_assignments')
    op.drop_index('idx_agent_assignments_status', table_name='agent_assignments')
    op.drop_index('idx_agent_assignments_type', table_name='agent_assignments')
    
    # Analysis Results indexes
    op.drop_index('idx_analysis_results_investigation_id', table_name='analysis_results')
    op.drop_index('idx_analysis_results_evidence_id', table_name='analysis_results')
    op.drop_index('idx_analysis_results_type', table_name='analysis_results')
    op.drop_index('idx_analysis_results_confidence', table_name='analysis_results')
    op.drop_index('idx_analysis_results_analyst', table_name='analysis_results')
    
    # Threat Assessments indexes
    op.drop_index('idx_threat_assessments_investigation_id', table_name='threat_assessments')
    op.drop_index('idx_threat_assessments_level_risk', table_name='threat_assessments')
    op.drop_index('idx_threat_assessments_status', table_name='threat_assessments')
    op.drop_index('idx_threat_assessments_type', table_name='threat_assessments')
    
    # Intelligence Requirements indexes
    op.drop_index('idx_intelligence_requirements_investigation_id', table_name='intelligence_requirements')
    op.drop_index('idx_intelligence_requirements_priority', table_name='intelligence_requirements')
    op.drop_index('idx_intelligence_requirements_status', table_name='intelligence_requirements')
    
    # Phase Transitions indexes
    op.drop_index('idx_phase_transitions_investigation_id', table_name='phase_transitions')
    op.drop_index('idx_phase_transitions_phases', table_name='phase_transitions')
    op.drop_index('idx_phase_transitions_triggered', table_name='phase_transitions')
    
    # Investigation Reports indexes
    op.drop_index('idx_investigation_reports_investigation_id', table_name='investigation_reports')
    op.drop_index('idx_investigation_reports_status', table_name='investigation_reports')
    op.drop_index('idx_investigation_reports_classification', table_name='investigation_reports')
    op.drop_index('idx_investigation_reports_authors', table_name='investigation_reports')
    
    # Final Assessments indexes
    op.drop_index('idx_final_assessments_investigation_id', table_name='final_assessments')
    op.drop_index('idx_final_assessments_threat_level', table_name='final_assessments')
    op.drop_index('idx_final_assessments_classification', table_name='final_assessments')
    
    # Enhanced Audit Logs indexes
    op.drop_index('idx_audit_logs_resource', table_name='audit_logs')
    op.drop_index('idx_audit_logs_severity', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action', table_name='audit_logs')
    
    # Task Results indexes
    op.drop_index('idx_task_results_created_at', table_name='task_results')
    op.drop_index('idx_task_results_updated_at', table_name='task_results')
    
    # User Sessions indexes
    op.drop_index('idx_user_sessions_last_activity', table_name='user_sessions')
    op.drop_index('idx_user_sessions_active', table_name='user_sessions')
    
    # WebSocket Connections indexes
    op.drop_index('idx_websocket_connections_last_activity', table_name='websocket_connections')
    op.drop_index('idx_websocket_connections_pipeline', table_name='websocket_connections')
    
    # Workflow States indexes
    op.drop_index('idx_workflow_states_created_at', table_name='workflow_states')
    op.drop_index('idx_workflow_states_updated_at', table_name='workflow_states')
    
    # Investigation States indexes
    op.drop_index('idx_investigation_states_created_at', table_name='investigation_states')
    op.drop_index('idx_investigation_states_updated_at', table_name='investigation_states')
    
    print("=== PERFORMANCE INDEXES REMOVED ===")