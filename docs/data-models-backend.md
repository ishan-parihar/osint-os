# ScrapeCraft OSINT Platform - Backend Data Models Documentation

## Overview

This document provides a comprehensive overview of all data models, database schemas, and relationships in the ScrapeCraft OSINT Platform backend. The platform uses SQLAlchemy for ORM modeling and Pydantic for API schemas, with support for both SQLite (development) and PostgreSQL (production) databases.

## Database Architecture

### Base Model Structure

All SQLAlchemy models inherit from the `Base` class, which provides common fields:

```python
class Base(DeclarativeBase):
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Soft delete support
```

**Common Fields:**
- `id`: Integer primary key with auto-increment
- `created_at`: Creation timestamp (UTC)
- `updated_at`: Last update timestamp (UTC)
- `deleted_at`: Soft delete timestamp (nullable)

## Core Data Models

### 1. Investigation Models

#### Investigation (investigations table)

**Purpose:** Main investigation entity for OSINT operations

**Fields:**
- `uuid`: String (UUID) - Primary key for investigations
- `title`: String (500) - Investigation title
- `description`: Text - Detailed description
- `classification`: Enum(InvestigationClassification) - Security classification
- `priority`: Enum(InvestigationPriority) - Priority level
- `status`: Enum(InvestigationStatus) - Current status
- `current_phase`: Enum(InvestigationPhase) - Current workflow phase
- `completed_at`: DateTime (nullable) - Completion timestamp

**Enums:**
```python
class InvestigationClassification(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"

class InvestigationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class InvestigationStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class InvestigationPhase(str, Enum):
    PLANNING = "planning"
    RECONNAISSANCE = "reconnaissance"
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    REPORTING = "reporting"
```

**Relationships:**
- targets (1:N) → InvestigationTarget
- intelligence_requirements (1:N) → IntelligenceRequirement
- agent_assignments (1:N) → AgentAssignment
- collected_evidence (1:N) → CollectedEvidence
- analysis_results (1:N) → AnalysisResult
- threat_assessments (1:N) → ThreatAssessment
- phase_transitions (1:N) → PhaseTransition
- reports (1:N) → InvestigationReport
- final_assessment (1:1) → FinalAssessment

#### InvestigationTarget (investigation_targets table)

**Purpose:** Targets for OSINT investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `type`: Enum(InvestigationTargetType) - Target type
- `identifier`: String - Primary identifier
- `aliases`: ARRAY(String) - Alternative identifiers
- `priority`: Enum(InvestigationPriority) - Target priority
- `collection_requirements`: ARRAY(String) - Collection requirements
- `status`: Enum(TargetStatus) - Current status

**Enums:**
```python
class InvestigationTargetType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DOMAIN = "DOMAIN"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    OTHER = "OTHER"

class TargetStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

#### IntelligenceRequirement (intelligence_requirements table)

**Purpose:** Intelligence requirements for investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `title`: String - Requirement title
- `description`: Text - Detailed description
- `priority`: Enum(InvestigationPriority) - Priority level
- `status`: String - Current status (default: "ACTIVE")

#### AgentAssignment (agent_assignments table)

**Purpose:** AI agent assignments for investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `agent_id`: String - Agent identifier
- `agent_type`: Enum(AgentType) - Type of agent
- `assigned_targets`: ARRAY(String) - Assigned target IDs
- `current_task`: JSON - Current task details
- `status`: Enum(AgentStatus) - Agent status
- `performance_metrics`: JSON - Performance data

**Enums:**
```python
class AgentType(str, Enum):
    PLANNING = "PLANNING"
    COLLECTION = "COLLECTION"
    ANALYSIS = "ANALYSIS"
    SYNTHESIS = "SYNTHESIS"

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
```

#### CollectedEvidence (collected_evidence table)

**Purpose:** Evidence collected during investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `source`: String - Evidence source
- `source_type`: Enum(EvidenceSourceType) - Type of source
- `content_type`: String - Content type (text, image, etc.)
- `content_data`: Text - Raw content data
- `content_summary`: Text - Content summary
- `content_tags`: ARRAY(String) - Content tags
- `evidence_metadata`: JSON - Metadata
- `reliability_score`: Float - Reliability score (0.0-1.0)
- `relevance_score`: Float - Relevance score (0.0-1.0)
- `verified`: Boolean - Verification status
- `verification_notes`: Text - Verification notes
- `analyst_notes`: Text - Analyst notes

**Enums:**
```python
class EvidenceSourceType(str, Enum):
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    PUBLIC_RECORDS = "PUBLIC_RECORDS"
    WEB_CONTENT = "WEB_CONTENT"
    DARK_WEB = "DARK_WEB"
    HUMINT = "HUMINT"
```

#### AnalysisResult (analysis_results table)

**Purpose:** Analysis results for collected evidence

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `evidence_uuid`: String (FK) - Reference to collected_evidence.uuid
- `analysis_type`: String - Type of analysis
- `results`: JSON - Analysis results
- `confidence`: Float - Confidence level (0.0-1.0)
- `analyst_id`: String - Analyst identifier
- `tags`: ARRAY(String) - Analysis tags

#### ThreatAssessment (threat_assessments table)

**Purpose:** Threat assessments for investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `title`: String - Assessment title
- `description`: Text - Detailed description
- `threat_level`: Enum(ThreatLevel) - Threat level
- `threat_type`: String - Type of threat
- `targets`: ARRAY(String) - Target IDs
- `likelihood`: Float - Likelihood score (0.0-1.0)
- `impact`: Float - Impact score (0.0-1.0)
- `risk_score`: Float - Calculated risk score
- `status`: String - Assessment status
- `analyst_notes`: Text - Analyst notes

**Enums:**
```python
class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
```

#### PhaseTransition (phase_transitions table)

**Purpose:** Track phase transitions in investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `from_phase`: Enum(InvestigationPhase) - Previous phase
- `to_phase`: Enum(InvestigationPhase) - New phase
- `timestamp`: DateTime - Transition timestamp
- `reason`: Text - Transition reason
- `triggered_by`: String - Who triggered the transition

#### InvestigationReport (investigation_reports table)

**Purpose:** Generated reports for investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `title`: String - Report title
- `content`: Text - Report content
- `format`: String - Report format (json, html, pdf)
- `classification`: Enum(InvestigationClassification) - Security classification
- `authors`: ARRAY(String) - Report authors
- `recipients`: ARRAY(String) - Report recipients
- `status`: String - Report status
- `approved_at`: DateTime - Approval timestamp
- `distributed_at`: DateTime - Distribution timestamp

#### FinalAssessment (final_assessments table)

**Purpose:** Final assessment for completed investigations

**Fields:**
- `uuid`: String (UUID) - Primary key
- `investigation_uuid`: String (FK) - Reference to investigations.uuid
- `executive_summary`: Text - Executive summary
- `key_findings`: ARRAY(String) - Key findings
- `confidence_level`: Float - Overall confidence level
- `overall_threat_level`: Enum(ThreatLevel) - Overall threat assessment
- `classification`: Enum(InvestigationClassification) - Security classification

### 2. AI Investigation Models

#### AIInvestigation (ai_investigations table)

**Purpose:** AI-driven investigation data persistence

**Fields:**
- `investigation_id`: String (100) - Unique investigation identifier
- `title`: String (500) - Investigation title
- `description`: Text - Investigation description
- `config`: JSON - Configuration data
- `status`: String (50) - Current status

#### AgentExecutionLog (agent_execution_logs table)

**Purpose:** Track agent execution activity

**Fields:**
- `investigation_id`: String (100) - Reference to AI investigation
- `agent_name`: String (100) - Agent identifier
- `execution_data`: JSON - Execution details
- `status`: String (50) - Execution status

#### InvestigationState (investigation_states table)

**Purpose:** Store investigation state data

**Fields:**
- `investigation_id`: String (100) - Unique investigation identifier
- `state_data`: Text - Serialized state data

### 3. Workflow Models

#### WorkflowState (workflow_states table)

**Purpose:** Workflow execution state persistence

**Fields:**
- `workflow_id`: String (100) - Unique workflow identifier
- `workflow_data`: Text - Serialized workflow data
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

#### Workflow (workflows table)

**Purpose:** Workflow definitions and management

**Fields:**
- `name`: String (100) - Workflow name
- `description`: Text - Workflow description
- `config`: JSON - Workflow configuration
- `is_active`: Boolean - Active status

#### WorkflowTransition (workflow_transitions table)

**Purpose:** Track workflow state changes

**Fields:**
- `workflow_id`: String (100) - Reference to workflow
- `from_state`: String (100) - Previous state
- `to_state`: String (100) - New state
- `transition_data`: JSON - Transition details

#### URLInfo (url_info table)

**Purpose:** URL metadata storage

**Fields:**
- `url`: String (1000) - URL
- `title`: String (500) - Page title
- `description`: Text - Page description
- `url_metadata`: JSON - Additional metadata

#### SchemaField (schema_fields table)

**Purpose:** Data schema field definitions

**Fields:**
- `name`: String (100) - Field name
- `field_type`: String (50) - Field data type
- `required`: Boolean - Required field
- `default_value`: Text - Default value
- `description`: Text - Field description

#### ApprovalRequest (approval_requests table)

**Purpose:** Workflow approval requests

**Fields:**
- `workflow_id`: String (100) - Reference to workflow
- `requester_id`: String (100) - Requester identifier
- `approver_id`: String (100) - Approver identifier
- `status`: String (20) - Approval status
- `request_data`: JSON - Request details
- `response_data`: JSON - Response details

#### PipelineExecution (pipeline_executions table)

**Purpose:** Pipeline execution tracking

**Fields:**
- `pipeline_id`: String (100) - Reference to pipeline
- `status`: String (20) - Execution status
- `config`: JSON - Execution configuration
- `result_data`: JSON - Execution results
- `error_message`: Text - Error details

### 4. Task Models

#### TaskResult (task_results table)

**Purpose:** Task execution results

**Fields:**
- `task_id`: String (100) - Unique task identifier
- `task_data`: Text - Serialized task data
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

#### Task (tasks table)

**Purpose:** Task definitions

**Fields:**
- `task_id`: String (100) - Unique task identifier
- `name`: String (200) - Task name
- `description`: Text - Task description
- `status`: String (50) - Task status
- `config`: Text - Task configuration

### 5. Audit and Security Models

#### AuditLog (audit_logs table)

**Purpose:** Security and operation audit logging

**Fields:**
- `id`: Integer - Primary key
- `event_type`: String (100) - Event type
- `user_id`: String (100) - User identifier
- `session_id`: String (100) - Session identifier
- `ip_address`: String (45) - IP address (IPv6 compatible)
- `user_agent`: Text - User agent string
- `action`: String (100) - Action performed
- `resource_type`: String (50) - Resource type
- `resource_id`: String (100) - Resource identifier
- `details`: Text - Event details
- `timestamp`: DateTime - Event timestamp
- `severity`: String (20) - Event severity

**Indexes:**
- PRIMARY KEY (id)
- INDEX (event_type)
- INDEX (user_id)
- INDEX (timestamp)
- INDEX (session_id)

#### UserSession (user_sessions table)

**Purpose:** Active user session tracking

**Fields:**
- `id`: Integer - Primary key
- `session_id`: String (100) - Unique session identifier
- `user_id`: String (100) - User identifier
- `ip_address`: String (45) - IP address
- `user_agent`: Text - User agent string
- `created_at`: DateTime - Session creation
- `last_activity`: DateTime - Last activity
- `expires_at`: DateTime - Session expiration
- `is_active`: Boolean - Active status
- `session_data`: Text - Session data

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE INDEX (session_id)
- INDEX (user_id)
- INDEX (expires_at)

#### SystemEvent (system_events table)

**Purpose:** System-level event logging

**Fields:**
- `event_type`: String (100) - Event type
- `source`: String (100) - Event source
- `message`: Text - Event message
- `details`: Text - Event details
- `severity`: String (20) - Event severity

### 6. WebSocket Models

#### WebSocketConnection (websocket_connections table)

**Purpose:** Active WebSocket connection tracking

**Fields:**
- `connection_id`: String (100) - Unique connection identifier
- `pipeline_id`: String (100) - Associated pipeline
- `connection_metadata`: JSON - Connection metadata
- `connected_at`: DateTime - Connection timestamp
- `last_activity`: DateTime - Last activity timestamp

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE INDEX (connection_id)
- INDEX (pipeline_id)

#### ConnectionMetadata (connection_metadata table)

**Purpose:** Additional connection metadata

**Fields:**
- `connection_id`: String (100) - Reference to connection
- `key`: String (100) - Metadata key
- `value`: Text - Metadata value

**Indexes:**
- PRIMARY KEY (id)
- INDEX (connection_id)

## Pydantic Schemas

### Common Schemas

#### BaseSchema
Base configuration for all Pydantic schemas with JSON encoding for datetime objects.

#### User Schemas
- `UserBase`: Basic user information
- `UserCreate`: User creation with password validation
- `UserUpdate`: User update fields
- `User`: Complete user schema
- `UserInDB`: User with database fields

#### Authentication Schemas
- `Token`: Token response
- `TokenData`: Token payload data
- `LoginRequest`: Login credentials

#### Investigation Schemas
- `InvestigationBase`: Base investigation fields
- `InvestigationCreate`: Creation schema with targets
- `InvestigationUpdate`: Updateable fields
- `Investigation`: Complete investigation schema
- `InvestigationTargetBase/TargetCreate/Target`: Target schemas

#### Pipeline Schemas
- `PipelineBase`: Base pipeline information
- `PipelineCreate`: Creation with URLs and schema
- `PipelineUpdate`: Updateable fields
- `Pipeline`: Complete pipeline schema
- `PipelineExecution`: Execution tracking

#### Workflow Schemas
- `WorkflowState`: State management
- `WorkflowAction`: Action definitions
- `ApprovalRequest`: Approval workflows
- `WorkflowPhase`: Phase enumeration

#### Evidence and Report Schemas
- `EvidenceBase/Create/Evidence`: Evidence management
- `ReportBase/Create/Report`: Report generation

#### Chat Schemas
- `MessageRole`: Message roles (user, assistant, system)
- `ChatMessage`: Individual messages
- `ChatResponse`: Response with metadata
- `ConversationHistory`: Conversation tracking

## Database Migrations

### Migration History

#### 001_osint_models (2025-11-02)
- Created core OSINT investigation tables
- Defined enums and relationships
- Established primary/foreign key constraints

#### 002_data_persistence (2025-11-05)
- Added data persistence tables
- WebSocket connection tracking
- Audit logging infrastructure
- Task and workflow state management

### Migration Structure
```
migrations/
├── versions/
│   ├── 001_osint_models.py
│   └── 002_data_persistence.py
└── env.py
```

## Database Constraints and Indexes

### Primary Keys
- All tables use integer auto-increment primary keys except investigation-related tables which use UUID strings
- Investigation models use `uuid` as primary key for better distribution

### Foreign Keys
- All relationships are properly constrained with foreign keys
- Cascade delete configured for dependent entities
- Referential integrity enforced at database level

### Indexes
- Primary key indexes automatically created
- Foreign key columns indexed for join performance
- Frequently queried columns indexed:
  - `investigation_uuid` in child tables
  - `user_id` in audit/session tables
  - `timestamp` columns for time-based queries
  - `status` columns for filtering

### Unique Constraints
- `investigation_id` in ai_investigations
- `workflow_id` in workflow_states
- `task_id` in tasks/task_results
- `connection_id` in websocket_connections

## Data Types and Validation

### PostgreSQL-Specific Features
- `ARRAY(String)` for list fields (aliases, tags, requirements)
- `JSON` for flexible metadata storage
- `ENUM` types for controlled vocabularies
- Timezone-aware timestamps

### Validation Rules
- String length limits enforced at database level
- Non-null constraints for required fields
- Default values for status fields
- Float ranges for scores (0.0-1.0)

### Soft Deletes
- `deleted_at` timestamp in base model
- Allows data recovery and audit trails
- Queries should filter out deleted records

## Security Considerations

### Data Classification
- Investigation classification levels enforced
- Sensitive data marked with appropriate classification
- Access control based on classification

### Audit Trail
- Comprehensive logging of all data operations
- User attribution for all changes
- Timestamp tracking for forensics

### Session Management
- Secure session tracking with expiration
- IP address and device fingerprinting
- Session invalidation on security events

## Performance Optimization

### Index Strategy
- Composite indexes for common query patterns
- Selective indexing on high-cardinality columns
- Regular index maintenance and analysis

### Query Patterns
- Optimized for investigation-centric access patterns
- Efficient joins with proper foreign key indexing
- Pagination support for large result sets

### Data Partitioning
- Consider time-based partitioning for audit logs
- Investigation-based partitioning for large datasets
- Archive strategies for historical data

## API Integration

### Serialization
- Automatic datetime serialization to ISO format
- JSON field handling for complex data
- Enum value serialization

### Validation
- Input validation using Pydantic schemas
- Database constraint validation
- Business rule enforcement

### Error Handling
- Comprehensive error responses
- Validation error details
- Database error mapping

---

*This documentation is generated automatically from the codebase. For the most up-to-date information, refer to the actual model definitions in the source code.*