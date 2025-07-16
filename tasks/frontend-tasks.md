# Frontend Integration Sprint Tasks

## FE-001: Setup FastAPI Wrapper
Status: Not Started
Priority: High
Dependencies: None

Create thin API layer that wraps existing Monte Carlo functions without refactoring Python code.

**Acceptance Criteria**
- FastAPI app created in `api/app.py`
- CORS middleware configured for React frontend
- Existing Python functions imported and accessible
- API runs on localhost:8000

**Technical Notes**
- Add `sys.path.append('../src')` to import existing modules
- Use `from main import run_simulation` (or similar)
- Keep existing code 100% untouched
- Install: `pip install fastapi uvicorn`

---

## FE-002: Create Basic API Endpoints
Status: Not Started
Priority: High
Dependencies: FE-001

Expose core Monte Carlo functionality through REST endpoints.

**Acceptance Criteria**
- `GET /api/portfolio/default` - Returns default portfolio composition
- `POST /api/simulate` - Runs Monte Carlo simulation
- `GET /api/health` - Health check endpoint
- All endpoints return JSON responses

**Technical Notes**
- Wrap existing `get_portfolio()` function
- Wrap existing simulation logic from `main.py`
- Use Pydantic models for request/response validation
- Keep business logic in existing Python files

---

## FE-003: Setup React Application
Status: Not Started
Priority: High
Dependencies: None

Create modern React app with TypeScript and essential dependencies.

**Acceptance Criteria**
- React app created with Vite + TypeScript
- Essential dependencies installed (React Query, Recharts, Tailwind)
- Development server runs on localhost:3000
- Basic project structure established

**Technical Notes**
- Use `npm create vite@latest frontend -- --template react-ts`
- Install: `@tanstack/react-query`, `recharts`, `tailwindcss`
- Setup Tailwind CSS configuration
- Create folder structure: `components/`, `services/`, `types/`

---

## FE-004: Interactive Portfolio Builder - Your Portfolio First
Status: Not Started
Priority: High
Dependencies: FE-003

Create portfolio interface that starts with YOUR portfolio as default, with option to customize.

**Acceptance Criteria**
- Loads YOUR portfolio (BTC-EUR 60%, 5MVW.DE 13%, etc.) as default
- Users can modify weights and see real-time validation
- Users can swap out assets (change BTC-EUR to TSLA, etc.)
- Real-time validation: weights must sum to 100%
- "Reset to Default" button to restore your original portfolio

**Technical Notes**
- Create `PortfolioBuilder.tsx` component
- Load your portfolio from `/api/portfolio/default`
- Allow editing of tickers and weights
- Add/remove asset rows dynamically
- Include "Why this portfolio?" explanation section

---

## FE-005: Enhanced Portfolio Builder - Smart Customization
Status: Not Started
Priority: High
Dependencies: FE-004

Add intelligent features for portfolio customization while keeping your defaults prominent.

**Acceptance Criteria**
- Asset autocomplete when users want to swap assets
- Current price and basic info display for all assets
- Portfolio value calculation in real-time
- Visual weight allocation (pie chart or bars)
- "Compare to Original" mode showing differences from your portfolio

**Technical Notes**
- Integrate with Yahoo Finance API for asset search
- Add debounced search for performance
- Create visual portfolio composition display
- Show performance comparison vs your original portfolio
- Use localStorage for saving user modifications

---

## FE-006: Connect Portfolio Builder to Backend
Status: Not Started
Priority: High
Dependencies: FE-002, FE-005

Establish API communication for custom portfolio simulations.

**Acceptance Criteria**
- API service layer created (`services/api.ts`)
- React Query setup for data fetching
- Custom portfolio submissions to `/api/simulate` endpoint
- Loading states during portfolio validation and simulation
- Error handling for invalid tickers or API failures

**Technical Notes**
- Use `fetch()` or `axios` for HTTP requests
- Implement `useQuery` for data fetching
- Add ticker validation endpoint
- Handle network timeouts gracefully
- Store portfolio configurations in React state

---

## FE-007: Basic Simulation Results Display
Status: Not Started
Priority: High
Dependencies: FE-006

Show Monte Carlo results for custom portfolios in clean format.

**Acceptance Criteria**
- Display key metrics for user's custom portfolio
- Show portfolio performance (median, mean, best/worst case)
- Present results in clean, readable cards/tables
- Include percentage changes and absolute values
- Loading spinner during simulation

**Technical Notes**
- Create `SimulationResults.tsx` component
- Format numbers with proper decimal places
- Use cards or tables for metric display
- Add conditional styling for positive/negative returns
- Focus on core metrics, not all visualizations

---

## FE-008: Dynamic Scenario Analysis - Basic
Status: Not Started
Priority: High
Dependencies: FE-007

Add regime selection and comparison for custom portfolios.

**Acceptance Criteria**
- Dropdown for scenario selection (Historical, Fiat Debasement, Geopolitical Crisis)
- Results update when scenario changes
- Side-by-side comparison of scenarios
- Clear labeling of active scenario
- Show how same portfolio performs under different regimes

**Technical Notes**
- Create `RegimeSelector.tsx` component
- Update API to accept regime parameter for custom portfolios
- Implement state management for scenario switching
- Add loading states during scenario changes
- Cache results to avoid redundant API calls

---

## FE-009: Advanced Scenario Analysis (Optional)
Status: Not Started
Priority: Medium
Dependencies: FE-008

Add advanced scenario customization and parameter tweaking.

**Acceptance Criteria**
- Sliders for regime parameter adjustment (volatility multipliers, correlation shifts)
- Real-time simulation updates as users adjust parameters
- Custom scenario creation and saving
- Parameter sensitivity analysis
- "What-if" analysis tools

**Technical Notes**
- Create `AdvancedScenarioBuilder.tsx` component
- Add parameter validation and ranges
- Implement debounced API calls for real-time updates
- Add preset scenario templates
- Include parameter impact explanations

---

## FE-010: Basic Chart Visualization
Status: Not Started
Priority: Medium
Dependencies: FE-009

Add essential charts for portfolio simulation results.

**Acceptance Criteria**
- Line chart showing portfolio value over time
- Confidence intervals (50%, 80%, 90%) displayed
- Best/worst case scenarios highlighted
- Basic hover tooltips
- Clean, professional styling

**Technical Notes**
- Use Recharts `LineChart` component
- Implement multiple data series for confidence bands
- Add custom tooltips with formatted values
- Match color scheme from existing Python charts
- Keep visualization simple and focused

---

## FE-011: Polish & Responsive Design
Status: Not Started
Priority: Medium
Dependencies: FE-010

Ensure application works well on all devices and add professional polish.

**Acceptance Criteria**
- Responsive design works on mobile, tablet, desktop
- Professional typography and spacing
- Loading animations and micro-interactions
- Error states handled gracefully
- Focus on portfolio builder and scenario analysis UX

**Technical Notes**
- Use Tailwind responsive utilities
- Add CSS animations for smooth transitions
- Implement skeleton loading states
- Test portfolio builder on multiple device sizes
- Optimize for the core workflow (build portfolio → run scenarios)

---

## FE-012: Deployment & Documentation
Status: Not Started
Priority: Medium
Dependencies: FE-011

Deploy application and create user documentation.

**Acceptance Criteria**
- Frontend deployed to Vercel/Netlify
- Backend deployed to Railway/Render
- Environment variables configured
- User guide created with screenshots
- Technical documentation updated

**Technical Notes**
- Build production versions of both apps
- Configure environment variables for production
- Update README with deployment instructions
- Add screenshots of key features
- Include troubleshooting section

---

## Estimated Timeline: 8-10 days
- **Week 1**: Tasks FE-001 through FE-007 (Core portfolio builder + basic results)
- **Week 2**: Tasks FE-008 through FE-012 (Dynamic scenario analysis + polish)

## Focus Areas Based on Your Preferences:
1. **Interactive Portfolio Builder** (FE-004, FE-005) - 60% of development time
2. **Dynamic Scenario Analysis** (FE-008, FE-009) - 30% of development time  
3. **Basic visualizations** (FE-010) - 10% of development time

## Key Dependencies
- Existing Monte Carlo Python code (completed)
- FastAPI and React development environment
- Yahoo Finance API for asset data
- No database required - all data computed on-demand