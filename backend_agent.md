# Backend Agent Instructions

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Validation**: Pydantic
- **AI Integration**: LangChain + OpenAI
- **Testing**: Pytest

## Rules
- Services ≤150 lines (target 100).
- Controllers, services, and repositories **must be separated**.
- Implement **Supabase Auth** from the start.
- Endpoints must use Pydantic schemas.
- Follow REST conventions:
  - `/api/expenses/summary`
  - `/api/transactions/timeline`
  - `/api/ai/advice`
  - `/api/health`
- Provide clear error handling & logging.

## File Structure
```
src/modules/[ModuleName]/
├── [ModuleName].controller.py
├── [ModuleName].service.py
├── [ModuleName].repository.py
├── [ModuleName].schemas.py
├── [ModuleName].test.py
```

## Quality Checklist
- [ ] Code linted (Black).  
- [ ] Tests passing (Pytest).  
- [ ] API documented via FastAPI auto-docs.  
- [ ] Supabase Auth configured.  
- [ ] Dockerized and working locally.  
