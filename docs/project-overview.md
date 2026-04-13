# ScrapeCraft OSINT Platform - Project Overview

## Executive Summary

ScrapeCraft is a comprehensive Open Source Intelligence (OSINT) platform designed for automated data collection, analysis, and investigation workflows. The platform combines web scraping capabilities, AI-powered analysis, and real-time collaboration features to support intelligence gathering operations.

**Project Type:** Multi-part Software System  
**Architecture Pattern:** Microservices with Shared Infrastructure  
**Primary Language:** Python (Backend), TypeScript (Frontend)  
**Repository Structure:** Multi-part (4 distinct parts)

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI + Python 3.12 | REST API, WebSocket services, async processing |
| **Frontend** | React 18 + TypeScript 18 | User interface, real-time dashboards |
| **Database** | PostgreSQL + Redis | Primary data storage, caching, task queues |
| **Infrastructure** | Kubernetes + Docker | Container orchestration, deployment |
| **AI/ML** | OpenAI + LangChain + ScrapeGraphAI | LLM integration, intelligent scraping |
| **Authentication** | JWT + OAuth | User authentication and authorization |
| **Real-time** | WebSocket + Redis Pub/Sub | Live updates and notifications |

## Architecture Classification

**Repository Type:** Multi-part system with 4 distinct components:
1. **Backend** - FastAPI REST API and WebSocket services
2. **Frontend** - React web application  
3. **Infrastructure** - Kubernetes deployment and monitoring
4. **BMad Framework** - CLI tooling and AI agent system

**Integration Pattern:** Service-oriented architecture with:
- REST API communication between frontend and backend
- WebSocket for real-time updates
- Shared PostgreSQL database and Redis cache
- Kubernetes for service orchestration

## Project Structure

```
scrapecraft/
├── backend/              # FastAPI Python backend
│   ├── app/             # Application source code
│   ├── tests/           # Backend test suite
│   ├── alembic/         # Database migrations
│   └── requirements.txt # Python dependencies
├── frontend/            # React TypeScript frontend
│   ├── src/            # Application source code
│   ├── public/         # Static assets
│   └── package.json    # Node.js dependencies
├── infrastructure/      # Kubernetes and deployment configs
│   ├── k8s/            # Kubernetes manifests
│   └── helm/           # Helm charts
├── .bmad/              # BMad framework configuration
│   ├── bmm/            # Core BMad system
│   └── agents/         # AI agent definitions
└── docs/               # Generated documentation
```

## Key Features

### Core Capabilities
- **Automated Web Scraping** - Intelligent data extraction from web sources
- **AI-Powered Analysis** - LLM-driven content analysis and summarization
- **Real-time Collaboration** - Multi-user investigation workflows
- **Extensible Architecture** - Plugin system for custom data sources
- **Comprehensive Monitoring** - Built-in logging and performance metrics

### Technical Highlights
- **Microservices Architecture** - Scalable, maintainable service design
- **Real-time Updates** - WebSocket-based live data streaming
- **Containerized Deployment** - Docker/Kubernetes orchestration
- **Modern Development Stack** - FastAPI, React, TypeScript with full type safety
- **Comprehensive Testing** - Unit, integration, and end-to-end test coverage

## Documentation Navigation

### Architecture Documentation
- [Backend Architecture](./backend-architecture.md) - FastAPI system design and patterns
- [Frontend Architecture](./frontend-architecture.md) - React application structure and state management
- [Infrastructure Architecture](./infrastructure-architecture.md) - Kubernetes deployment and monitoring
- [BMad Framework Architecture](./bmad-framework-architecture.md) - CLI and AI agent system

### Technical Documentation
- [Source Tree Analysis](./source-tree-analysis.md) - Complete annotated directory structure
- [API Contracts](./api-contracts-backend.md) - Backend API endpoints and schemas
- [Data Models](./data-models-backend.md) - Database schema and relationships
- [Component Inventory](./component-inventory-frontend.md) - React components and UI patterns

### Development Documentation
- [Development Guide](./development-guide.md) - Setup instructions and development workflow
- [Deployment Guide](./deployment-guide.md) - Production deployment procedures
- [Contribution Guide](./contribution-guide.md) - Code standards and contribution process

### Integration Documentation
- [Integration Architecture](./integration-architecture.md) - Service communication patterns
- [API Documentation](./api-documentation-backend.md) - Detailed API reference
- [Testing Strategy](./testing-strategy.md) - Test frameworks and approaches

## Getting Started

### For Developers
1. **Prerequisites**: Docker, Node.js 18+, Python 3.12+
2. **Local Setup**: See [Development Guide](./development-guide.md)
3. **API Documentation**: See [Backend Architecture](./backend-architecture.md)
4. **Frontend Development**: See [Frontend Architecture](./frontend-architecture.md)

### For Operations
1. **Deployment**: See [Deployment Guide](./deployment-guide.md)
2. **Infrastructure**: See [Infrastructure Architecture](./infrastructure-architecture.md)
3. **Monitoring**: Built-in Prometheus/Grafana stack

### For Product Planning
1. **System Overview**: This document provides high-level context
2. **Feature Planning**: Reference architecture documents for technical constraints
3. **Integration Planning**: See [Integration Architecture](./integration-architecture.md)

## Project Status

**Current Version:** Active development  
**Last Updated:** 2025-11-10  
**Documentation Coverage:** Comprehensive (architecture, API, deployment, development)

**Active Development Areas:**
- AI/ML integration with multiple LLM providers
- Advanced scraping workflows and automation
- Real-time collaboration features
- Performance optimization and scaling

---

*This overview serves as the entry point for understanding the ScrapeCraft OSINT platform. For detailed technical information, please refer to the specific architecture and documentation files linked above.*