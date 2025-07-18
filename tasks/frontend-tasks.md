# Frontend Integration Sprint Tasks - Final 2025 Stack

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
  Regime name is echoed in the response.  
  No extra parameters unless needed for UX.
  
- **POST /api/simulate/custom**  
  Status: Implemented
  Runs a simulation for a custom portfolio and regime.  
  Accepts a JSON body with:
    - `tickers`: list of asset tickers
    - `weights`: list of asset weights (fractions, must sum to 1.0)
    - `regime`: scenario name (optional, defaults to 'historical')
    - `start_date`: (optional) start date for historical data fetching
    - `end_date`: (optional) end date for historical data fetching
  Returns URLs for three generated charts (same as default endpoint) and the regime name.  
  Core simulation/chart logic is reused from the default endpoint, but uses user-supplied portfolio data and date range.

## Regime Endpoints

- **GET /api/regimes**  
  Status: Implemented
  Lists available regimes, each with key, name, and description.

- **GET /api/regimes/{regime}/parameters**  
  Status: Implemented
  Returns regime parameter details for the given regime, including mean_factor, vol_factor, correlation_move_pct for each asset, and a description. The structure matches the backend regime definitions.

**Technical Notes**
- Use existing portfolio/regime logic from src/ modules
- Return both chart URLs and JSON data for interactive elements
- Handle custom regime parameters (mean_factor, vol_factor, correlation_move_pct)
- Support date range parameters: start_date, end_date for historical data fetching
- Include parameter defaults and validation ranges in API responses

---

## FE-003: Setup React Application with 2025 Stack
Status: Not Started
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
Status: Not Started
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
- Create `ChartDisplay.tsx` with React.lazy and Suspense:
  ```typescript
  const ChartDisplay = lazy(() => import('./ChartDisplay'))
  
  <Suspense fallback={<ChartSkeleton />}>
    <ChartDisplay />
  </Suspense>
  ```
- Create `RegimeSelector.tsx` using shadcn/ui Select
- Setup TanStack Query for intelligent caching:
  ```typescript
  const { data: portfolio } = useQuery({
    queryKey: ['portfolio', 'default'],
    queryFn: api.getDefaultPortfolio,
    staleTime: 10 * 60 * 1000 // Cache for 10 minutes
  })
  ```
- Use Zustand for regime state management

---

## FE-005: Add shadcn/ui Chart Visualizations
Status: Not Started
Priority: Medium
Dependencies: FE-004
Enhance experience with interactive shadcn/ui charts that complement your backend analysis.

**Acceptance Criteria**
- Portfolio allocation pie chart using shadcn/ui PieChart
- Risk metrics dashboard using shadcn/ui Cards and charts
- Real-time updates when regime changes via TanStack Query
- Professional tooltips and smooth animations
- Responsive design that complements backend charts

**Technical Notes**
- Create `PortfolioPieChart.tsx` using shadcn/ui chart components:
  ```typescript
  import { PieChart, Pie } from "recharts"
  import { ChartContainer, ChartTooltip } from "@/components/ui/chart"
  
  const portfolioData = useMemo(() => 
    portfolio?.assets.map(asset => ({
      asset: asset.ticker,
      value: asset.weight_pct,
      description: asset.description,
      fill: getAssetColor(asset.ticker)
    })), [portfolio]
  )
  
  <ChartContainer config={chartConfig} className="min-h-[300px]">
    <PieChart>
      <Pie data={portfolioData} dataKey="value" nameKey="asset" />
      <ChartTooltip />
    </PieChart>
  </ChartContainer>
  ```
- Use TanStack Query's background updates for smooth regime switching
- Use lodash for data transformations (groupBy, sortBy)
- Store chart preferences in Zustand
- Keep visualizations complementary to your backend charts

---

## FE-006: Add Custom Portfolio Input  
Status: Not Started
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
- Create `PortfolioForm.tsx` using normal React form (no React Hook Form):
  ```typescript
  const [customPortfolio, setCustomPortfolio] = useState({
    tickers: ['BTC-EUR', 'SPYL.DE', '5MVW.DE', 'WMIN.DE', 'IS3N.DE', '4GLD.DE'],
    weights: [0.6, 0.105, 0.13, 0.07, 0.06, 0.035]
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Basic client-side validation for UX
    const weightSum = customPortfolio.weights.reduce((a, b) => a + b, 0)
    if (Math.abs(weightSum - 1.0) > 0.001) {
      setError('Weights must sum to 100%')
      return
    }
    
    // Backend handles real validation
    simulateCustomPortfolio.mutate(customPortfolio)
  }
  ```
- Use shadcn/ui Input and Button components
- Use TanStack Query mutations for form submission
- Store form state in Zustand for persistence across regime changes
- Let backend handle all real validation via `/api/portfolio/validate`

---

## FE-007: Custom Portfolio Results & Basic Routing
Status: Not Started  
Priority: High
Dependencies: FE-006
Display results for custom portfolios and add minimal routing structure.

**Acceptance Criteria**
- Generate and display 3 backend charts for user's custom portfolio
- Update shadcn/ui chart visualizations for custom portfolio data
- Maintain regime switching for custom portfolios
- Clear indication of "Custom Portfolio" vs "Default Portfolio"
- Basic routing between main view and custom portfolio builder

**Technical Notes**
- Setup React Router with minimal routes:
  ```typescript
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<PortfolioAnalysis />} />
      <Route path="/custom" element={<CustomPortfolioBuilder />} />
    </Routes>
  </BrowserRouter>
  ```
- Extend existing chart display for custom data
- Update all shadcn/ui chart components to use dynamic data from Zustand:
  ```typescript
  const { customPortfolio, isCustomMode } = usePortfolioStore()
  const portfolioData = isCustomMode ? customPortfolio : defaultPortfolio
  ```
- Use TanStack Query's intelligent caching to avoid redundant API calls
- Use lodash for data manipulation and transformations
- Ensure UI scales well with different portfolio compositions

---

## FE-008: Advanced Regime Customization
Status: Not Started
Priority: Medium  
Dependencies: FE-007
Allow power users to create custom regimes with parameter adjustments.

**Acceptance Criteria**
- Parameter sliders using shadcn/ui Slider components
- Real-time preview of regime impact on shadcn/ui charts
- Save/load custom regime configurations using localStorage
- "Custom Regime" mode with clear parameter explanations
- Reset to standard regimes functionality

**Technical Notes**
- Create `CustomRegimeBuilder.tsx` using shadcn/ui components
- Add parameter sliders with validation ranges from `/api/regimes/{regime}/parameters`
- Implement debounced updates using lodash.debounce:
  ```typescript
  const debouncedUpdateRegime = useMemo(
    () => debounce((params: RegimeParams) => {
      updateRegimeParams(params)
    }, 300),
    []
  )
  ```
- Store custom regimes in Zustand with localStorage persistence:
  ```typescript
  const useRegimeStore = create<RegimeStore>((set) => ({
    customRegimes: JSON.parse(localStorage.getItem('customRegimes') || '[]'),
    saveCustomRegime: (regime) => {
      set((state) => {
        const updated = [...state.customRegimes, regime]
        localStorage.setItem('customRegimes', JSON.stringify(updated))
        return { customRegimes: updated }
      })
    }
  }))
  ```
- Add shadcn/ui Tooltips explaining parameter impacts
- Use TanStack Query mutations for custom regime simulations

---

## FE-009: Enhanced UX & Modern React Features
Status: Not Started
Priority: Medium
Dependencies: FE-008
Add professional polish using modern React features and optimal performance.

**Acceptance Criteria**
- Smooth transitions using React 18 concurrent features
- Loading animations with shadcn/ui skeletons and React Suspense
- Responsive design across all device sizes
- Error states with helpful messaging using Error Boundaries
- Optimized performance with React.memo and useMemo

**Technical Notes**
- Implement React 18 concurrent features:
  ```typescript
  // Lazy loading with Suspense
  const ChartDisplay = lazy(() => import('./ChartDisplay'))
  
  <Suspense fallback={<ChartSkeleton />}>
    <ChartDisplay />
  </Suspense>
  
  // Error boundaries for graceful error handling
  <ErrorBoundary fallback={<ChartError />}>
    <SimulationResults />
  </ErrorBoundary>
  ```
- Use React.memo for expensive chart components:
  ```typescript
  const PortfolioPieChart = memo(({ data }: { data: PortfolioData }) => {
    const chartData = useMemo(() => 
      data.assets.map(asset => ({
        ...asset,
        formattedWeight: `${asset.weight_pct.toFixed(1)}%`
      })), [data]
    )
    return <PieChart data={chartData} />
  })
  ```
- Add CSS modules for professional mathematical styling
- Implement shadcn/ui skeleton components for loading states
- Optimize TanStack Query with proper stale times and background updates
- Use lodash for performance-critical data transformations

---

## FE-010: Deployment & Documentation
Status: Not Started
Priority: Low
Dependencies: FE-009
Deploy application and create comprehensive documentation.

**Acceptance Criteria**
- Frontend deployed to Vercel (optimal for Vite + React)
- Backend deployed to Railway/Render
- Environment variables properly configured
- Updated README with complete tech stack explanation
- User guide with screenshots and feature explanations
- Architecture documentation showing library integrations

**Technical Notes**
- Build production versions with TypeScript compilation
- Configure environment variables for production API endpoints
- Setup Vercel deployment with proper build settings for Vite
- Update repository README with:
  - **Tech Stack**: Vite, TypeScript, TanStack Query, Zustand, React Router, shadcn/ui, Lodash
  - **Architecture**: Component relationships, state management flow
  - **API Integration**: How frontend connects to FastAPI backend
  - **Chart Strategy**: Backend-generated charts + shadcn/ui interactive elements
- Create user documentation with screenshots of:
  - Your default portfolio analysis
  - Custom portfolio creation
  - Regime switching functionality  
  - Interactive shadcn/ui chart features
- Include troubleshooting section and performance optimization notes

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
- ✅ **No form libraries** - Simple native React forms
- ✅ **CSS Modules** - Scoped styling for mathematical aesthetics
- ✅ **Backend validation** - Single source of truth for data validation
- ✅ **Hybrid visualization** - Backend charts + shadcn/ui interactive elements
- ✅ **Modern React** - Concurrent features, Suspense, Error Boundaries

### **Key Features:**
- ✅ **Your portfolio showcase** - Default portfolio demonstrates your investment thesis
- ✅ **Custom portfolio analysis** - Users can input their own allocations
- ✅ **Regime switching** - Compare scenarios (historical, fiat debasement, geopolitical)
- ✅ **Interactive charts** - shadcn/ui pie charts and risk dashboards
- ✅ **Professional styling** - Clean, mathematical interface design
- ✅ **Performance optimized** - Intelligent caching and React optimizations