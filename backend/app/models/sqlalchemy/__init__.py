"""
SQLAlchemy ORM Models for ScrapeCraft

This module contains the database models that replace in-memory storage
with proper persistent storage.
"""

from .base import Base
from .investigation import (
    Investigation, InvestigationTarget, IntelligenceRequirement,
    AgentAssignment, CollectedEvidence, AnalysisResult, ThreatAssessment,
    PhaseTransition, InvestigationReport, FinalAssessment
)
from .workflow import (
    Workflow, WorkflowState, WorkflowTransition, URLInfo,
    SchemaField, ApprovalRequest, PipelineExecution
)
from .ai_investigation import (
    AIInvestigation, AgentExecutionLog, InvestigationState as AIInvestigationState
)
from .audit import AuditLog, SystemEvent
from .task import TaskResult
from .websocket import WebSocketConnection, ConnectionMetadata
from .osint_core import (
    DataSource, EvidenceChain, ThreatActor, ThreatIndicator,
    CollectionJob, LegalHold
)

__all__ = [
    "Base",
    # Investigation models
    "Investigation",
    "InvestigationTarget", 
    "IntelligenceRequirement",
    "AgentAssignment",
    "CollectedEvidence",
    "AnalysisResult",
    "ThreatAssessment",
    "PhaseTransition",
    "InvestigationReport",
    "FinalAssessment",
    # Workflow models
    "Workflow",
    "WorkflowState",
    "WorkflowTransition", 
    "URLInfo",
    "SchemaField",
    "ApprovalRequest",
    "PipelineExecution",
    # AI Investigation models
    "AIInvestigation",
    "AgentExecutionLog",
    "AIInvestigationState",
    # Audit models
    "AuditLog",
    "SystemEvent",
    # Task models
    "TaskResult",
    # WebSocket models
    "WebSocketConnection",
    "ConnectionMetadata",
    # OSINT Core models
    "DataSource",
    "EvidenceChain",
    "ThreatActor",
    "ThreatIndicator",
    "CollectionJob",
    "LegalHold",
]
