# Backend Architecture Documentation

## Overview

The ScrapeCraft backend is a sophisticated FastAPI-based microservice designed for OSINT (Open Source Intelligence) operations, AI-powered investigations, and web scraping automation. It implements a modern async architecture with comprehensive security, monitoring, and scalability features.

## Architecture Stack

### Core Framework
- **FastAPI**: High-performance async web framework
- **Python 3.12**: Modern Python with enhanced performance
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

### Database & Storage
- **PostgreSQL**: Primary relational database
- **Redis**: Caching, session storage, and task queues
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migration management

### AI & ML Integration
- **LangChain**: AI/ML framework for LLM orchestration
- **OpenAI**: Primary LLM provider
- **OpenRouter**: Multi-provider LLM gateway
- **ScrapeGraphAI**: AI-powered web scraping
- **Ollama**: Local LLM support (optional)

### Security & Authentication
- **JWT**: Token-based authentication with refresh tokens and blacklisting
- **bcrypt**: Password hashing with secure salt rounds
- **CORS**: Cross-origin resource sharing with origin whitelisting
- **Rate limiting**: Advanced API abuse prevention with IP-based throttling
- **RBAC**: Role-based access control with granular permissions
- **Security Headers**: HSTS, CSP, X-Frame-Options, and other security headers
- **Input Validation**: Comprehensive request validation and sanitization
- **Audit Logging**: Complete security event tracking and forensic analysis

### Monitoring & Observability
- **Structured logging**: Comprehensive audit trails
- **Health checks**: Service health monitoring
- **Metrics**: Performance tracking
- **WebSocket**: Real-time communication

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API route definitions
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── osint.py           # OSINT operations
│   │   ├── scraping.py        # Web scraping
│   │   ├── pipelines.py       # Processing pipelines
│   │   ├── execution.py       # Task execution
│   │   ├── workflow.py        # Workflow management
│   │   └── ai_investigation.py # AI investigations
│   ├── core/                  # Core application logic
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # Security utilities
│   │   └── database.py        # Database connections
│   ├── models/                # Data models
│   │   ├── user.py           # User management
│   │   ├── investigation.py   # Investigation data
│   │   └── pipeline.py       # Pipeline definitions
│   ├── services/              # Business logic services
│   │   ├── websocket.py      # WebSocket management
│   │   ├── workflow_manager.py # Workflow orchestration
│   │   ├── task_storage.py   # Task persistence
│   │   └── openrouter.py     # LLM integration
│   └── middleware/            # Custom middleware
├── tests/                     # Test suite
├── alembic/                   # Database migrations
├── requirements.txt           # Python dependencies
└── Dockerfile                # Container configuration
```

## API Architecture

### RESTful Endpoints

The backend exposes 70+ REST endpoints organized into logical modules:

#### Authentication (`/api/auth`)
- `POST /login` - User authentication
- `POST /register` - User registration
- `POST /refresh` - Token refresh
- `GET /me` - Current user info

#### OSINT Operations (`/api/osint`)
- `POST /investigate` - Start OSINT investigation
- `GET /results/{id}` - Get investigation results
- `POST /enrich` - Data enrichment
- `GET /sources` - Available OSINT sources

#### Web Scraping (`/api/scraping`)
- `POST /scrape` - Initiate scraping task
- `GET /status/{task_id}` - Task status
- `GET /results/{task_id}` - Scraping results
- `POST /bulk-scrape` - Bulk operations

#### AI Investigation (`/api/ai-investigation`)
- `POST /analyze` - AI analysis request
- `GET /insights/{id}` - Investigation insights
- `POST /report` - Generate reports
- `GET /models` - Available AI models

### WebSocket Communication

Real-time communication via WebSocket at `/api/ws/{pipeline_id}`:

```typescript
// Message format
{
  "type": "user_message|system_message|error|status",
  "content": "message content",
  "metadata": {
    "pipeline_id": "string",
    "timestamp": "ISO8601",
    "user_id": "string"
  }
}
```

## Database Architecture

### Schema Design

The database uses a relational schema with 20+ tables:

#### Core Tables
- `users` - User management and authentication
- `investigations` - OSINT investigation records
- `pipelines` - Processing pipeline definitions
- `tasks` - Asynchronous task tracking
- `results` - Investigation results storage

#### Supporting Tables
- `audit_logs` - Comprehensive audit trail
- `api_keys` - External API credentials
- `scraping_targets` - Web scraping configurations
- `ai_models` - AI model configurations
- `user_sessions` - Active session management

### Migration Strategy

Database migrations are managed through Alembic:
- Version-controlled schema changes
- Automatic rollback capabilities
- Production-safe deployment
- Data preservation guarantees

## Security Architecture - Version 2.0

### **Zero-Trust Security Implementation**

#### **Authentication & Authorization Flow**
1. **Multi-Factor Authentication**: Optional MFA with TOTP support
2. **JWT Token Management**: Access tokens (15 min) + Refresh tokens (7 days) + blacklisting
3. **Session Management**: Secure session tracking with automatic cleanup
4. **Role-Based Access Control**: Admin, Analyst, Viewer roles with granular permissions
5. **API Key Management**: Secure external service credential storage
6. **Token Refresh**: Automatic token rotation and secure refresh mechanism

#### **Advanced Security Measures**
- **Defense-in-Depth Strategy**: Multiple security layers with comprehensive controls
- **Rate Limiting**: Intelligent throttling (100 req/min per user, IP-based limits)
- **Input Validation**: Comprehensive Pydantic schemas with custom validators
- **SQL Injection Prevention**: ORM parameterization with query logging
- **XSS Protection**: Content Security Policy and input sanitization
- **CSRF Protection**: Token-based CSRF prevention for state-changing operations
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **CORS Configuration**: Strict origin whitelist with credential support

#### **Data Protection & Privacy**
- **Encryption at Rest**: AES-256 encryption for sensitive data
- **Encryption in Transit**: TLS 1.3 with perfect forward secrecy
- **Data Classification**: Automatic data classification and handling
- **Secure Key Management**: Hardware security module (HSM) integration
- **Data Retention**: Automated data lifecycle management
- **Privacy Controls**: GDPR/CCPA compliance features

#### **Threat Detection & Response**
- **Real-time Monitoring**: Continuous security event monitoring
- **Anomaly Detection**: ML-based threat pattern recognition
- **Automated Response**: Automatic threat containment and alerting
- **Security Analytics**: Comprehensive security dashboards and reporting
- **Incident Response**: Automated incident handling and forensic analysis
- **Vulnerability Scanning**: Continuous automated security scanning

#### **Infrastructure Security**
- **Container Security**: Non-root containers with security contexts
- **Network Security**: Network policies and micro-segmentation
- **Secret Management**: Kubernetes secrets with rotation policies
- **Pod Security**: Pod Security Standards enforcement
- **Resource Limits**: CPU/memory limits to prevent DoS attacks
- **Health Monitoring**: Comprehensive health checks and monitoring

#### **Compliance & Audit**
- **Comprehensive Audit Logging**: All actions logged with immutable storage
- **Compliance Reporting**: Automated GDPR, CCPA, and government compliance reports
- **Data Governance**: Data lineage and provenance tracking
- **Access Auditing**: Complete access attempt logging and analysis
- **Risk Assessment**: Continuous risk monitoring and assessment
- **Security Certifications**: SOC 2, ISO 27001, and FedRAMP readiness

## Performance Architecture

### Async Processing

- **FastAPI async/await**: Non-blocking I/O
- **Async SQLAlchemy**: Concurrent database queries
- **Redis queues**: Background task processing
- **Connection pooling**: Database connection reuse

### Caching Strategy

- **Redis caching**: Frequently accessed data
- **Application-level cache**: In-memory storage
- **API response caching**: Redundant request prevention
- **Session caching**: User session persistence

### Scalability Features

- **Horizontal scaling**: Stateless design
- **Load balancing**: Multiple instance support
- **Database pooling**: Connection management
- **Task queues**: Background processing

## Integration Architecture

### External Service Integration

#### LLM Providers
- **OpenAI**: GPT models for analysis
- **OpenRouter**: Multi-provider gateway
- **Ollama**: Local model hosting

#### OSINT Sources
- **Whois API**: Domain information
- **Social media APIs**: Public data extraction
- **News APIs**: Article and media monitoring
- **Government databases**: Public record access

#### Web Scraping
- **ScrapeGraphAI**: AI-powered scraping
- **Playwright**: Browser automation
- **BeautifulSoup**: HTML parsing
- **Selenium**: Legacy browser support

### Internal Service Communication

- **WebSocket manager**: Real-time updates
- **Task storage**: Redis-based persistence
- **Workflow engine**: Pipeline orchestration
- **Event system**: Async messaging

## Development Architecture

### Configuration Management

- **Environment variables**: Sensitive data
- **YAML configs**: Structured settings
- **Validation**: Configuration verification
- **Environment-specific**: Dev/staging/prod

### Testing Architecture

- **Unit tests**: pytest framework
- **Integration tests**: API endpoint testing
- **Security tests**: Vulnerability scanning
- **Performance tests**: Load testing

### Code Quality

- **Type hints**: Full type annotation
- **Black**: Code formatting
- **Ruff**: Linting and analysis
- **MyPy**: Static type checking
- **Bandit**: Security scanning

## Deployment Architecture

### Container Strategy

- **Multi-stage builds**: Optimized Docker images
- **Security hardening**: Non-root users
- **Health checks**: Container monitoring
- **Resource limits**: Memory/CPU constraints

### Orchestration

- **Kubernetes**: Production deployment
- **Docker Compose**: Development environment
- **Service discovery**: DNS-based resolution
- **Configuration maps**: External configuration

### Monitoring & Logging

- **Structured logging**: JSON format
- **Health endpoints**: Service monitoring
- **Metrics collection**: Performance tracking
- **Error tracking**: Comprehensive reporting

## Conclusion

The ScrapeCraft backend represents a modern, secure, and scalable architecture for OSINT operations. Its modular design, comprehensive security measures, and extensive integration capabilities make it suitable for both development and production environments.

The architecture supports:
- **High concurrency** through async processing
- **Scalability** via stateless design
- **Security** with comprehensive protection
- **Maintainability** through modular structure
- **Extensibility** via plugin architecture

This foundation enables rapid development of OSINT tools while maintaining enterprise-grade reliability and performance.