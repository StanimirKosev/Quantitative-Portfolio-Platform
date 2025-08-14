# Frontend Integration Sprint Tasks - Final 2025 Stack

> Note: Deployment tasks are consolidated in `tasks/backend-tasks.md` (Docker + GCP).

## FE-001: Setup FastAPI Wrapper

Status: Completed
Priority: High
Dependencies: None
Create thin API layer that wraps existing Monte Carlo functions without refactoring Python code.

**Acceptance Criteria**

- FastAPI app created in api/app.py
- CORS middleware configured for React frontend
- Existing Python functions imported and accessible
- API runs on localhost:8000

**Technical Notes**

- Add sys.path.append('../src') to import existing modules
- Use from main import run_simulation (or similar)
- Keep existing code 100% untouched
- Install: pip install fastapi uvicorn
- Test with browser at localhost:8000/docs

---

## FE-002: Complete API Implementation

Status: Completed
Priority: High
Dependencies: FE-001
Implement all 6 endpoints needed for full frontend interactivity with real-time updates.

**Acceptance Criteria**

### Portfolio Endpoints

- **GET /api/portfolio/default**  
  Returns the default portfolio as a list of assets, each with:

  - `ticker`
  - `weight_pct` (percentage, not decimal)
  - `description`
  - `start_date`, `end_date`: default date range for historical data visualization
    No unnecessary metadata; response is designed for direct frontend use.

- **POST /api/portfolio/validate**  
  Status: Implemented
  Validates a custom portfolio in real time.  
  Expects a JSON body with:
  - `tickers`: list of asset tickers
  - `weights`: list of asset weights (fractions, must sum to 1.0)
  - `start_date`: start date for historical data fetching (required)
  - `end_date`: end date for historical data fetching (required)
    Returns:
  - `{success: true, message: ...}` if valid
  - `{success: false, errors: [...]}` if invalid
    Covers both portfolio and single ticker validation (no need for separate ticker validation endpoints).

## Simulation Endpoints

- **POST /api/simulate/{regime}**  
  Runs a Monte Carlo simulation for the default portfolio under the specified regime (`historical`, `fiat_debasement`, `geopolitical_crisis`).  
  Uses the default date range for historical data fetching (see GET /api/portfolio/default).  
  Returns URLs for three generated charts:
  - `simulation_chart_path`
  - `correlation_matrix_chart_path`
  - `risk_factors_chart_path`
- **POST /api/simulate/custom**  
  Status: Implemented
  Runs a simulation for a custom portfolio and regime.  
  Accepts a JSON body with:
  - `tickers`: list of asset tickers
  - `weights`: list of asset weights (fractions, must sum to 1.0)
  - `regime`: scenario name (optional, defaults to 'historical')
  - `start_date`: (optional) start date for historical data fetching
  - `end_date`: (optional) end date for historical data fetching
    Returns URLs for three generated charts (same as default endpoint).  
    Core simulation/chart logic is reused from the default endpoint, but uses user-supplied portfolio data and date range.

## Regime Endpoints

- **GET /api/regimes**  
  Status: Implemented
  Lists available regimes, each with key, and name.

- **GET /api/regimes/{regime}/parameters**  
  Status: Implemented
  Returns regime parameter details for the given regime. The response structure is:

  ```
  {
    "regime": "<regime_name>",
    "parameters": [
      {"ticker": "BTC-EUR", "mean_factor": 1.3, "vol_factor": 1.1, "correlation_move_pct": -0.15},
      {"ticker": "4GLD.DE", "mean_factor": 1.15, "vol_factor": 1.05, "correlation_move_pct": -0.15},
      ...
    ],
    "description": "..."
  }
  ```

  Each object in `parameters` contains the asset ticker, mean_factor, vol_factor, and correlation_move_pct for that regime.

**Technical Notes**

- Use existing portfolio/regime logic from src/ modules
- Return both chart URLs and JSON data for interactive elements
- Handle custom regime parameters (mean_factor, vol_factor, correlation_move_pct)
- Support date range parameters: start_date, end_date for historical data fetching
- Include parameter defaults and validation ranges in API responses

---

## FE-003: Setup React Application with 2025 Stack

Status: Completed
Priority: High
Dependencies: None
Create modern React app with finalized library stack and project structure.

**Acceptance Criteria**

- React app created with Vite + TypeScript
- All chosen libraries installed and configured
- Development server runs on localhost:3000
- Clean project structure with proper folder organization
- shadcn/ui initialized with chart components

**Technical Notes**

- Use `npm create vite@latest frontend -- --template react-ts`
- Install core stack:
  ```bash
  npm install @tanstack/react-query zustand react-router-dom lodash
  ```
- Setup shadcn/ui with charts:
  ```bash
  npx shadcn-ui@latest init
  npx shadcn-ui@latest add chart
  ```
- Create folder structure:
  ```
  src/
  ├── components/     # Reusable UI components
  ├── stores/         # Zustand stores
  ├── types/          # TypeScript interfaces
  ├── hooks/          # Custom React hooks
  ```
- Configure TanStack Query client and React Router

---

## FE-004: Display Default Portfolio + Charts

Status: Completed
Priority: High
Dependencies: FE-002, FE-003
Create initial demo showing default portfolio and backend charts with regime switching.

**Acceptance Criteria**

- Display default portfolio composition
- Show 3 backend-generated chart images for selected regime
- Regime selector using shadcn/ui Select component
- Loading states with shadcn/ui skeleton components
- Error boundaries for graceful error handling

**Technical Notes**

- Create `PortfolioDisplay.tsx` using shadcn/ui Card components
- Use Zustand for regime state management

---

## FE-005: Add shadcn/ui Chart Visualizations

Status: Completed (with architectural changes)
Priority: Medium
Dependencies: FE-004
Enhanced experience with interactive shadcn/ui charts that complement backend analysis.

**ARCHITECTURAL CHANGE:** Implemented as carousel-based slides instead of separate chart components for better UX flow.

**Acceptance Criteria** ✅

- ✅ Portfolio allocation pie chart using shadcn/ui PieChart (PortfolioPieChart.tsx)
- ✅ Risk metrics dashboard with radar chart visualization (PortfolioRadarChart.tsx)
- ✅ Real-time updates when regime changes via TanStack Query
- ✅ Professional tooltips and smooth animations via Recharts
- ✅ Responsive carousel design that complements backend charts (ChartsSlides.tsx)
- ✅ Portfolio overview slide with key metrics (PortfolioOverviewSlide.tsx)

**Technical Notes**

- Create `PortfolioPieChart.tsx` using shadcn/ui chart components

- Use TanStack Query's background updates for smooth regime switching
- Use lodash for data transformations (groupBy, sortBy)
- Store chart preferences in Zustand
- Keep visualizations complementary to your backend charts

---

## FE-006: Add Custom Portfolio Input

Status: Completed
Priority: High
Dependencies: FE-005
Allow users to input their own portfolio using simple React forms.

**Acceptance Criteria**

- Portfolio input form using shadcn/ui form components
- Start with your default portfolio as template
- Real-time validation (weights sum to 100%, basic ticker format)
- "Reset to Default" button using shadcn/ui Button
- Form submission triggers new simulation via TanStack Query mutation
- Backend validation as single source of truth

**Technical Notes**

- Create `PortfolioForm.tsx` using normal React form (no React Hook Form)
- Use shadcn/ui Input and Button components
- Use TanStack Query mutations for form submission
- Store form state in Zustand for persistence across regime changes
- Let backend handle all real validation via `/api/portfolio/validate`

---

## FE-007: Custom Portfolio Results & Basic Routing

Status: Completed
Priority: High
Dependencies: FE-006
Display results for custom portfolios and add minimal routing structure.

**Acceptance Criteria**

- Generate and display 3 backend charts for user's custom portfolio
- Update shadcn/ui chart visualizations for custom portfolio data
- Clear indication of "Custom Portfolio" vs "Default Portfolio"
- Basic routing between main view and custom portfolio builder

**Technical Notes**

- Setup React Router with minimal routes
- Use TanStack Query's intelligent caching to avoid redundant API calls
- Use lodash for data manipulation and transformations
- Ensure UI scales well with different portfolio compositions

---

## FE-008: Advanced Regime Customization

Status: Completed
Priority: Medium  
Dependencies: FE-007
Two-tier regime system: predefined regimes for default portfolio, custom parameters for user portfolios.

**ARCHITECTURAL CHANGE:** Split regime handling into two approaches:

1. **Default Portfolio:** Toggle between predefined regimes (historical/fiat_debasement/geopolitical_crisis)
2. **Custom Portfolio:** Direct parameter input in form for maximum flexibility

**Acceptance Criteria** ✅

- ✅ Conditional regime rendering: RegimeSelector only shown for default portfolio
- ✅ Custom portfolio form includes regime parameter inputs (mean_factor, vol_factor, correlation_move_pct)
- ✅ Custom parameters applied to backend simulation and frontend charts
- ✅ Clear separation between predefined scenarios and user-defined parameters
- ✅ Custom radar chart reflects user's regime parameter choices

**Technical Notes** (Final Implementation)

- ✅ RegimeSelector.tsx conditionally rendered based on portfolio type
- ✅ CustomPortfolioForm.tsx includes regime parameter inputs for power users
- ✅ Backend API handles both predefined regimes and custom parameters
- ✅ Frontend charts (radar, pie) dynamically update based on custom parameters
- ✅ Predefined regimes showcase what's possible, custom parameters provide full control

---

## FE-009: Enhanced UX & Modern React Features

Status: Completed
Priority: Medium
Dependencies: FE-008
Added professional polish using modern React features and optimal performance.

**ARCHITECTURAL ENHANCEMENT:** Implemented carousel-based navigation with loading states and error boundaries.

**Acceptance Criteria** ✅

- ✅ Smooth transitions using React 18 and carousel animations
- ✅ Loading animations with custom LoadingBar component and progress indicators
- ✅ Responsive design across all device sizes with Tailwind CSS
- ✅ Error states with ErrorBoundary.tsx and ErrorPage.tsx components
- ✅ Optimized performance with React.memo, useMemo, and TanStack Query caching

**Technical Notes**

- Implement React 18 concurrent features
- Add CSS modules for professional mathematical styling
- Implement shadcn/ui skeleton components for loading states
- Optimize TanStack Query with proper stale times and background updates
- Use lodash for performance-critical data transformations

## FE-010: Implement Comprehensive Testing Suite

Status: Not Started
Priority: High
Dependencies: FE-009
Create testing coverage for frontend components, stores, and API integration.

**Acceptance Criteria**
- Unit tests for Zustand stores and utility functions
- Component tests for key UI components and charts  
- API integration tests with TanStack Query
- E2E tests for main user workflows
- Achieve >80% code coverage on critical paths

**Technical Notes**

### Dependencies
```bash
cd frontend
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event msw
```

### Tools
- **Vitest**: Testing framework with Vite integration
- **React Testing Library**: Component testing
- **MSW**: API mocking  
- **jsdom**: Browser environment simulation

### Setup
- Update vite.config.ts for test environment
- Create test setup files and API mocks
- Configure coverage reporting

---

## Final Tech Stack Summary

### **Core Libraries:**

- ✅ **Vite** - Lightning-fast build tool and dev server
- ✅ **TypeScript** - Type safety and better development experience
- ✅ **TanStack Query** - Server state management with intelligent caching
- ✅ **Zustand** - Lightweight client state management
- ✅ **React Router** - Simple routing (2 routes maximum)
- ✅ **shadcn/ui** - Professional components with built-in chart library
- ✅ **Lodash** - Utility functions for data manipulation

### **Architecture Decisions:**

- ✅ **No authentication** - Stateless demo application
- ✅ **No form libraries** - Simple native React forms (CustomPortfolioForm.tsx)
- ✅ **Tailwind CSS** - Professional styling with shadcn/ui components (changed from CSS Modules)
- ✅ **Backend validation** - Single source of truth for data validation via API
- ✅ **Hybrid visualization** - Backend charts + shadcn/ui interactive elements in carousel format
- ✅ **Modern React** - React 19, Error Boundaries, optimized performance
- ✅ **Carousel Navigation** - Embla carousel for smooth slide transitions between visualizations

### **Key Features:**

- ✅ **Portfolio showcase** - Default portfolio with detailed asset descriptions and weights
- ✅ **Custom portfolio analysis** - Full form validation and custom simulation support
- ✅ **Regime switching** - Toggle between 3 scenarios with real-time chart updates
- ✅ **Interactive carousel** - Multiple visualization slides (pie chart, radar chart, overview)
- ✅ **Backend chart integration** - Monte Carlo simulation and risk factor analysis charts
- ✅ **Professional styling** - Modern UI with Header navigation and responsive design
- ✅ **Performance optimized** - Zustand state management, TanStack Query caching, optimized re-renders
