# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monte Carlo portfolio simulation platform with full-stack architecture: Python simulation engine + FastAPI + React frontend. Focuses on regime-dependent risk modeling with advanced financial mathematics (PCA, VaR, CVaR).

## Architecture

**Current Modular Monolith Structure:**

- **Backend** (`backend/`) - Organized monolith with modular architecture preparing for future expansion
  - `core/` - Shared utilities (logging, type validation, future shared components)
  - `simulation/` - Complete Monte Carlo engine with tests, API routes, and chart generation
  - `optimization/` - Future module for portfolio optimization (CVXPY, efficient frontiers)
  - `app.py` - Main FastAPI application with unified routing
- **Frontend** (`frontend/src/`) - TypeScript React dashboard with comprehensive validation and visualizations
- **Task Management** (`tasks/`) - Development roadmap with modular backend/frontend separation

**Data flow:** Python fetches Yahoo Finance data → Monte Carlo simulation → FastAPI serves results → React displays visualizations

**Future Architecture Vision** (documented in `docs/architecture.mermaid`):

- Monorepo with organized monolith backend
- Shared `core/` module for data fetching, covariance utilities, risk metrics
- Separate `simulation/` and `optimization/` modules
- Single FastAPI app with multiple routers

## Key Development Commands

**Backend (Python):**

```bash
# Install dependencies (from project root)
cd backend && pip install -r requirements.txt

# Run standalone simulation (generates backend/simulation/charts/)
cd backend && python -m simulation.main

# Run API server (from project root)
cd backend && uvicorn app:app --reload --port 8000
```

**Frontend (React/TypeScript):**

```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Dev server (port 5173)
npm run build        # Production build
npm run lint         # ESLint
npm run preview      # Preview production build
```

**Full development setup:** Run API server (port 8000) and frontend dev server (port 5173) simultaneously.

## Core Architecture Components

**Portfolio Configuration** (`backend/simulation/engine/portfolio.py`):

- Default 6-asset portfolio (60% BTC, 40% traditional assets)
- Regime definitions (Historical, Fiat Debasement, Geopolitical Crisis)
- Correlation and volatility factor adjustments per regime

**Simulation Engine** (`backend/simulation/engine/monte_carlo.py`):

- 1000 simulations, 252 trading days
- Multivariate normal sampling with regime-adjusted covariance matrices
- PCA/eigenvalue decomposition for risk factor analysis
- VaR/CVaR calculations at 95% and 99% levels

**API Endpoints** (`backend/app.py`):

- `GET /api/portfolio/default` - Portfolio composition
- `POST /api/simulate/{regime}` - Default portfolio simulation
- `POST /api/simulate/custom` - Custom portfolio simulation
- `POST /api/portfolio/validate` - Portfolio validation
- `GET /api/regimes` - Available scenarios

**Frontend State Management:**

- **Zustand** (`frontend/src/store/`) - Client state for regime selection, custom portfolios
- **TanStack Query** - Server state management with caching for API calls

## Important Implementation Details

**Financial Mathematics:**

- Uses regime-dependent covariance matrices for scenario stress-testing
- PCA identifies dominant risk factors and explained variance
- Correlation matrix conditioning ensures numerical stability

**Data Sources:**

- Yahoo Finance API for real market data (yfinance library)
- No database - file-based storage for generated charts in `backend/simulation/charts/`
- Asset tickers are European-listed (BTC-EUR, 5MVW.DE, etc.)

**Frontend Technology Stack:**

- React 19 with TypeScript, Vite build tool
- shadcn/ui components with Radix UI primitives
- Recharts for interactive visualizations
- Tailwind CSS for styling

**Error Handling:**

- Backend: Portfolio validation ensures weights sum to 1.0, valid tickers
- Frontend: React error boundaries, form validation with real-time feedback
- API: CORS configured for cross-origin requests

## Testing and Validation

**Test Framework:**

- Python: pytest with comprehensive test coverage in `backend/simulation/tests/`
- Unit tests for Monte Carlo engine, portfolio validation, API functions
- Integration tests for FastAPI endpoints
- Run tests: `cd backend && python -m pytest simulation/tests/`

**Validation:**

- Interactive testing via web interface
- Backend portfolio validation (weight sums, ticker validity)
- Monte Carlo simulation consistency checks

## Customization Points

**Adding new assets:** Modify `get_portfolio()` in `backend/simulation/engine/portfolio.py`
**New regimes:** Add to `REGIME_FACTORS` with mean/volatility adjustments
**Simulation parameters:** Adjust `num_simulations`, `initial_value` in `backend/simulation/engine/monte_carlo.py`
**Frontend components:** Follow shadcn/ui patterns with TypeScript interfaces

## Development Workflow

**Before starting any task:**

1. Read relevant task files in `tasks/` directory for current requirements
2. Check `docs/architecture.mermaid` for component relationships
3. Follow the architectural vision for future core module extraction

**Current Development Phase:**

- Monte Carlo simulation implementation (advanced phase)
- Preparing for core module extraction and PostgreSQL integration
- Next phase: Portfolio optimization engine with CVXPY

**Task Management:**

- Backend tasks: `tasks/simulation-backend.md`
- Frontend tasks: `tasks/simulation-frontend.md`
- Optimization planning: `tasks/optimization-backend.md` and `tasks/optimization-frontend.md`
