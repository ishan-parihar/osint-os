# ScrapeCraft Backend API Contracts

This document provides comprehensive API contracts for all endpoints in the ScrapeCraft backend application.

## Table of Contents

- [Base Information](#base-information)
- [Authentication](#authentication)
- [Health Checks](#health-checks)
- [OSINT Investigations](#osint-investigations)
- [Pipeline Management](#pipeline-management)
- [Scraping Operations](#scraping-operations)
- [Workflow Management](#workflow-management)
- [AI Investigations](#ai-investigations)
- [Execution Management](#execution-management)
- [Enhanced Workflow v2](#enhanced-workflow-v2)
- [Common Data Models](#common-data-models)
- [Error Handling](#error-handling)
- [Rate Limiting & Security](#rate-limiting--security)

## Base Information

**Base URL**: `http://localhost:8000` (development)
**API Version**: v1
**Content-Type**: `application/json`
**Authentication**: Bearer Token (JWT)

### Standard Response Format

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": {
    "timestamp": "2025-01-01T00:00:00Z",
    "request_id": "uuid",
    "version": "v1",
    "processing_time_ms": 123.45
  }
}
```

### Pagination Format

```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## Authentication

### Register User
**Endpoint**: `POST /api/auth/register`

**Request Body**:
```json
{
  "username": "string (3-50 chars)",
  "email": "valid@email.com",
  "full_name": "string (optional, max 100 chars)",
  "password": "string (min 6 chars)"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "valid@email.com",
    "full_name": "string",
    "disabled": false,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

### Login
**Endpoint**: `POST /api/auth/token`

**Request Body** (form-data):
```
username: string
password: string
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_role": "admin|analyst|viewer",
    "permissions": ["read", "write", "delete"]
  }
}
```

### Get Current User
**Endpoint**: `GET /api/auth/me`

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "valid@email.com",
    "full_name": "string",
    "disabled": false,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

### Save API Keys
**Endpoint**: `POST /api/auth/api-keys`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "openrouter_key": "string (optional)",
  "scrapegraph_key": "string (optional)"
}
```

### Get API Keys
**Endpoint**: `GET /api/auth/api-keys`

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "openrouter_key": "key_prefix...suffix",
    "scrapegraph_key": "key_prefix...suffix",
    "last_updated": "2025-01-01T00:00:00Z"
  }
}
```

### Refresh Token
**Endpoint**: `POST /api/auth/refresh`

**Request Body**:
```json
{
  "refresh_token": "string"
}
```

### Logout
**Endpoint**: `POST /api/auth/logout`

**Headers**: `Authorization: Bearer <token>`

### Get User Permissions
**Endpoint**: `GET /api/auth/permissions`

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "user_role": "admin",
    "permissions": ["read", "write", "delete", "admin"],
    "permission_count": 4
  }
}
```

## Health Checks

### Overall Health Check
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "services": {
    "websocket": {"status": "healthy", "connections": 5},
    "redis": {"status": "healthy", "connected": true},
    "llm": {"status": "healthy", "provider": "openrouter"}
  }
}
```

### Detailed Health Check
**Endpoint**: `GET /api/v1/health`

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "v1",
    "timestamp": "2025-01-01T00:00:00Z",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "llm_service": "healthy",
      "websocket": "healthy",
      "agent_registry": "healthy"
    }
  }
}
```

### Simple Health Check
**Endpoint**: `GET /api/v1/health/simple`

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-01T00:00:00Z",
    "version": "v1"
  }
}
```

### Readiness Check
**Endpoint**: `GET /api/v1/health/ready`

**Response**:
```json
{
  "success": true,
  "data": {
    "ready": true,
    "timestamp": "2025-01-01T00:00:00Z",
    "version": "v1",
    "services": {}
  }
}
```

### Liveness Check
**Endpoint**: `GET /api/v1/health/live`

**Response**:
```json
{
  "success": true,
  "data": {
    "alive": true,
    "timestamp": "2025-01-01T00:00:00Z",
    "version": "v1",
    "uptime": "1d 2h 30m"
  }
}
```

## OSINT Investigations

### List Investigations
**Endpoint**: `GET /api/osint/investigations`

**Query Parameters**:
- `classification`: `public|internal|confidential|secret|top_secret` (optional)
- `status`: `active|inactive|pending|completed|failed|cancelled` (optional)
- `priority`: `low|medium|high|critical` (optional)

**Response**:
```json
[
  {
    "id": "inv-uuid",
    "title": "string",
    "description": "string",
    "classification": "internal",
    "priority": "medium",
    "status": "active",
    "current_phase": "planning",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "targets": [],
    "progress_percentage": 25.0
  }
]
```

### Create Investigation
**Endpoint**: `POST /api/osint/investigations`

**Request Body**:
```json
{
  "title": "string (1-200 chars)",
  "description": "string (min 1 char)",
  "classification": "internal",
  "priority": "medium"
}
```

**Response**: Returns created investigation object

### Get Investigation
**Endpoint**: `GET /api/osint/investigations/{investigation_id}`

**Response**: Investigation object with full details

### Update Investigation
**Endpoint**: `PUT /api/osint/investigations/{investigation_id}`

**Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "classification": "internal (optional)",
  "priority": "medium (optional)",
  "status": "active (optional)",
  "current_phase": "planning (optional)"
}
```

### Delete Investigation
**Endpoint**: `DELETE /api/osint/investigations/{investigation_id}`

**Response**:
```json
{
  "message": "Investigation inv-uuid deleted successfully"
}
```

### Investigation Targets

#### Create Target
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/targets`

**Request Body**:
```json
{
  "type": "person|organization|domain|etc",
  "identifier": "string",
  "aliases": ["string"],
  "priority": "medium",
  "collection_requirements": {}
}
```

#### List Targets
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/targets`

### Investigation Evidence

#### List Evidence
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/evidence`

#### Create Evidence
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/evidence`

**Request Body**:
```json
{
  "source": "string",
  "source_type": "string",
  "content": "string",
  "metadata": {},
  "reliability_score": 0.8,
  "relevance_score": 0.9
}
```

### Investigation Threats

#### List Threats
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/threats`

#### Create Threat
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/threats`

**Request Body**:
```json
{
  "title": "string",
  "description": "string",
  "threat_level": "low|medium|high|critical",
  "threat_type": "string",
  "targets": ["string"],
  "likelihood": 0.7,
  "impact": 0.8
}
```

### Investigation Reports

#### List Reports
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/reports`

#### Create Report
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/reports`

**Request Body**:
```json
{
  "title": "string",
  "content": "string",
  "format": "markdown|html|pdf",
  "classification": "internal",
  "recipients": ["email@example.com"]
}
```

### Investigation Timeline
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/timeline`

**Response**:
```json
{
  "investigation_id": "inv-uuid",
  "timeline": [
    {
      "type": "phase_change|target_added|evidence_collected|threat_identified",
      "timestamp": "2025-01-01T00:00:00Z",
      "details": {}
    }
  ]
}
```

### Advance Investigation Phase
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/advance-phase`

**Request Body**:
```json
{
  "next_phase": "reconnaissance|collection|analysis|synthesis|reporting"
}
```

### Agent Coordination

#### Get Investigation Agents
**Endpoint**: `GET /api/osint/investigations/{investigation_id}/agents`

#### Assign Agent
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/agents/assign`

**Request Body**:
```json
{
  "agent_id": "string",
  "agent_type": "COLLECTION|ANALYSIS|SPECIALIZED",
  "assigned_targets": ["string"],
  "current_task": "string",
  "status": "IDLE|ACTIVE|BUSY|ERROR",
  "performance_metrics": {}
}
```

#### Update Agent Status
**Endpoint**: `PUT /api/osint/agents/{agent_id}/status`

**Request Body**:
```json
{
  "status": "IDLE|ACTIVE|BUSY|ERROR",
  "task_details": {}
}
```

#### Assign Task to Agent
**Endpoint**: `POST /api/osint/agents/{agent_id}/tasks`

**Request Body**:
```json
{
  "type": "string",
  "description": "string",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "details": {}
}
```

#### Get Agent Performance
**Endpoint**: `GET /api/osint/agents/{agent_id}/performance`

### Search Operations

#### Web Search
**Endpoint**: `POST /api/osint/search`

**Request Body** (form-data):
```
query: string
max_results: 10 (optional)
engines: ["duckduckgo", "google"] (optional)
```

**Response**:
```json
{
  "success": true,
  "query": "string",
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "source": "string",
      "relevance_score": 0.8
    }
  ],
  "total_results": 50,
  "engines_used": ["duckduckgo"],
  "search_time": 1.23,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### Investigation Search
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/search`

**Request Body** (form-data):
```
query: string
max_results: 10 (optional)
```

#### Premium Search
**Endpoint**: `POST /api/osint/premium-search`

**Request Body** (form-data):
```
query: string
engines: ["duckduckgo", "brave"] (optional)
max_pages: 1 (optional)
use_browser: false (optional)
```

#### Investigation Premium Search
**Endpoint**: `POST /api/osint/investigations/{investigation_id}/premium-search`

#### Get Premium Search Engines
**Endpoint**: `GET /api/osint/premium-search/engines`

#### Test Premium Connectivity
**Endpoint**: `POST /api/osint/premium-search/test-connectivity`

### WebSocket
**Endpoint**: `WS /api/osint/ws/{investigation_id}`

Real-time updates for investigation events.

## Pipeline Management

### Create Pipeline
**Endpoint**: `POST /api/v1/pipelines`

**Request Body**:
```json
{
  "name": "string (1-100 chars)",
  "description": "string (min 1 char)",
  "urls": ["string"],
  "extraction_schema": {}
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "urls": ["string"],
    "extraction_schema": {},
    "code": "",
    "status": "idle",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

### Get Pipeline
**Endpoint**: `GET /api/v1/pipelines/{pipeline_id}`

### List Pipelines
**Endpoint**: `GET /api/v1/pipelines`

**Query Parameters**:
- `page`: int (default: 1, min: 1)
- `page_size`: int (default: 10, min: 1, max: 100)
- `search`: string (optional)
- `status`: `active|inactive|pending|completed|failed|cancelled|running|idle` (optional)

### Update Pipeline
**Endpoint**: `PUT /api/v1/pipelines/{pipeline_id}`

**Request Body**:
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "urls": ["string"] (optional),
  "extraction_schema": {} (optional),
  "code": "string" (optional)
}
```

### Delete Pipeline
**Endpoint**: `DELETE /api/v1/pipelines/{pipeline_id}`

### Run Pipeline
**Endpoint**: `POST /api/v1/pipelines/{pipeline_id}/run`

**Response**:
```json
{
  "success": true,
  "data": {
    "pipeline_id": "uuid",
    "status": "running",
    "message": "Pipeline execution started"
  }
}
```

### Get Pipeline Status
**Endpoint**: `GET /api/v1/pipelines/{pipeline_id}/status`

**Response**:
```json
{
  "success": true,
  "data": {
    "pipeline_id": "uuid",
    "status": "running",
    "updated_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Get Pipeline Results
**Endpoint**: `GET /api/v1/pipelines/{pipeline_id}/results`

**Response**:
```json
{
  "success": true,
  "data": {
    "pipeline_id": "uuid",
    "results": [
      {
        "url": "string",
        "success": true,
        "data": {},
        "error": null,
        "scraped_at": "2025-01-01T00:00:00Z"
      }
    ],
    "total": 10,
    "success": 8,
    "failed": 2,
    "status": "completed",
    "execution_time": 123.45
  }
}
```

### Export Pipeline Results
**Endpoint**: `POST /api/v1/pipelines/{pipeline_id}/export`

**Query Parameters**:
- `format`: `json|csv|excel` (default: json)

**Response**:
```json
{
  "success": true,
  "data": {
    "pipeline_id": "uuid",
    "format": "json",
    "filename": "pipeline_uuid_20250101_123456.json",
    "download_url": "/api/v1/pipelines/uuid/download/json",
    "file_size": 1024,
    "expires_at": 1234567890
  }
}
```

## Scraping Operations

### Execute Scraping
**Endpoint**: `POST /api/scraping/execute`

**Request Body**:
```json
{
  "urls": ["https://example.com"],
  "prompt": "Extract product information",
  "scraping_schema": {}
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Scraping task started"
}
```

### Get Scraping Status
**Endpoint**: `GET /api/scraping/status/{task_id}`

**Response**:
```json
{
  "task_id": "uuid",
  "status": "pending|running|completed|failed",
  "error": null
}
```

### Get Scraping Results
**Endpoint**: `GET /api/scraping/results/{task_id}`

**Response**:
```json
[
  {
    "url": "https://example.com",
    "success": true,
    "data": {},
    "error": null
  }
]
```

### Validate URL
**Endpoint**: `POST /api/scraping/validate-url`

**Request Body** (form-data):
```
url: https://example.com
```

**Response**:
```json
{
  "url": "https://example.com",
  "valid": true,
  "status_code": 200,
  "content_type": "text/html"
}
```

### Preview Scraping
**Endpoint**: `POST /api/scraping/preview`

**Request Body** (form-data):
```
url: https://example.com
selector: .product-title (optional)
```

**Response**:
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "description": "Page description",
  "headings": [
    {"tag": "h1", "text": "Heading text"}
  ],
  "links": [
    {"text": "Link text", "href": "/page"}
  ],
  "content_preview": "First 500 chars of content...",
  "content_length": 2500,
  "status": "success"
}
```

### Search URLs
**Endpoint**: `POST /api/scraping/search`

**Request Body**:
```json
{
  "query": "product search",
  "max_results": 5
}
```

**Response**:
```json
{
  "query": "product search",
  "enhanced_query": "product search ecommerce",
  "max_results": 5,
  "results": {
    "search_results": [],
    "intelligence_insights": {},
    "query_enhancement": {},
    "llm_provider": "openrouter"
  },
  "count": 5,
  "llm_enhanced": true
}
```

## Workflow Management

### Get Workflow
**Endpoint**: `GET /api/workflow/workflow/{pipeline_id}`

### Get Workflow Summary
**Endpoint**: `GET /api/workflow/workflow/{pipeline_id}/summary`

### Update URLs
**Endpoint**: `POST /api/workflow/workflow/{pipeline_id}/urls`

**Request Body**:
```json
[
  {
    "url": "https://example.com",
    "description": "Product page",
    "relevance": "medium",
    "validated": false
  }
]
```

### Update Schema
**Endpoint**: `POST /api/workflow/workflow/{pipeline_id}/schema`

**Request Body**:
```json
[
  {
    "name": "product_name",
    "type": "string",
    "description": "Product name",
    "required": true,
    "example": "iPhone 15"
  }
]
```

### Approve Action
**Endpoint**: `POST /api/workflow/workflow/{pipeline_id}/approve`

**Request Body**:
```json
{
  "approval_id": "uuid",
  "approved": true,
  "reason": "Looks good"
}
```

### Manual Transition
**Endpoint**: `POST /api/workflow/workflow/{pipeline_id}/transition`

**Request Body** (form-data):
```
target_phase: reconnaissance|collection|analysis|synthesis|reporting
reason: Manual transition (optional)
```

### Get Workflow History
**Endpoint**: `GET /api/workflow/workflow/{pipeline_id}/history`

### Get Phase Options
**Endpoint**: `GET /api/workflow/workflow/{pipeline_id}/phase-options`

## AI Investigations

### Start Investigation
**Endpoint**: `POST /api/ai-investigation/start`

**Request Body**:
```json
{
  "target": "string",
  "objective": "string",
  "scope": ["string"],
  "priority": "medium",
  "requirements": {}
}
```

**Response**:
```json
{
  "investigation_id": "uuid",
  "status": "initializing",
  "current_phase": "planning",
  "progress_percentage": 0.0,
  "estimated_completion": "2025-01-01T01:00:00Z",
  "message": "Investigation started"
}
```

### Get Investigation Status
**Endpoint**: `GET /api/ai-investigation/{investigation_id}/status`

### Approve Investigation Phase
**Endpoint**: `POST /api/ai-investigation/{investigation_id}/approve-phase`

**Request Body**:
```json
{
  "phase": "planning|collection|analysis|synthesis",
  "notes": "Approved to proceed"
}
```

### Get Investigation Report
**Endpoint**: `GET /api/ai-investigation/{investigation_id}/report`

### Get Active Investigations
**Endpoint**: `GET /api/ai-investigation/active`

**Response**:
```json
[
  {
    "investigation_id": "uuid",
    "target": "string",
    "objective": "string",
    "status": "running",
    "current_phase": "collection",
    "progress_percentage": 45.0,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Cancel Investigation
**Endpoint**: `DELETE /api/ai-investigation/{investigation_id}`

## Execution Management

### Execute Pipeline
**Endpoint**: `POST /api/execution/execute`

**Request Body**:
```json
{
  "pipeline_id": "uuid",
  "code": "python code string",
  "urls": ["https://example.com"],
  "execution_schema": {},
  "api_key": "optional_api_key"
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "url": "https://example.com",
      "data": {},
      "success": true
    }
  ],
  "errors": [],
  "execution_time": 45.67,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Enhanced Workflow v2

### Get Agent Mode
**Endpoint**: `GET /api/v2/workflow/agent-mode`

**Response**:
```json
{
  "mode": "tools-based|state-based",
  "features": {
    "tools_based": {
      "enabled": true,
      "description": "Simplified tool-based agent",
      "advantages": ["Simpler state management", "Better error recovery"]
    },
    "state_based": {
      "enabled": false,
      "description": "Original state machine agent",
      "advantages": ["Fine-grained control", "Complex workflows"]
    }
  }
}
```

### Search URLs (v2)
**Endpoint**: `POST /api/v2/workflow/search`

**Request Body** (form-data):
```
search_query: string
pipeline_id: uuid
max_results: 10 (optional)
```

**Response**:
```json
{
  "success": true,
  "query": "string",
  "urls": ["https://example.com"],
  "count": 5,
  "agent_mode": "tools-based"
}
```

### Scrape URLs (v2)
**Endpoint**: `POST /api/v2/workflow/scrape`

**Request Body**:
```json
{
  "pipeline_id": "uuid",
  "urls": ["https://example.com"],
  "extraction_prompt": "Extract product information"
}
```

**Response**:
```json
{
  "success": true,
  "urls_scraped": 5,
  "results": [
    {
      "url": "https://example.com",
      "success": true,
      "data": {}
    }
  ],
  "agent_mode": "tools-based"
}
```

### Get Available Tools
**Endpoint**: `GET /api/v2/workflow/tools`

**Response**:
```json
{
  "tools": [
    {
      "name": "smart_scraper",
      "description": "Extract structured data from a single webpage",
      "parameters": ["website_url", "user_prompt"],
      "use_cases": ["Extract contact information", "Get product details"]
    },
    {
      "name": "smart_crawler",
      "description": "Crawl and extract data from multiple pages",
      "parameters": ["website_url", "user_prompt", "max_depth", "max_pages"],
      "use_cases": ["Scrape entire product catalogs", "Collect blog data"]
    }
  ]
}
```

### Migrate Workflow
**Endpoint**: `POST /api/v2/workflow/migrate`

**Response**:
```json
{
  "success": true,
  "original_workflow": {
    "phase": "planning",
    "urls_count": 10,
    "schema_fields_count": 5,
    "has_code": true
  },
  "migration_result": {},
  "recommendations": [
    "Use smart_scraper for single-page extraction",
    "Use smart_crawler for multi-page scraping"
  ]
}
```

## Common Data Models

### Status Enum
- `ACTIVE`
- `INACTIVE`
- `PENDING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`
- `RUNNING`
- `IDLE`

### Priority Enum
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

### Classification Enum
- `PUBLIC`
- `INTERNAL`
- `CONFIDENTIAL`
- `SECRET`
- `TOP_SECRET`

### Workflow Phase Enum
- `PLANNING`
- `RECONNAISSANCE`
- `COLLECTION`
- `ANALYSIS`
- `SYNTHESIS`
- `REPORTING`

### User Role Enum
- `ADMIN`
- `ANALYST`
- `VIEWER`

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "field": "field_name"
  },
  "metadata": {
    "timestamp": "2025-01-01T00:00:00Z",
    "request_id": "uuid",
    "version": "v1"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - 400
- `UNAUTHORIZED` - 401
- `FORBIDDEN` - 403
- `NOT_FOUND` - 404
- `BUSINESS_RULE_VIOLATION` - 400
- `INTERNAL_ERROR` - 500
- `SERVICE_UNAVAILABLE` - 503
- `RATE_LIMIT_EXCEEDED` - 429

## Rate Limiting & Security

### Authentication
- JWT tokens with expiration
- Refresh token support
- Token blacklisting on logout

### Rate Limiting
- Login attempts limited
- API endpoint rate limiting
- IP-based throttling

### CORS
- Configurable origins
- All methods and headers allowed in development

### Security Headers
- All CORS headers supported
- Content-Type validation
- Request/response logging

## WebSocket Endpoints

### Pipeline WebSocket
**Endpoint**: `WS /api/ws/{pipeline_id}`

Real-time communication for pipeline execution updates.

### OSINT Investigation WebSocket
**Endpoint**: `WS /api/osint/ws/{investigation_id}`

Real-time updates for investigation events.

### WebSocket Message Format
```json
{
  "type": "update|error|completion",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Pagination

All list endpoints support pagination with these parameters:
- `page`: Page number (default: 1, min: 1)
- `page_size`: Items per page (default: 10, min: 1, max: 100)
- `offset`: Number of items to skip (alternative to page)

## Sorting & Filtering

Many endpoints support sorting and filtering:
- `sort_by`: Field to sort by
- `sort_order`: `asc|desc` (default: `asc`)
- `search`: Text search across relevant fields
- Various enum-based filters depending on the endpoint

## File Operations

### Export Formats
- JSON - Structured data export
- CSV - Tabular data export
- Excel - Spreadsheet format (planned)

### File Downloads
Export endpoints provide download URLs that expire after 1 hour for security.

---

## Notes

1. All timestamps are in ISO 8601 format (UTC)
2. All IDs are UUID strings
3. Authentication is required for most endpoints
4. Rate limiting applies to prevent abuse
5. WebSocket connections require authentication token in query parameter
6. File exports are temporary and expire after 1 hour
7. All endpoints return standardized response formats
8. Error details include field-specific information for validation errors
9. The API supports both sync and async operations
10. Background processing is used for long-running tasks like scraping

## Version History

- **v1.0**: Initial API release with core functionality
- **v1.1**: Added enhanced workflow v2 endpoints
- **v1.2**: Premium search capabilities added
- **v1.3**: AI investigation endpoints implemented
- **v1.4**: Enhanced error handling and validation