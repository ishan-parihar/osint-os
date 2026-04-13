# ScrapeCraft OSINT Platform - Source Tree Analysis

**Generated:** 2025-11-10  
**Project Type:** Multi-part Architecture (4 parts)  
**Scan Level:** Deep Analysis  

## Project Overview

ScrapeCraft is a comprehensive OSINT (Open Source Intelligence) platform built with a modern multi-part architecture. The system combines automated data collection, intelligent analysis, and report generation capabilities for intelligence operations.

## Repository Structure

```
scrapecraft/                              # Project Root
├── .bmad/                                # BMad Framework Configuration (Part: bmm-system)
│   ├── _cfg/                             # Agent and workflow configuration registry
│   │   ├── agents/                       # BMad agent definitions
│   │   └── files-manifest.csv            # File tracking manifest
│   ├── bmm/                              # Core BMad Methodology Framework
│   │   ├── agents/                       # BMad specialized agents (analyst, architect, dev, etc.)
│   │   ├── workflows/                    # Structured workflow templates
│   │   │   ├── document-project/         # Project documentation workflow
│   │   │   ├── workflow-status/          # Progress tracking system
│   │   │   └── 1-analysis/               # Analysis phase workflows
│   │   ├── docs/                         # BMad framework documentation
│   │   ├── tasks/                        # Core task definitions
│   │   ├── teams/                        # Team configuration templates
│   │   └── tools/                        # BMad utility tools
│   └── core/                             # Core BMad execution engine
│       ├── agents/                       # Base agent classes
│       ├── tasks/                        # Task execution framework
│       ├── tools/                        # Core tools
│       └── workflows/                    # Core workflow templates
│
├── backend/                              # FastAPI Python Backend (Part: backend)
│   ├── app/                              # Main application package
│   │   ├── agents/                       # OSINT Agent System
│   │   │   ├── base/                     # Base agent classes and interfaces
│   │   │   │   ├── communication.py      # Agent communication protocols
│   │   │   │   └── osint_agent.py        # Base OSINT agent implementation
│   │   │   ├── specialized/              # Specialized OSINT agents
│   │   │   │   ├── collection/           # Data collection agents
│   │   │   │   │   ├── dark_web_collector.py
│   │   │   │   │   ├── social_media_collector.py
│   │   │   │   │   ├── surface_web_collector.py
│   │   │   │   │   ├── url_discovery_agent.py
│   │   │   │   │   ├── multi_engine_search_agent.py
│   │   │   │   │   └── public_records_collector.py
│   │   │   │   ├── analysis/             # Data analysis agents
│   │   │   │   │   ├── contextual_analysis_agent.py
│   │   │   │   │   ├── data_fusion_agent.py
│   │   │   │   │   └── pattern_recognition_agent.py
│   │   │   │   ├── synthesis/            # Report and intelligence synthesis
│   │   │   │   │   ├── intelligence_synthesis_agent.py
│   │   │   │   │   ├── report_generation_agent.py
│   │   │   │   │   └── quality_assurance_agent.py
│   │   │   │   ├── planning/             # Strategic planning agents
│   │   │   │   │   ├── objective_definition.py
│   │   │   │   │   └── strategy_formulation.py
│   │   │   │   ├── coordination/         # Workflow coordination
│   │   │   │   │   └── conversational_coordinator.py
│   │   │   │   └── generation/           # Content generation
│   │   │   │       └── pipeline_generation_agent.py
│   │   │   ├── legacy/                   # Legacy agent implementations
│   │   │   │   ├── kimi_agent.py
│   │   │   │   ├── langgraph_agent.py
│   │   │   │   ├── openrouter_agent.py
│   │   │   │   └── scraping_agent.py
│   │   │   ├── tools/                    # Agent tools and utilities
│   │   │   │   └── langchain_tools.py
│   │   │   └── nodes/                    # Agent node definitions
│   │   ├── api/                          # REST API Endpoints
│   │   │   ├── agents/                   # Agent management APIs
│   │   │   ├── auth/                     # Authentication endpoints
│   │   │   ├── investigations/           # Investigation management
│   │   │   ├── llm/                      # LLM service integration
│   │   │   ├── search/                   # Search service APIs
│   │   │   └── websocket/                # WebSocket connection handling
│   │   ├── core/                         # Core application services
│   │   │   ├── config.py                 # Application configuration
│   │   │   ├── database.py               # Database connections and setup
│   │   │   ├── security.py               # Security utilities
│   │   │   └── logging.py                # Logging configuration
│   │   ├── middleware/                   # HTTP middleware
│   │   │   └── cors.py                   # Cross-origin resource sharing
│   │   ├── models/                       # Database Models
│   │   │   ├── agent.py                  # Agent data models
│   │   │   ├── investigation.py          # Investigation models
│   │   │   ├── llm_service.py            # LLM service configurations
│   │   │   ├── search_service.py         # Search service models
│   │   │   ├── user.py                   # User management models
│   │   │   └── websocket.py              # WebSocket connection models
│   │   ├── services/                     # Business Logic Services
│   │   │   ├── agent_service.py          # Agent management service
│   │   │   ├── auth_service.py           # Authentication service
│   │   │   ├── investigation_service.py  # Investigation management
│   │   │   ├── llm_service.py            # LLM integration service
│   │   │   ├── search_service.py         # Search integration service
│   │   │   └── websocket_service.py      # WebSocket management
│   │   ├── utils/                        # Utility functions
│   │   │   ├── async_utils.py            # Async programming utilities
│   │   │   ├── logger.py                 # Logging utilities
│   │   │   └── response_helpers.py       # API response helpers
│   │   └── main.py                       # FastAPI application entry point
│   ├── data/                             # Data storage
│   │   ├── investigations.json           # Investigation data
│   │   └── users.json                    # User data
│   ├── migrations/                       # Database migrations (Alembic)
│   │   ├── versions/                     # Migration version files
│   │   │   ├── 001_osint_models.py       # Initial OSINT models
│   │   │   └── 002_data_persistence.py   # Data persistence improvements
│   │   └── env.py                        # Alembic environment configuration
│   ├── tests/                            # Test suite
│   │   ├── test_async_llm_service.py     # LLM service tests
│   │   ├── test_real_search_service.py   # Search service tests
│   │   └── test_utils.py                 # Utility function tests
│   ├── config/                           # Configuration management
│   │   └── environments/                 # Environment-specific configs
│   │       ├── development.yaml          # Development environment
│   │       ├── production.yaml           # Production environment
│   │       └── staging.yaml              # Staging environment
│   ├── dev_server.py                     # Development server
│   ├── requirements.txt                  # Python dependencies
│   ├── Dockerfile                        # Docker container configuration
│   └── alembic.ini                       # Database migration configuration
│
├── frontend/                             # React TypeScript Frontend (Part: frontend)
│   ├── public/                           # Static assets
│   │   ├── index.html                    # HTML template
│   │   ├── logo.png                      # Application logo
│   │   └── manifest.json                 # PWA manifest
│   ├── src/                              # Source code
│   │   ├── components/                   # React components
│   │   │   ├── Workflow/                 # Workflow management components
│   │   │   │   ├── AgentCoordinator.tsx  # Agent coordination UI
│   │   │   │   ├── ApprovalDialog.tsx    # Approval workflow dialogs
│   │   │   │   ├── ApprovalManager.tsx   # Approval process manager
│   │   │   │   └── WorkflowSidebar.tsx   # Workflow navigation sidebar
│   │   │   ├── common/                   # Shared UI components
│   │   │   └── layout/                   # Layout components
│   │   ├── hooks/                        # Custom React hooks
│   │   │   └── useWebSocket.ts           # WebSocket connection hook
│   │   ├── services/                     # API and service layer
│   │   │   ├── api.ts                    # Base API client
│   │   │   └── osintAgentApi.ts          # OSINT agent API client
│   │   ├── store/                        # State management (Zustand)
│   │   │   ├── chatStore.ts              # Chat state management
│   │   │   ├── investigationStore.ts     # Investigation state
│   │   │   ├── pipelineStore.ts          # Pipeline state
│   │   │   ├── websocketStore.ts         # WebSocket state
│   │   │   └── workflowStore.ts          # Workflow state
│   │   ├── types/                        # TypeScript type definitions
│   │   │   ├── index.ts                  # Global type exports
│   │   │   └── osint.ts                  # OSINT-specific types
│   │   ├── assets/                       # Static assets
│   │   ├── App.tsx                       # Main application component
│   │   ├── index.tsx                     # Application entry point
│   │   └── index.css                     # Global styles
│   ├── package.json                      # Node.js dependencies and scripts
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── tailwind.config.js                # Tailwind CSS configuration
│   ├── postcss.config.js                 # PostCSS configuration
│   ├── nginx.conf                        # Nginx configuration for deployment
│   └── Dockerfile                        # Docker container configuration
│
├── infrastructure/                       # Infrastructure as Code (Part: infrastructure)
│   ├── k8s/                             # Kubernetes manifests
│   │   ├── backend-deployment.yaml       # Backend service deployment
│   │   ├── frontend-deployment.yaml      # Frontend service deployment
│   │   ├── postgres-deployment.yaml      # PostgreSQL database
│   │   ├── redis-deployment.yaml         # Redis cache
│   │   ├── services.yaml                 # Service definitions
│   │   ├── configmap.yaml                # Configuration maps
│   │   ├── secrets.yaml                  # Secret management
│   │   ├── ingress.yaml                  # Ingress routing
│   │   └── namespace.yaml                # Namespace configuration
│   ├── kubernetes/                       # Additional Kubernetes configurations
│   │   └── monitoring/                   # Monitoring stack
│   │       ├── prometheus.yaml           # Prometheus monitoring
│   │       ├── grafana.yaml              # Grafana dashboards
│   │       └── alertmanager.yaml         # Alert management
│   └── helm/                             # Helm charts
│       ├── Chart.yaml                    # Helm chart metadata
│       └── values.yaml                   # Default configuration values
│
├── docs/                                # Project Documentation
│   ├── bmm-workflow-status.yaml          # BMad workflow progress tracking
│   ├── project-scan-report.json          # Project analysis state
│   ├── api-contracts-backend.md          # Backend API documentation
│   ├── data-models-backend.md            # Database schema documentation
│   ├── component-inventory-frontend.md   # Frontend component catalog
│   ├── bmm-technology-stack.md           # Technology stack analysis
│   └── source-tree-analysis.md           # This file
│
├── tests/                               # End-to-end and integration tests
│   ├── e2e/                              # End-to-end tests
│   │   └── test_critical_flows.py        # Critical user flow tests
│   ├── fixtures/                         # Test data fixtures
│   │   └── test_data.py                  # Test data definitions
│   ├── integration/                      # Integration tests
│   │   └── test_integration.py           # Service integration tests
│   ├── performance/                      # Performance tests
│   │   └── test_performance.py           # Performance benchmarks
│   ├── security/                         # Security tests
│   │   ├── comprehensive_security_test.py # Full security suite
│   │   └── test_security.py              # Security-focused tests
│   └── unit/                             # Unit tests
│       ├── test_api.py                   # API endpoint tests
│       └── test_services.py              # Service layer tests
│
├── config/                              # Configuration files
│   ├── environments/                     # Environment configurations
│   │   ├── development.yaml              # Development settings
│   │   ├── production.yaml               # Production settings
│   │   └── staging.yaml                  # Staging settings
│   └── .env.example                      # Environment variable template
│
├── .github/                             # GitHub configuration
│   └── workflows/                        # CI/CD workflows
│       └── ci-cd.yml                     # Continuous integration/deployment
│
├── docker-compose.yml                   # Multi-container Docker setup
├── docker-compose.override.yml          # Development Docker overrides
├── osint_cli.py                         # Command-line interface
├── README.md                            # Project documentation
├── LICENSE                              # Software license
└── .gitignore                           # Git ignore patterns
```

## Critical Directories and Entry Points

### Backend Entry Points
- **Main Application:** `backend/app/main.py` - FastAPI application entry point
- **Development Server:** `backend/dev_server.py` - Development environment server
- **Database Migrations:** `backend/alembic.ini` - Alembic migration configuration

### Frontend Entry Points  
- **React Application:** `frontend/src/index.tsx` - React application entry point
- **Main Component:** `frontend/src/App.tsx` - Primary application component
- **Package Configuration:** `frontend/package.json` - Node.js dependencies and scripts

### Infrastructure Entry Points
- **Docker Compose:** `docker-compose.yml` - Local development environment
- **Kubernetes:** `k8s/` - Production deployment manifests
- **Helm Charts:** `helm/` - Package-based deployment

### BMad Framework Entry Points
- **Agent Registry:** `.bmad/_cfg/agents/` - BMad agent definitions
- **Workflow Engine:** `.bmad/core/tasks/workflow.xml` - Core workflow execution
- **Configuration:** `.bmad/bmm/config.yaml` - BMad framework configuration

## Integration Points

### Backend-Frontend Communication
- **REST API:** Backend `app/api/` → Frontend `src/services/api.ts`
- **WebSocket:** Backend `app/api/websocket/` → Frontend `src/hooks/useWebSocket.ts`
- **OSINT Agent API:** Backend `app/api/agents/` → Frontend `src/services/osintAgentApi.ts`

### Service Integration
- **Database:** PostgreSQL via Alembic migrations
- **Cache:** Redis for session and temporary data
- **LLM Services:** External LLM provider integrations
- **Search Services:** Multiple search engine APIs

### Infrastructure Integration
- **Containerization:** Docker for service isolation
- **Orchestration:** Kubernetes for production deployment
- **Monitoring:** Prometheus + Grafana stack
- **CI/CD:** GitHub Actions workflow automation

## Development Workflow Paths

### Backend Development
1. **Local Development:** `backend/dev_server.py` 
2. **Database Setup:** `alembic upgrade head`
3. **Testing:** `pytest tests/`
4. **Container Build:** `docker build -t scrapecraft-backend ./backend`

### Frontend Development
1. **Local Development:** `npm start` (from `frontend/`)
2. **Build Process:** `npm run build`
3. **Testing:** `npm test`
4. **Container Build:** `docker build -t scrapecraft-frontend ./frontend`

### Full Stack Development
1. **Environment Setup:** `docker-compose up -d`
2. **Database Migrations:** Run via backend container
3. **Service Access:** 
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Configuration Management

### Environment-Specific Configuration
- **Development:** `config/environments/development.yaml`
- **Staging:** `config/environments/staging.yaml`  
- **Production:** `config/environments/production.yaml`

### Service Configuration
- **Backend:** `backend/config/environments/`
- **Database:** Alembic configuration in `backend/alembic.ini`
- **Frontend:** Environment variables via `frontend/.env`

## Security and Compliance

### Authentication
- **Backend JWT:** `backend/app/services/auth_service.py`
- **Frontend Auth:** Stored in Zustand stores
- **API Security:** CORS middleware in `backend/app/middleware/`

### Data Protection
- **Database Encryption:** Configured in PostgreSQL deployment
- **API Security:** Rate limiting and input validation
- **Secret Management:** Kubernetes secrets for production

## Monitoring and Observability

### Application Monitoring
- **Health Checks:** FastAPI health endpoints
- **Logging:** Structured logging in `backend/app/utils/logger.py`
- **Performance:** Response time tracking

### Infrastructure Monitoring
- **Prometheus:** Metrics collection
- **Grafana:** Visualization dashboards
- **Alert Manager:** Alert routing and notification

## Deployment Architecture

### Development Environment
- **Local Docker:** `docker-compose.yml`
- **Hot Reloading:** Development servers with auto-reload
- **Database:** Local PostgreSQL instance

### Production Environment
- **Kubernetes:** Full K8s deployment in `k8s/`
- **Load Balancing:** Ingress controller for traffic routing
- **Scaling:** Horizontal pod autoscaling
- **Persistence:** Persistent volumes for database storage

---

**Summary:** This source tree analysis reveals a sophisticated multi-part OSINT platform with clear separation of concerns, comprehensive testing infrastructure, and production-ready deployment capabilities. The architecture supports both development agility and production scalability.