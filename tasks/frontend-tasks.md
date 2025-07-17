FE-001: Setup FastAPI Wrapper
Status: Completed
Priority: High
Dependencies: None
Create thin API layer that wraps existing Monte Carlo functions without refactoring Python code.
Acceptance Criteria

FastAPI app created in api/app.py
CORS middleware configured for React frontend
Existing Python functions imported and accessible
API runs on localhost:8000

Technical Notes

Add sys.path.append('../src') to import existing modules
Use from main import run_simulation (or similar)
Keep existing code 100% untouched
Install: pip install fastapi uvicorn
Test with browser at localhost:8000/docs


FE-002: Complete API Implementation
Status: Not Started
Priority: High
Dependencies: FE-001
Implement all 8 endpoints needed for full frontend interactivity with real-time updates.
Acceptance Criteria

## Portfolio Endpoints

- **GET /api/portfolio/default**  
  Returns the default portfolio as a list of assets, each with:
  - `ticker`
  - `weight_pct` (percentage, not decimal)
  - `description`
  No unnecessary metadata; response is designed for direct frontend use.

- **POST /api/portfolio/validate**  
  (To be implemented) Validates a custom portfolio in real time.

## Simulation Endpoints

- **POST /api/simulate/{regime}**  
  Runs a Monte Carlo simulation for the default portfolio under the specified regime (`historical`, `fiat_debasement`, `geopolitical_crisis`).  
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
    - `weights`: list of asset weights (percentages)
    - `regime`: scenario name (optional, defaults to 'historical')
  Returns URLs for three generated charts (same as default endpoint) and the regime name.  
  Core simulation/chart logic is reused from the default endpoint, but uses user-supplied portfolio data.

## Chart/Image Endpoints

## Regime Endpoints

- **GET /api/regimes**  
  (To be implemented) Lists available regimes.

- **GET /api/regimes/{regime}/parameters**  
  (To be implemented) Returns regime parameter details.

## Ticker Endpoints

- **GET /api/tickers/validate**  
  (To be implemented) Real-time portfolio validation.

- **GET /api/tickers/validate/{ticker}**  
  (To be implemented) Ticker validation for custom portfolios.


  Debounced real-time updates with loading states

Technical Notes

Use existing portfolio/regime logic from src/ modules
Return both chart URLs and JSON data for interactive elements
Implement proper validation ranges for custom regime parameters
Save charts with unique timestamp-based IDs
Include simulation metadata and risk metrics in all responses
Handle custom regime parameters (mean_factor, vol_factor, correlation_move_pct)
Support simulation parameters via query params: num_simulations (default: 1000), time_steps (default: 252), initial_value (default: 10000)
Support date range parameters: start_date, end_date for historical data fetching
Include parameter defaults and validation ranges in API responses


FE-003: Setup React Application
Status: Not Started
Priority: High
Dependencies: None
Create modern React app with all necessary dependencies for hybrid approach.
Acceptance Criteria

React app created with Vite + TypeScript
Essential dependencies installed and configured
Development server runs on localhost:3000
Basic project structure with proper folder organization
Tailwind CSS working with basic styling

Technical Notes

Use npm create vite@latest frontend -- --template react-ts
Install: @tanstack/react-query, recharts, tailwindcss, axios
Setup Tailwind CSS configuration
Create folders: components/, services/, types/, hooks/
Test with basic "Hello World" page


FE-004: Display Portfolio + Charts
Status: Not Started
Priority: High
Dependencies: FE-002, FE-003
Create initial demo showing default portfolio and backend charts with regime switching.
Acceptance Criteria

Display default portfolio composition (assets, weights, description)
Show 3 backend-generated charts for selected regime
Regime selector (dropdown/tabs) to switch between scenarios
Loading states during chart generation
Professional styling and responsive design
Include simulation metadata (dates, parameters)

Technical Notes

Create PortfolioDisplay.tsx for composition
Create ChartDisplay.tsx for backend images
Create RegimeSelector.tsx for scenario switching
Use React Query for API state management
Add error boundaries and loading skeletons
Style with Tailwind for professional appearance


FE-005: Add Complementary Recharts Visualizations
Status: Not Started
Priority: Medium
Dependencies: FE-004
Enhance the experience with interactive Recharts elements that complement backend charts.
Acceptance Criteria

Portfolio allocation pie chart with your asset breakdown
Interactive risk metrics dashboard (VaR/CVaR gauges or cards)
Real-time updates when regime changes
Hover tooltips and smooth animations
Responsive design that works with backend charts

Technical Notes

Research Recharts examples for best visualizations
Create PortfolioPieChart.tsx component
Create RiskMetricsDashboard.tsx component
Use data from backend simulation results
Implement smooth transitions between regimes
Keep complementary to backend charts, don't compete


FE-006: Add Custom Portfolio Input
Status: Not Started
Priority: High
Dependencies: FE-005
Allow users to input their own portfolio and see the same analysis applied to their choices.
Acceptance Criteria

Portfolio input form with ticker + weight fields
Start with default portfolio as template
Real-time validation (weights sum to 100%, valid tickers)
"Reset to Default" button to restore default portfolio
Form submission triggers new simulation
Error handling for invalid tickers or API failures

Technical Notes

Create PortfolioForm.tsx component
Add ticker validation (basic format checking)
Implement weight sum validation with visual feedback
API endpoints implemented in FE-002
Preserve form state across regime changes
Add loading states during custom simulations


FE-007: Custom Portfolio Results
Status: Not Started
Priority: High
Dependencies: FE-006
Acceptance Criteria

Generate and display 3 charts for user's custom portfolio
Update Recharts visualizations for custom portfolio
Maintain regime switching for custom portfolios
Clear indication of "Custom Portfolio" vs "Default Portfolio"

Technical Notes

Extend existing chart display for custom data
Update all Recharts components to use dynamic data
Cache simulation results to avoid redundant API calls
Ensure UI scales well with different portfolio compositions


FE-008: Advanced Regime Customization
Status: Not Started
Priority: Medium
Dependencies: FE-007
Allow power users to create custom regimes with parameter adjustments.
Acceptance Criteria

Parameter sliders for regime customization (volatility, correlation)
Real-time preview of regime impact on Recharts elements
Save/load custom regime configurations
"Custom Regime" mode with clear parameter explanations
Reset to standard regimes functionality

Technical Notes

Create CustomRegimeBuilder.tsx component
Add parameter sliders with validation ranges
Implement debounced updates for performance
Store custom regimes in localStorage
Add tooltips explaining parameter impacts
Custom regime API implemented in FE-002


FE-009: Enhanced UX & Polish
Status: Not Started
Priority: Medium
Dependencies: FE-008
Add professional polish, animations, and user experience improvements.
Acceptance Criteria

Smooth transitions between all states (default→custom→regimes)
Loading animations and skeleton states
Responsive design across all device sizes
Professional typography and spacing
Error states with helpful messaging
Export functionality for charts (optional)

Technical Notes

Add CSS animations with Tailwind
Implement skeleton loading components
Test responsive design thoroughly
Add micro-interactions for better UX
Include proper error boundaries
Optimize performance for smooth interactions


FE-010: Documentation & Deployment
Status: Not Started
Priority: Low
Dependencies: FE-009
Deploy application and create comprehensive documentation.
Acceptance Criteria

Frontend deployed to Vercel/Netlify
Backend deployed to Railway/Render/Heroku
Environment variables properly configured
README updated with complete setup instructions
User guide with screenshots and feature explanations
Architecture documentation

Technical Notes

Build production versions with environment configs
Set up CI/CD pipelines (optional)
Update repository README with deployment info
Create user documentation with screenshots
Include troubleshooting section
Document API endpoints and data flows

### General API Design Principle

- All API responses are designed with the frontend vision in mind:
  - Only include fields that are directly useful for the UI/UX.
  - All calculations and formatting are done in the backend.
  - Responses are minimal, clear, and ready for direct use by the frontend.