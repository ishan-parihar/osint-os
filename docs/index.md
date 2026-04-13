# ScrapeCraft OSINT Platform - Documentation Index

## Project Overview

**Type:** Multi-part project with 4 parts  
**Primary Language:** Python/TypeScript  
**Architecture:** Microservices with shared infrastructure  

## Quick Reference

### Backend (backend)
**Type:** Backend API  
**Tech Stack:** FastAPI, Python, PostgreSQL, Redis  
**Root:** /home/ishanp/Documents/GitHub/scrapecraft/backend  

### Frontend (frontend)  
**Type:** Web Frontend  
**Tech Stack:** React, TypeScript, Tailwind CSS  
**Root:** /home/ishanp/Documents/GitHub/scrapecraft/frontend  

### Infrastructure (infrastructure)
**Type:** Infrastructure  
**Tech Stack:** Kubernetes, Docker, GitHub Actions  
**Root:** /home/ishanp/Documents/GitHub/scrapecraft  

### BMad Framework (bmm-system)
**Type:** CLI  
**Tech Stack:** YAML, Python, Shell  
**Root:** /home/ishanp/Documents/GitHub/scrapecraft  

## Generated Documentation

- [Project Overview](./project-overview.md)
- [Architecture - Backend](./backend-architecture.md)
- [Architecture - Frontend](./frontend-architecture.md)  
- [Architecture - Infrastructure](./infrastructure-architecture.md)
- [Architecture - BMad Framework](./bmad-framework-architecture.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Component Inventory - Frontend](./component-inventory-frontend.md)
- [Development Guide](./development-guide.md)
- [Deployment Guide](./deployment-guide.md)
- [API Contracts - Backend](./api-contracts-backend.md)
- [Data Models - Backend](./data-models-backend.md)
- [Integration Architecture](./integration-architecture.md)
- [Component Inventory - Backend](./component-inventory-backend.md)
- [Component Inventory - Infrastructure](./component-inventory-infrastructure.md)
- [Component Inventory - BMad Framework](./component-inventory-bmm-system.md) _(To be generated)_
- [API Contracts - Frontend](./api-contracts-frontend.md) _(To be generated)_
- [Data Models - Frontend](./data-models-frontend.md) _(To be generated)_
- [Data Models - Infrastructure](./data-models-infrastructure.md) _(To be generated)_
- [Data Models - BMad Framework](./data-models-bmm-system.md) _(To be generated)_

## Existing Documentation

- [README.md](../README.md) - Main project README with setup instructions
- [AGENTS.md](../AGENTS.md) - Development guidelines and build/test commands
- [INTEGRATED_README.md](./INTEGRATED_README.md) - Integrated project documentation
- [BACKEND_RESTRUCTURE_PLAN.md](./BACKEND_RESTRUCTURE_PLAN.md) - Backend restructuring plan
- [CONSOLIDATION_COMPLETE.md](./CONSOLIDATION_COMPLETE.md) - Project consolidation report

## Getting Started

### For Backend Development
1. Navigate to `backend/` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Start development server: `python dev_server.py`
4. View API docs at: http://localhost:8000/docs

### For Frontend Development  
1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Start development server: `npm start`
4. Access application at: http://localhost:3000

### For Infrastructure Setup
1. Ensure Docker and Docker Compose are installed
2. Run: `docker-compose up -d` to start all services
3. Check Kubernetes configs in `k8s/` for production deployment

### For BMad Framework Usage
1. Use commands from `.gemini/commands/` directory
2. Run `*workflow-init` to start new development workflows
3. Check `*workflow-status` for current progress

## Development Quick Reference

### Backend Commands
```bash
cd backend
python dev_server.py                    # Start development server
pytest -v                              # Run all tests
pytest tests/test_specific.py -v       # Run single test file
```

### Frontend Commands
```bash
cd frontend  
npm start                               # Start development server
npm test                                # Run all tests
npm run build                           # Production build
```

### Testing
```bash
python -m pytest -v                    # Run all Python tests
python osint_cli.py --help             # Test CLI functionality
```

## Architecture Navigation

### Full-Stack Features
Reference both part architectures + integration-architecture.md

### Backend-Only Features  
Reference backend-architecture.md + api-contracts-backend.md + data-models-backend.md

### Frontend-Only Features
Reference frontend-architecture.md + component-inventory-frontend.md

### Infrastructure Changes
Reference infrastructure-architecture.md + deployment-guide.md

### BMad Framework Development
Reference bmad-framework-architecture.md + development-guide.md

---
*This documentation index serves as the primary entry point for AI-assisted development of the ScrapeCraft OSINT Platform.*