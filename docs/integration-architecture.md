# Integration Architecture

## Overview

The ScrapeCraft OSINT Platform is designed as a microservices architecture with shared infrastructure, enabling seamless communication between four distinct parts: Backend API, Web Frontend, Infrastructure layer, and BMad Framework CLI tools.

## Architecture Type

**Microservices with Shared Infrastructure**

- **Communication Pattern:** Service-to-service via HTTP/WebSocket APIs
- **Data Flow:** Unidirectional and bidirectional streams based on use case
- **Shared Resources:** PostgreSQL database, Redis cache, Kubernetes orchestration
- **Service Discovery:** Docker Compose (development) / Kubernetes DNS (production)

## Integration Points

### 1. Frontend ↔ Backend Integration

**Protocol:** HTTP REST API + WebSocket  
**Endpoint:** `http://localhost:8000/api/*`  
**WebSocket:** `ws://localhost:8000/api/ws/{pipeline_id}`

#### Communication Flow:
```
Frontend → HTTP Request → Backend API → Database/External APIs
Backend → WebSocket Push → Frontend (real-time updates)
```

#### Key Integration Areas:
- **Authentication:** JWT tokens with refresh mechanism
- **API Consumption:** Axios HTTP client with custom interceptors
- **Real-time Updates:** WebSocket connection for pipeline status
- **Error Handling:** Centralized error propagation to UI

#### API Routes Consumed:
- `/api/osint/*` - OSINT investigation endpoints
- `/api/auth/*` - Authentication and authorization
- `/api/pipelines/*` - Pipeline management
- `/api/scraping/*` - Web scraping operations
- `/api/execution/*` - Task execution monitoring
- `/api/workflow/*` - Workflow management
- `/api/ai-investigation/*` - AI-powered investigations

### 2. Backend ↔ Infrastructure Integration

**Protocol:** SQL + Redis + Kubernetes Services  
**Components:** PostgreSQL, Redis, Kubernetes

#### Data Persistence:
- **PostgreSQL:** Primary data store for investigations, users, workflows
- **Redis:** Caching layer and task queue storage
- **Connection Pooling:** SQLAlchemy async connection management

#### Infrastructure Services:
- **Database Service:** `postgres` Kubernetes service
- **Cache Service:** `redis` Kubernetes service
- **Service Discovery:** Kubernetes DNS resolution
- **Load Balancing:** Kubernetes Service load balancer

#### Deployment Coupling:
- **Stateful Service:** Backend requires database connectivity
- **Health Checks:** Kubernetes liveness/readiness probes
- **Configuration Management:** Environment-specific configs

### 3. Infrastructure ↔ All Parts Integration

**Protocol:** Kubernetes Services + Docker Compose  
**Scope:** Orchestration and resource management

#### Orchestration Responsibilities:
- **Service Deployment:** Kubernetes Deployments and Services
- **Resource Management:** CPU/memory limits and requests
- **Network Policies:** Service-to-service communication rules
- **Secret Management:** Kubernetes secrets for sensitive data

#### Environment Configuration:
- **Development:** Docker Compose with local volumes
- **Production:** Kubernetes with persistent volumes
- **Configuration Sources:** ConfigMaps and environment variables

### 4. BMad Framework ↔ All Parts Integration

**Protocol:** CLI Commands + File System  
**Scope:** Development tooling and workflow automation

#### Framework Capabilities:
- **Workflow Orchestration:** Multi-agent coordination
- **Documentation Generation:** Automated project documentation
- **Development Tooling:** Code generation and analysis
- **Status Tracking:** Progress monitoring across components

#### Integration Patterns:
- **File-based Configuration:** YAML workflow definitions
- **Command-line Interface:** Unified development commands
- **State Management:** JSON-based progress tracking
- **Cross-part Operations:** Coordinated actions across components

## Data Flow Architecture

### User Request Flow
```
User Interface (Frontend) 
    ↓ HTTP Request
Backend API Services
    ↓ Business Logic
External APIs / Scraping Engines
    ↓ Data Processing
PostgreSQL Database
    ↓ Response
Frontend (via HTTP/WebSocket)
```

### Real-time Update Flow
```
Backend Events (Pipeline Status, Investigation Results)
    ↓ WebSocket Broadcast
Connected Frontend Clients
    ↓ UI Updates
User Dashboard
```

### Background Task Flow
```
Scheduled Tasks / User Actions
    ↓ Task Queue (Redis)
Background Workers
    ↓ Processing
Database Updates
    ↓ Notification
WebSocket Push to Frontend
```

### Infrastructure Monitoring Flow
```
Kubernetes Events / Metrics
    ↓ Collection
Prometheus/Grafana Stack
    ↓ Alerting
Notification Channels
```

## Service Discovery Configuration

### Development Environment (Docker Compose)
```yaml
services:
  backend:
    # Service name: "backend"
    # Accessible as: http://backend:8000
  
  frontend:
    # Service name: "frontend"
    # Accessible as: http://frontend:3000
    
  db:
    # Service name: "db"
    # Accessible as: postgresql://db:5432
    
  redis:
    # Service name: "redis"
    # Accessible as: redis://redis:6379
```

### Production Environment (Kubernetes)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

## Shared Resources Architecture

### Database Layer (PostgreSQL)
- **Shared Across:** Backend services only
- **Connection Management:** Connection pooling via SQLAlchemy
- **Schema Organization:** Separate schemas per domain
- **Backup Strategy:** Kubernetes volume snapshots

### Cache Layer (Redis)
- **Shared Across:** Backend services and background workers
- **Use Cases:** Session storage, task queues, caching
- **Data Persistence:** Configurable TTL and persistence
- **Clustering:** Redis Cluster for high availability

### Monitoring Stack
- **Centralized Logging:** ELK stack or similar
- **Metrics Collection:** Prometheus + Grafana
- **Alert Management:** AlertManager with notification routing
- **Distributed Tracing:** Jaeger or OpenTelemetry

### Secret Management
- **Development:** Environment variables and .env files
- **Production:** Kubernetes secrets with RBAC
- **Rotation:** Automated secret rotation policies
- **Access Control:** Principle of least privilege

## Deployment Integration Patterns

### Frontend Deployment
- **Strategy:** Independent deployment (nginx static files)
- **CDN Integration:** Static asset optimization
- **Version Management:** Build-specific asset paths
- **Rollback:** Blue-green deployment support

### Backend Deployment
- **Strategy:** Rolling updates with health checks
- **Database Migrations:** Automated schema updates
- **Dependency Management:** Service dependency resolution
- **Graceful Shutdown:** Connection draining and cleanup

### Infrastructure Deployment
- **Strategy:** GitOps with Kubernetes manifests
- **Resource Provisioning:** Automated infrastructure setup
- **Configuration Drift:** Continuous reconciliation
- **Multi-environment:** Dev/staging/prod parity

### BMad Framework Deployment
- **Strategy:** Package distribution and installation
- **Version Management:** Semantic versioning compatibility
- **Configuration:** Framework-specific config files
- **Updates:** Over-the-air updates and rollback

## Security Integration

### Authentication Flow
```
Frontend Login Request
    ↓
Backend Authentication Service
    ↓
JWT Token Generation
    ↓
Token Storage (Frontend)
    ↓
Subsequent API Calls with Bearer Token
    ↓
Backend Token Validation
    ↓
Access Granted/Denied
```

### Authorization Integration
- **RBAC Implementation:** Role-based access control
- **API Gateway:** Centralized policy enforcement
- **Service-to-Service:** mTLS for internal communication
- **Audit Logging:** Comprehensive access logging

### Network Security
- **Ingress Control:** Kubernetes NetworkPolicies
- **Firewall Rules:** Service-specific port restrictions
- **TLS Termination:** Edge-level encryption
- **Certificate Management:** Automated cert rotation

## Performance Integration

### Caching Strategy
- **Application Level:** Redis for frequently accessed data
- **Database Level:** Query result caching
- **CDN Level:** Static asset caching
- **Browser Level:** Client-side caching headers

### Load Balancing
- **Frontend:** CDN distribution
- **Backend:** Kubernetes Service load balancing
- **Database:** Read replicas and connection pooling
- **Cache:** Redis Cluster distribution

### Scalability Patterns
- **Horizontal Scaling:** Pod autoscaling based on metrics
- **Vertical Scaling:** Resource limit adjustments
- **Database Scaling:** Read replicas and sharding
- **Cache Scaling:** Redis Cluster expansion

## Monitoring and Observability

### Health Check Integration
- **Backend:** `/health` endpoint with dependency checks
- **Frontend:** Liveness probes and error tracking
- **Database:** Connection health monitoring
- **Cache:** Redis ping and memory usage

### Metrics Collection
- **Application Metrics:** Custom business metrics
- **Infrastructure Metrics:** CPU, memory, network
- **Database Metrics:** Query performance and connections
- **User Metrics:** Application usage analytics

### Logging Integration
- **Structured Logging:** JSON format with correlation IDs
- **Log Aggregation:** Centralized log collection
- **Log Analysis:** Search and alerting capabilities
- **Audit Trails:** Compliance and security logging

## Disaster Recovery Integration

### Backup Strategy
- **Database Backups:** Automated daily snapshots
- **Configuration Backups:** Git-based configuration storage
- **Asset Backups:** Static asset replication
- **State Backups:** Application state serialization

### Failover Patterns
- **Database Failover:** Primary/replica promotion
- **Cache Failover:** Redis Cluster failover
- **Service Failover:** Pod restart and rescheduling
- **Geographic Failover:** Multi-region deployment

### Recovery Procedures
- **Automated Recovery:** Self-healing mechanisms
- **Manual Recovery:** Runbooks and procedures
- **Data Recovery:** Point-in-time restoration
- **Service Recovery:** Graceful service restart

## Development Workflow Integration

### Local Development
- **Docker Compose:** Complete local stack
- **Hot Reloading:** Code change detection
- **Debug Support:** Integrated debugging tools
- **Testing:** Local test environment

### CI/CD Integration
- **Source Control:** Git-based workflow
- **Automated Testing:** Unit, integration, e2e tests
- **Build Pipeline:** Automated build and packaging
- **Deployment Pipeline:** Automated deployment to environments

### Code Quality Integration
- **Linting:** Automated code quality checks
- **Security Scanning:** Vulnerability assessment
- **Dependency Management:** Automated updates
- **Documentation:** Auto-generated API docs

---

*This integration architecture document serves as the blueprint for understanding how all parts of the ScrapeCraft OSINT Platform work together to deliver a cohesive OSINT investigation platform.*