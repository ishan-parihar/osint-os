# ScrapeCraft OSINT Platform - Development Guidelines

## Build / Lint / Test Commands

### Backend (FastAPI)
```bash
cd backend
python dev_server.py                    # Start dev server (port 8000)
python main.py                          # Production server
pytest -v --cov=app                     # Run tests with coverage
pytest -m unit                          # Run unit tests only
pytest -m integration                   # Run integration tests
pytest -m api                           # Run API endpoint tests
```

### Frontend (React/TypeScript)
```bash
cd frontend
npm start                               # Start dev server (port 4000)
npm run test:coverage                   # Run tests with coverage
npm run test:components                 # Test components only
npm run test:services                   # Test services only
npm run lint                            # ESLint check
npm run format                          # Prettier formatting
npm run type-check                      # TypeScript type checking
```

### Root Level Testing
```bash
pytest -v                               # Run all project tests
pytest tests/e2e/ -v                    # End-to-end tests
pytest tests/security/ -v               # Security tests
```

## Code Quality Tools

### Python (configured in pyproject.toml)
- **Formatting**: `black .` (line length 88, py311)
- **Linting**: `ruff check .` then `ruff format .`
- **Type Checking**: `mypy .` (strict mode, excludes tests/migrations)
- **Security**: `bandit -r .` (excludes tests/migrations)
- **Coverage**: pytest --cov=app --cov-fail-under=80

### TypeScript/React (configured in package.json)
- **Linting**: `npm run lint` (ESLint + TypeScript rules)
- **Formatting**: `npm run format` (Prettier)
- **Testing**: Jest with 80% coverage threshold
- **Type Checking**: `npm run type-check`

### Development Patterns
- Test files: `test_*.py`, `*_test.py`, `*.test.ts`, `*.spec.ts`
- Use pytest markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.api
- Frontend components: Functional with hooks, Zustand for state management
- Error handling: Structured logging, comprehensive try/catch, async/await patterns