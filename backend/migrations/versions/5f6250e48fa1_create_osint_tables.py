"""create_osint_tables

Revision ID: 5f6250e48fa1
Revises: 002_data_persistence
Create Date: 2025-11-13 05:14:58.766737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5f6250e48fa1'
down_revision: Union[str, Sequence[str], None] = '002_data_persistence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create investigations table
    op.create_table('investigations',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('phase', sa.String(), nullable=True),
        sa.Column('reliability_score', sa.Float(), nullable=True),
        sa.Column('threat_level', sa.String(), nullable=True),
        sa.Column('lead_analyst', sa.String(), nullable=True),
        sa.Column('assigned_agents', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_investigations_uuid'), 'investigations', ['uuid'], unique=False)

    # Create investigation_targets table
    op.create_table('investigation_targets',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('investigation_uuid', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investigation_uuid'], ['investigations.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_investigation_targets_uuid'), 'investigation_targets', ['uuid'], unique=False)

    # Create collected_evidence table
    op.create_table('collected_evidence',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('investigation_uuid', sa.String(), nullable=False),
        sa.Column('target_uuid', sa.String(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('reliability_score', sa.Float(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investigation_uuid'], ['investigations.uuid'], ),
        sa.ForeignKeyConstraint(['target_uuid'], ['investigation_targets.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_collected_evidence_uuid'), 'collected_evidence', ['uuid'], unique=False)

    # Create analysis_results table
    op.create_table('analysis_results',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('investigation_uuid', sa.String(), nullable=False),
        sa.Column('evidence_uuid', sa.String(), nullable=True),
        sa.Column('analysis_type', sa.String(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('insights', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investigation_uuid'], ['investigations.uuid'], ),
        sa.ForeignKeyConstraint(['evidence_uuid'], ['collected_evidence.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_analysis_results_uuid'), 'analysis_results', ['uuid'], unique=False)

    # Create threat_assessments table
    op.create_table('threat_assessments',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('investigation_uuid', sa.String(), nullable=False),
        sa.Column('threat_level', sa.String(), nullable=False),
        sa.Column('threat_type', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('mitigation_recommendations', sa.Text(), nullable=True),
        sa.Column('impact_assessment', sa.Text(), nullable=True),
        sa.Column('likelihood', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investigation_uuid'], ['investigations.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_threat_assessments_uuid'), 'threat_assessments', ['uuid'], unique=False)

    # Create investigation_reports table
    op.create_table('investigation_reports',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('investigation_uuid', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('findings', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investigation_uuid'], ['investigations.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_investigation_reports_uuid'), 'investigation_reports', ['uuid'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_investigation_reports_uuid'), table_name='investigation_reports')
    op.drop_table('investigation_reports')
    op.drop_index(op.f('ix_threat_assessments_uuid'), table_name='threat_assessments')
    op.drop_table('threat_assessments')
    op.drop_index(op.f('ix_analysis_results_uuid'), table_name='analysis_results')
    op.drop_table('analysis_results')
    op.drop_index(op.f('ix_collected_evidence_uuid'), table_name='collected_evidence')
    op.drop_table('collected_evidence')
    op.drop_index(op.f('ix_investigation_targets_uuid'), table_name='investigation_targets')
    op.drop_table('investigation_targets')
    op.drop_index(op.f('ix_investigations_uuid'), table_name='investigations')
    op.drop_table('investigations')
