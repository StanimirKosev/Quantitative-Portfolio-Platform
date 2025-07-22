# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monte Carlo portfolio simulation platform with full-stack architecture: Python simulation engine + FastAPI + React frontend. Focuses on regime-dependent risk modeling with advanced financial mathematics (PCA, VaR, CVaR).

## Architecture

**Three-tier separation:**
- **Simulation Engine** (`src/`) - Core Monte Carlo with regime modeling
- **API Layer** (`api/`) - FastAPI wrapper with CORS
- **Frontend** (`frontend/src/`) - React dashboard with interactive charts

**Data flow:** Python fetches Yahoo Finance data → Monte Carlo simulation → FastAPI serves results → React displays visualizations

## Key Development Commands

**Backend (Python):**
```bash
# Install dependencies
pip install -r requirements.txt

# Run standalone simulation (generates charts/)
python src/main.py

# Run API server
cd api && uvicorn app:app --reload --port 8000
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

**Portfolio Configuration** (`src/portfolio.py`):
- Default 6-asset portfolio (60% BTC, 40% traditional assets)
- Regime definitions (Historical, Fiat Debasement, Geopolitical Crisis)
- Correlation and volatility factor adjustments per regime

**Simulation Engine** (`src/monte_carlo.py`):
- 1000 simulations, 252 trading days
- Multivariate normal sampling with regime-adjusted covariance matrices
- PCA/eigenvalue decomposition for risk factor analysis
- VaR/CVaR calculations at 95% and 99% levels

**API Endpoints** (`api/app.py`):
- `GET /api/portfolio/default` - Portfolio composition
- `POST /api/simulate/{regime}` - Default portfolio simulation
- `POST /api/simulate/custom` - Custom portfolio simulation
- `POST /api/portfolio/validate` - Portfolio validation
- `GET /api/regimes` - Available scenarios

**Frontend State Management:**
- **Zustand** (`src/store/`) - Client state for regime selection, custom portfolios
- **TanStack Query** - Server state management with caching for API calls

## Important Implementation Details

**Financial Mathematics:**
- Uses regime-dependent covariance matrices for scenario stress-testing
- PCA identifies dominant risk factors and explained variance
- Correlation matrix conditioning ensures numerical stability

**Data Sources:**
- Yahoo Finance API for real market data (yfinance library)
- No database - file-based storage for generated charts
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

Currently no formal test suite. Validation occurs through:
- Interactive testing via web interface
- Backend portfolio validation (weight sums, ticker validity)
- Monte Carlo simulation consistency checks

## Customization Points

**Adding new assets:** Modify `get_portfolio()` in `src/portfolio.py`
**New regimes:** Add to `REGIME_FACTORS` with mean/volatility adjustments
**Simulation parameters:** Adjust `num_simulations`, `initial_value` in `monte_carlo.py`
**Frontend components:** Follow shadcn/ui patterns with TypeScript interfaces