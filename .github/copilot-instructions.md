# Stori Expense Tracker - AI Agent Instructions

## Project Overview

This is a **dual-agent system** for an expense tracker with AI financial advice. Read `PRD.md` and `Plan.md` first to understand the business requirements and development timeline, then follow agent-specific guidelines.

## Development Plan Adherence

- **Follow Plan.md**: Always reference the 4-day development plan for phase priorities and deliverables
- **Timeline awareness**: Check current phase and ensure deliverables align with plan milestones
- **Quality gates**: Verify completion criteria before moving to next phase
- **Risk mitigation**: Apply contingency plans when encountering blockers

## Architecture Pattern

- **Modular separation**: Backend (FastAPI/Python) + Frontend (React/TypeScript)
- **Agent-based development**: Each agent handles specific domain (see `AGENTS.md`)
- **Module structure**: Controllers → Services → Repositories (backend), Components → Hooks → Utils (frontend)
- **File size constraint**: ≤150 lines per file (target 100), split when exceeded

## Package Manager Requirements

- **Frontend**: Always use `bun` for package management (install, add, remove, run commands)
- **Backend**: Always use `uv` for Python package management and virtual environments
- **Never use**: npm, yarn, pip, or conda - stick to bun and uv exclusively

## Navigation Requirements

- **Strict folder navigation**: Always navigate to correct folder before executing any commands
- **Backend work**: `cd /Users/savg/Desktop/stori/backend` before any backend operations
- **Frontend work**: `cd /Users/savg/Desktop/stori/frontend` before any frontend operations
- **Root operations**: Only execute root-level commands from `/Users/savg/Desktop/stori/`

## Key Technical Decisions

### Backend (`backend/`)

- **Package manager**: Use `uv` exclusively for Python dependencies and virtual environments
- **Module pattern**: `src/modules/[ModuleName]/` with separated concerns
- **Required files per module**: `.controller.py`, `.service.py`, `.repository.py`, `.schemas.py`, `.test.py`
- **Auth integration**: Supabase Auth must be implemented from start, not retrofitted
- **API conventions**: `/api/expenses/summary`, `/api/transactions/timeline`, `/api/ai/advice`
- **AI pipeline**: LangChain + OpenAI for contextual financial advice
- **Navigation rule**: Always `cd /Users/savg/Desktop/stori/backend` before backend operations

### Frontend (`frontend/`)

- **Package manager**: Use `bun` exclusively for all Node.js operations (install, add, remove, run)
- **Component pattern**: `src/components/[FeatureName]/` with co-located types and tests
- **Required approach**: Dark mode by default, mobile-first (min 320px), strict TypeScript
- **State management**: React Query for API state, avoid complex global state
- **UI stack**: TailwindCSS + Shadcn UI components, Recharts for financial visualizations
- **Navigation rule**: Always `cd /Users/savg/Desktop/stori/frontend` before frontend operations

## Development Workflow

### Phase-Based Development

- **Current phase tracking**: Check Plan.md for current day/phase requirements
- **Deliverable completion**: Mark phase tasks as complete before moving forward
- **Quality verification**: Run all tests and linting before phase transitions

### Quality Gates

- **Backend**: Black linting, Pytest passing, FastAPI auto-docs generated
- **Frontend**: ESLint + Prettier, Vitest + Playwright tests, accessibility verified
- **Both**: Docker containerized, responsive design validated

### Command Execution Rules

- **Backend commands**: Must run from `/Users/savg/Desktop/stori/backend/`

  - Use `uv` for all Python package operations
  - Examples: `uv add fastapi`, `uv run python main.py`, `uv run pytest`

- **Frontend commands**: Must run from `/Users/savg/Desktop/stori/frontend/`

  - Use `bun` for all Node.js operations
  - Examples: `bun install`, `bun add react`, `bun dev`, `bun test`

- **Root commands**: Only run from `/Users/savg/Desktop/stori/` for:
  - Docker operations: `docker-compose up`
  - Git operations: `git add .`, `git commit`
  - Documentation updates

### Critical Data Models

```python
# Core transaction entity drives all features
class Transaction(BaseModel):
    type: Literal['income', 'expense']  # Affects all calculations
    category: str                       # Powers expense summary
    date: date                         # Drives timeline aggregation
```

### Integration Points

- **Supabase**: Single source of truth for auth + data persistence
- **AI Context**: Transaction data fed to LangChain for personalized advice
- **Charts**: Recharts expects specific data shape for timeline/summary views

## Agent Selection Rules

- **Backend tasks**: API endpoints, database operations, AI integration → Use `backend_agent.md`
- **Frontend tasks**: UI components, charts, responsive design → Use `frontend_agent.md`
- **Cross-cutting**: Read both agent files + `PRD.md` for full context

## Common Patterns

- **Error handling**: Clear user messages, proper HTTP status codes
- **Testing**: Unit tests for business logic, integration tests for user flows
- **Documentation**: Inline for complex logic, README for architectural decisions
