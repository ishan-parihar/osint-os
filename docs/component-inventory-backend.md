# Component Inventory - Backend

## Overview

The ScrapeCraft backend is built with FastAPI and follows a layered architecture pattern with clear separation of concerns. This document provides a comprehensive inventory of all components, services, and modules that make up the backend system.

## Architecture Layers

### 1. API Layer (`app/api/`)
The entry point for all HTTP requests, organized by functional domains.

#### Authentication & Authorization (`auth.py`)
- **Purpose**: User authentication, JWT token management, and authorization
- **Key Components**:
  - `authenticate_user()` - User credential validation
  - `create_access_token()` - JWT token generation
  - `get_current_user()` - Current user dependency
  - `get_current_active_user()` - Active user validation
- **Dependencies**: OAuth2 with Password Flow, JWT Bearer tokens
- **Security Features**: Password hashing, token expiration, refresh tokens

#### OSINT Operations (`osint.py`)
- **Purpose**: Core OSINT investigation workflows and evidence collection
- **Key Components**:
  - `InvestigationManager` - Investigation lifecycle management
  - `EvidenceCollector` - Evidence gathering automation
  - `SourceValidator` - Source reliability assessment
  - `DataEnricher` - Data enhancement and analysis
- **WebSocket Integration**: Real-time investigation updates
- **External Integrations**: Multiple OSINT sources and APIs

#### Pipeline Management (`pipelines.py`)
- **Purpose**: Data processing pipeline orchestration
- **Key Components**:
  - `PipelineManager` - Pipeline execution control
  - `StageProcessor` - Individual pipeline stage handling
  - `DataTransformer` - Data transformation logic
  - `ErrorHandler` - Pipeline error management
- **Features**: Pipeline templates, stage dependencies, parallel processing

#### Scraping Engine (`scraping.py`)
- **Purpose**: Web scraping and data extraction capabilities
- **Key Components**:
  - `ScrapingEngine` - Main scraping orchestrator
  - `SiteAdapter` - Website-specific adapters
  - `RateLimiter` - Request rate management
  - `ProxyManager` - Proxy rotation and management
- **Anti-Detection**: User agent rotation, request delays, CAPTCHA handling

#### Workflow Orchestration (`workflow.py`)
- **Purpose**: Business workflow management and state tracking
- **Key Components**:
  - `WorkflowEngine` - Workflow execution engine
  - `StateTracker` - Workflow state management
  - `TransitionManager` - State transition logic
  - `ApprovalManager` - Approval workflow handling
- **Features**: Workflow templates, conditional branching, user approvals

#### AI Investigation (`ai_investigation.py`)
- **Purpose**: AI-powered investigation assistance
- **Key Components**:
  - `AIInvestigator` - AI investigation coordinator
  - `LLMManager` - Large language model integration
  - `InsightGenerator` - AI-powered insight generation
  - `HypothesisTester` - Automated hypothesis testing
- **AI Models**: OpenAI GPT, local models via Ollama integration

#### Health Monitoring (`health.py`)
- **Purpose**: System health checks and monitoring endpoints
- **Key Components**:
  - `HealthChecker` - Comprehensive health assessment
  - `MetricsCollector` - System metrics gathering
  - `DependencyChecker` - External dependency validation
  - `StatusReporter` - Health status reporting
- **Monitoring**: Database connectivity, external service health, system resources

### 2. Core Services Layer (`app/services/`)
Business logic and service implementations.

#### Investigation Service (`investigation.py`)
- **Purpose**: Investigation business logic and data management
- **Key Components**:
  - `InvestigationService` - Core investigation operations
  - `EvidenceService` - Evidence management
  - `SourceService` - Source validation and rating
  - `AnalysisService` - Data analysis and insights
- **Features**: Investigation lifecycle, evidence chain of custody, source verification

#### Data Processing Service (`data_processing.py`)
- **Purpose**: Data transformation and processing utilities
- **Key Components**:
  - `DataProcessor` - Generic data processing
  - `TextAnalyzer` - Text analysis and NLP
  - `DataValidator` - Data quality validation
  - `FormatConverter` - Data format conversion
- **Capabilities**: Text processing, data cleaning, format standardization

#### Notification Service (`notifications.py`)
- **Purpose**: User notifications and alert management
- **Key Components**:
  - `NotificationManager` - Notification orchestration
  - `EmailNotifier` - Email notifications
  - `WebSocketNotifier` - Real-time notifications
  - `AlertManager` - Alert routing and escalation
- **Channels**: Email, WebSocket, SMS (future), webhook notifications

#### External API Service (`external_apis.py`)
- **Purpose**: Integration with external OSINT APIs and services
- **Key Components**:
  - `APIClient` - Generic API client
  - `RateLimitManager` - API rate limit handling
  - `ResponseParser` - API response parsing
  - `ErrorHandler` - API error management
- **Integrations**: Various OSINT APIs, data providers, analysis services

### 3. Data Models Layer (`app/models/`)
Data structures and database models.

#### SQLAlchemy Models (`sqlalchemy/`)
- **User Models** (`user.py`):
  - `User` - User account information
  - `UserInDB` - User with password hash
  - `UserProfile` - Extended user profile

- **Investigation Models** (`investigation.py`):
  - `Investigation` - Investigation metadata
  - `Evidence` - Collected evidence items
  - `Source` - Information sources
  - `InvestigationStatus` - Status tracking

- **Workflow Models** (`workflow.py`):
  - `Workflow` - Workflow definitions
  - `WorkflowState` - Workflow execution state
  - `WorkflowTransition` - State transition history

- **Task Models** (`task.py`):
  - `Task` - Task definitions
  - `TaskExecution` - Task execution records
  - `TaskDependency` - Task dependencies

- **Audit Models** (`audit.py`):
  - `AuditLog` - System audit trail
  - `UserActivity` - User activity tracking
  - `SystemEvent` - System event logging

- **WebSocket Models** (`websocket.py`):
  - `WebSocketConnection` - Connection tracking
  - `WebSocketMessage` - Message history
  - `ConnectionSession` - Session management

#### Pydantic Models (`pydantic/`)
- **Request/Response Schemas**:
  - `schemas/investigation.py` - Investigation I/O schemas
  - `schemas/auth.py` - Authentication schemas
  - `schemas/pipeline.py` - Pipeline operation schemas
  - `schemas/scraping.py` - Scraping request/response schemas

### 4. Database Layer (`app/database/`)
Database configuration and management.

#### Database Configuration (`database.py`)
- **Purpose**: Database connection and session management
- **Key Components**:
  - `Database` - Database connection manager
  - `SessionLocal` - SQLAlchemy session factory
  - `engine` - Database engine configuration
- **Features**: Connection pooling, transaction management, retry logic

#### Migrations (`migrations/`)
- **Purpose**: Database schema versioning and migrations
- **Components**: Alembic migration scripts
- **Management**: Version control, rollback capabilities, schema evolution

### 5. Authentication & Security (`app/auth/`)
Security components and authentication utilities.

#### Authentication (`authentication.py`)
- **Purpose**: User authentication and credential management
- **Key Components**:
  - `AuthService` - Authentication business logic
  - `PasswordManager` - Password hashing and verification
  - `TokenManager` - JWT token management
- **Security**: Bcrypt password hashing, JWT tokens, secure session management

#### Authorization (`authorization.py`)
- **Purpose**: Role-based access control (RBAC)
- **Key Components**:
  - `RBACService` - Role-based permission management
  - `PermissionChecker` - Permission validation
  - `RoleManager` - Role assignment and management
- **Features**: Hierarchical roles, resource-based permissions, dynamic permissions

#### Dependencies (`dependencies.py`)
- **Purpose**: FastAPI dependency injection for auth
- **Key Components**:
  - `get_current_user` - Current user dependency
  - `get_current_active_user` - Active user validation
  - `require_permission` - Permission-based access control
- **Integration**: FastAPI dependency system, automatic token validation

### 6. WebSocket Layer (`app/websocket/`)
Real-time communication and event broadcasting.

#### Connection Manager (`connection_manager.py`)
- **Purpose**: WebSocket connection lifecycle management
- **Key Components**:
  - `ConnectionManager` - Connection pool management
  - `Connection` - Individual connection handling
  - `ConnectionPool` - Connection pool implementation
- **Features**: Connection tracking, message broadcasting, room management

#### Event Broadcasting (`event_broadcaster.py`)
- **Purpose**: Real-time event distribution
- **Key Components**:
  - `EventBroadcaster` - Event distribution manager
  - `Event` - Event data structure
  - `SubscriptionManager` - Event subscription management
- **Capabilities**: Event filtering, targeted broadcasting, event persistence

#### Message Handlers (`message_handlers.py`)
- **Purpose**: WebSocket message processing and routing
- **Key Components**:
  - `MessageRouter` - Message routing logic
  - `MessageHandler` - Base handler class
  - `HandlerRegistry` - Handler registration
- **Features**: Message validation, async processing, error handling

### 7. Utility Layer (`app/utils/`)
Shared utilities and helper functions.

#### Configuration (`config.py`)
- **Purpose**: Application configuration management
- **Key Components**:
  - `Settings` - Pydantic settings model
  - `ConfigLoader` - Configuration loading
  - `EnvironmentManager` - Environment variable handling
- **Features**: Environment-based config, validation, secret management

#### Logging (`logging.py`)
- **Purpose**: Structured logging configuration
- **Key Components**:
  - `Logger` - Application logger configuration
  - `LogFormatter` - Structured log formatting
  - `LogManager` - Log lifecycle management
- **Features**: Structured logging, log levels, output formatting

#### Validation (`validation.py`)
- **Purpose**: Data validation utilities
- **Key Components**:
  - `DataValidator` - Generic data validation
  - `SchemaValidator` - Schema validation
  - `CustomValidators` - Business rule validators
- **Capabilities**: Type validation, business rules, custom validators

#### Error Handling (`errors.py`)
- **Purpose**: Custom error definitions and handling
- **Key Components**:
  - `ScrapecraftException` - Base exception class
  - `ValidationError` - Data validation errors
  - `AuthenticationError` - Authentication failures
  - `AuthorizationError` - Permission errors
- **Features**: Structured errors, error codes, detailed messages

### 8. Testing Infrastructure (`tests/`)
Comprehensive testing suite.

#### Unit Tests (`unit/`)
- **API Tests**: Endpoint testing, request/response validation
- **Service Tests**: Business logic testing, mock dependencies
- **Model Tests**: Data model validation, relationship testing
- **Utility Tests**: Helper function testing, edge cases

#### Integration Tests (`integration/`)
- **Database Tests**: Database operations, transaction handling
- **API Integration**: End-to-end API testing
- **External Service Tests**: Third-party integration testing
- **WebSocket Tests**: Real-time communication testing

#### Performance Tests (`performance/`)
- **Load Tests**: API performance under load
- **Database Performance**: Query optimization testing
- **Stress Tests**: System limits and breaking points
- **Memory Tests**: Memory usage and leak detection

### 9. Configuration and Deployment

#### Application Configuration (`app/main.py`)
- **Purpose**: FastAPI application factory and setup
- **Key Components**:
  - `create_app()` - Application factory function
  - `app` - FastAPI application instance
  - Middleware configuration
  - Route registration
- **Features**: CORS, middleware, exception handlers, startup/shutdown events

#### Environment Configuration
- **Development**: Local development settings
- **Testing**: Test environment configuration
- **Production**: Production-optimized settings
- **Staging**: Pre-production environment

#### Docker Configuration
- **Dockerfile**: Container image definition
- **docker-compose.yml**: Local development stack
- **Health Checks**: Container health monitoring
- **Volume Management**: Data persistence

## Component Interactions

### Request Flow
```
HTTP Request → FastAPI Router → API Endpoint → Service Layer → Database Layer
                                    ↓
WebSocket Events ← WebSocket Manager ← Service Layer ← Background Tasks
```

### Service Communication
- **Synchronous**: Direct service method calls
- **Asynchronous**: Background task processing
- **Event-Driven**: WebSocket event broadcasting
- **External**: Third-party API integrations

### Data Flow
- **Input**: Request validation → Business logic → Database operations
- **Processing**: Data transformation → Business rules → Validation
- **Output**: Response formatting → Real-time updates → Audit logging

## Security Architecture

### Authentication Flow
```
Client Request → JWT Validation → User Identification → Permission Check → Resource Access
```

### Authorization Layers
- **API Level**: Endpoint protection via dependencies
- **Service Level**: Business rule authorization
- **Data Level**: Row-level security (future)
- **Infrastructure Level**: Network security, firewalls

### Security Features
- **Password Security**: Bcrypt hashing, salt generation
- **Token Security**: JWT with expiration, refresh tokens
- **Session Security**: Secure cookie handling, CSRF protection
- **API Security**: Rate limiting, input validation, SQL injection prevention

## Performance Optimizations

### Database Optimizations
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Efficient query patterns
- **Indexing Strategy**: Proper database indexes
- **Caching**: Redis caching for frequently accessed data

### Application Optimizations
- **Async Processing**: Async/await patterns throughout
- **Background Tasks**: Celery or FastAPI BackgroundTasks
- **Memory Management**: Efficient data structures
- **Response Compression**: gzip compression for API responses

### Monitoring and Observability
- **Health Checks**: Comprehensive health monitoring
- **Metrics Collection**: Application and system metrics
- **Structured Logging**: JSON-based logging
- **Error Tracking**: Comprehensive error logging and alerting

---

*This component inventory provides a comprehensive overview of the ScrapeCraft backend architecture, serving as a guide for development, maintenance, and system enhancement activities.*