# Expense Tracker with AI Financial Advice - Product Requirements Document (PRD)

## Overview

A mobile-friendly web application that helps users track their expenses and receive AI-powered financial advice, built for **Stori's Generative AI Squad technical challenge**.

**Timeline**: 4 days (Monday - Thursday)\
**Deployment**: AWS (EC2 + S3 + CloudFront) with GitHub repository\
**Tech Choices**: Includes **Supabase** (for PostgreSQL persistence) and **LangChain** (for modular AI orchestration).

---

## Core Features

### 1. Expense Summary Dashboard

**User Story**: As a user, I want to see a summary of my spending by category so I can understand where my money goes.

**Requirements**:

- Breakdown of spending by category (rent, groceries, dining, utilities, etc.)
- Show total amount + % of total spending
- Visualized with **Recharts** (pie or bar chart)
- Supports current month + year-to-date views
- Fully mobile responsive

**API Endpoint**: `GET /api/expenses/summary`

---

### 2. Income & Expense Timeline

**User Story**: As a user, I want to see a timeline of my income and expenses so I can track my financial flow over time.

**Requirements**:

- Interactive chart of income vs expenses over time
- Monthly aggregation with net income calculation
- Hover tooltips for details
- Optimized for touch/mobile interactions

**API Endpoint**: `GET /api/transactions/timeline`

---

### 3. AI Financial Advisor

**User Story**: As a user, I want to get personalized financial advice based on my spending patterns so I can improve my financial health.

**Requirements**:

- Input box for natural language questions
- **LangChain pipeline** calling OpenAI/Gemini with transaction context
- Contextual recommendations (e.g., “reduce dining expenses to save \$100/month”)
- Clear, actionable text responses

**API Endpoint**: `POST /api/ai/advice`

---

## Technology Stack

### Backend

- **Framework**: FastAPI (Python, async support, auto-docs)
- **Database**: Supabase (managed PostgreSQL)
- **Validation**: Pydantic models
- **AI Integration**: LangChain + OpenAI GPT-3.5/4
- **APIs**: RESTful, documented via FastAPI

### Frontend

- **Framework**: React.js + TypeScript (Vite for fast builds)
- **State Management**: React Query (data fetching & caching)
- **Styling**: Tailwind CSS + Shadcn UI
- **Charts**: Recharts

### Infrastructure

- **Containerization**: Docker + Docker Compose (local + prod)
- **Hosting**: AWS EC2 (Free Tier) for backend
- **Static Assets**: AWS S3 + CloudFront
- **Repository**: GitHub

### Development Tools

- **Package Managers**: bun/npm (frontend), uv/pip (backend)
- **Linters/Formatters**: ESLint, Prettier, Black
- **Testing**: Pytest, vitest, Playwright

---

## Data Model

### Transaction Entity

```python
class Transaction(BaseModel):
    id: str
    date: date
    amount: float
    category: str
    description: str
    type: Literal['income', 'expense']
```

### API Response Models

```python
class CategorySummary(BaseModel):
    category: str
    total_amount: float
    percentage: float
    transaction_count: int

class TimelinePoint(BaseModel):
    date: str
    income: float
    expenses: float
    net: float

class AIAdviceResponse(BaseModel):
    question: str
    advice: str
    context_used: str
```

---

## API Endpoints

### `GET /api/expenses/summary`

Returns aggregated spending by category.

### `GET /api/transactions/timeline`

Returns income vs expenses timeline.

### `POST /api/ai/advice`

Returns personalized advice using LangChain + OpenAI.

### `GET /api/health`

Health check endpoint.

---

## UI & Design

- **Mobile-first design** (320px, 768px, 1024px breakpoints)
- **Color scheme**: Dark mode by default, finance-inspired (Blue = trust, Green = income, Red = expenses)

