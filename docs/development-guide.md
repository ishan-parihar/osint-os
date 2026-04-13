# ScrapeCraft Development Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Node.js**: 18.x or higher
- **Python**: 3.12 or higher
- **Git**: 2.30 or higher

### Development Tools
- **IDE**: VS Code (recommended) with extensions:
  - Python
  - TypeScript and JavaScript
  - Docker
  - GitLens
  - Thunder Client (for API testing)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/scrapecraft.git
cd scrapecraft
```

### 2. Backend Setup

#### Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scrapecraft
REDIS_URL=redis://localhost:6379/0

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key

# External Services
OLLAMA_BASE_URL=http://localhost:11434
```

#### Database Setup
```bash
# Install PostgreSQL (if not using Docker)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb scrapecraft

# Run migrations
alembic upgrade head

# Create initial user (optional)
python -m app.scripts.create_admin
```

### 3. Frontend Setup

#### Node.js Environment
```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
```

**Frontend Environment Variables (.env.local):**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_ENVIRONMENT=development
```

### 4. Docker Development Setup

```bash
# Start development services
docker-compose up -d db redis ollama

# Verify services are running
docker-compose ps
```

## Local Development Commands

### Backend Development

#### Start Development Server
```bash
cd backend
source venv/bin/activate  # if not already activated

# Start FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Alternative: Use the dev_server.py script
python dev_server.py
```

#### Code Quality and Formatting
```bash
# Format code
black .

# Lint code
ruff check .

# Sort imports
isort .

# Type checking
mypy .

# Security check
bandit -r app/

# Dependency check
safety check
```

#### Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

#### Testing
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_specific.py -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test method
pytest tests/test_specific.py::test_method -v
```

### Frontend Development

#### Start Development Server
```bash
cd frontend

# Start React development server
npm start

# The app will open at http://localhost:3000
```

#### Code Quality and Testing
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- --testPathPattern=specific.test

# Build for production
npm run build

# Type checking
npx tsc --noEmit

# Linting
npm run lint

# Format code
npm run format
```

### Full Stack Development

#### Start All Services
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Docker services (if not already running)
docker-compose up db redis ollama
```

## Common Development Tasks

### Adding New API Endpoints

1. **Create Pydantic Models** (app/models/schemas/)
```python
from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
```

2. **Create Database Models** (app/models/sqlalchemy/)
```python
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
```

3. **Create API Routes** (app/api/)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # Implementation here
    pass
```

### Adding New Frontend Components

1. **Create Component** (src/components/)
```typescript
import React from 'react';

interface ItemProps {
  name: string;
  description?: string;
}

const Item: React.FC<ItemProps> = ({ name, description }) => {
  return (
    <div className="item">
      <h3>{name}</h3>
      {description && <p>{description}</p>}
    </div>
  );
};

export default Item;
```

2. **Add Styling** (with Tailwind CSS)
```typescript
const Item: React.FC<ItemProps> = ({ name, description }) => {
  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold">{name}</h3>
      {description && (
        <p className="text-gray-600 mt-2">{description}</p>
      )}
    </div>
  );
};
```

### Database Schema Changes

1. **Create Migration**
```bash
cd backend
alembic revision --autogenerate -m "Add user_preferences table"
```

2. **Review and Edit Migration**
Edit the generated migration file in `alembic/versions/`

3. **Apply Migration**
```bash
alembic upgrade head
```

### Adding New LLM Providers

1. **Create Provider Class** (app/llm/providers/)
```python
from app.llm.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_response(self, prompt: str) -> str:
        # Implementation here
        pass
```

2. **Register Provider** (app/llm/factory.py)
```python
from app.llm.providers.custom import CustomProvider

LLM_PROVIDERS = {
    "openai": OpenAIProvider,
    "custom": CustomProvider,
    # ... other providers
}
```

## Testing Strategy

### Backend Testing

#### Unit Tests
```python
# tests/test_models.py
import pytest
from app.models.sqlalchemy.user import User

def test_user_creation():
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
```

#### Integration Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

### Frontend Testing

#### Component Tests
```typescript
// src/components/__tests__/Item.test.tsx
import { render, screen } from '@testing-library/react';
import Item from '../Item';

test('renders item name', () => {
  render(<Item name="Test Item" />);
  expect(screen.getByText('Test Item')).toBeInTheDocument();
});
```

#### Integration Tests
```typescript
// src/__tests__/App.integration.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

test('creates new item', async () => {
  render(<App />);
  
  fireEvent.change(screen.getByLabelText('Name'), {
    target: { value: 'Test Item' }
  });
  
  fireEvent.click(screen.getByText('Create'));
  
  expect(await screen.findByText('Test Item')).toBeInTheDocument();
});
```

## Debugging

### Backend Debugging

#### Using pdb
```python
import pdb; pdb.set_trace()

# Or with ipdb (if installed)
import ipdb; ipdb.set_trace()
```

#### Logging Configuration
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
```

### Frontend Debugging

#### Browser DevTools
- Use React DevTools for component inspection
- Use Redux DevTools for state management debugging
- Use Network tab for API call debugging

#### VS Code Debugging
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Backend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/dev_server.py",
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Frontend",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["start"]
    }
  ]
}
```

## Performance Optimization

### Backend Optimization

1. **Database Query Optimization**
```python
# Use selectinload for relationships
from sqlalchemy.orm import selectinload

users = session.query(User).options(
    selectinload(User.items)
).all()
```

2. **Caching with Redis**
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@cache.memoize(timeout=300)
def expensive_operation(param: str):
    # Expensive computation
    pass
```

### Frontend Optimization

1. **Code Splitting**
```typescript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

2. **React.memo for Performance**
```typescript
import React from 'react';

const ExpensiveComponent = React.memo(({ data }) => {
  // Component implementation
});
```

## Troubleshooting

### Common Issues

#### Backend Issues
- **Database Connection**: Check DATABASE_URL in .env
- **Migration Failures**: Drop and recreate database, then re-run migrations
- **Import Errors**: Check virtual environment activation

#### Frontend Issues
- **Module Not Found**: Run `npm install`
- **TypeScript Errors**: Check tsconfig.json configuration
- **API Connection**: Verify REACT_APP_API_URL in .env.local

#### Docker Issues
- **Port Conflicts**: Check if ports are already in use
- **Container Failures**: Check logs with `docker-compose logs [service]`
- **Volume Issues**: Clear Docker volumes if needed

### Getting Help

1. **Check Logs**
   - Backend: Check terminal output or log files
   - Frontend: Check browser console
   - Docker: `docker-compose logs`

2. **Community Resources**
   - GitHub Issues
   - Documentation
   - Stack Overflow

3. **Development Team**
   - Create detailed bug reports
   - Include error messages and reproduction steps
   - Provide environment details

---

This guide provides a comprehensive foundation for ScrapeCraft development. For specific feature development, refer to the relevant architecture documents and API documentation.