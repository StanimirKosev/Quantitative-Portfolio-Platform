# Optimization Backend Tasks

**OPT-001: Migration to Poetry and Dependency Management**
Status: Completed
Priority: High
Dependencies: MC-019

Migrate from pip/requirements.txt to Poetry for better dependency management
Add optimization-specific dependencies for mathematical programming and numerics
Prepare clean dependency structure for both simulation and optimization modules

Acceptance Criteria

- Create `pyproject.toml` with Poetry configuration
- Migrate existing dependencies to Poetry format
- Add optimization dependencies: CVXPY, SQLAlchemy, psycopg2-binary, scikit-learn (shrinkage)
- Maintain development/production dependency separation
- All existing functionality works with Poetry-managed dependencies

Technical Notes

- Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Initialize: `poetry init` and migrate from requirements.txt
- Key new deps: `poetry add cvxpy sqlalchemy psycopg2-binary alembic`
- Dev deps: `poetry add --group dev pytest pytest-cov black isort`
- Virtual env: `poetry shell` and `poetry install`

**OPT-002: Basic CVXPY Optimization Engine**
Status: Completed
Priority: High
Dependencies: OPT-001

Implement core portfolio optimization using CVXPY
Start with basic mean-variance optimization (Markowitz model)
Create foundation for efficient frontier calculations

Acceptance Criteria

- Minimize risk optimization: given target return, find minimum variance portfolio
- Maximize Sharpe ratio optimization: find optimal risk-adjusted return
- Basic constraint handling: long-only, budget constraint (weights sum to 1)
- Return optimal weights and portfolio metrics (expected return, volatility, Sharpe)
- Solver controls: time limit, fallback solver, clear infeasibility messages
- Use shrinkage covariance from core by default

Technical Notes

- Use CVXPY for quadratic programming: `cp.Minimize(cp.quad_form(w, cov_matrix))`
- Variables: weights `w = cp.Variable(n_assets)`
- Constraints: `cp.sum(w) == 1`, `w >= 0` for long-only
- Objective functions: minimize variance or maximize return/risk ratio
- Solver selection: OSQP or ECOS for quadratic problems

**OPT-003: Efficient Frontier Calculation**
Status: Completed
Priority: High
Dependencies: OPT-002

Implement efficient frontier calculation across risk-return spectrum
Generate multiple optimal portfolios for different target returns
Prepare data structure for frontend visualization

Acceptance Criteria

- Calculate 20-30 optimal portfolios across return range
- Each point: target return, minimum risk, optimal weights
- Return structured data for efficient frontier plotting
- Handle edge cases: infeasible targets (skip/mark), numerical issues (retry/fallback)

Technical Notes

- Iterate over target returns: `np.linspace(min_return, max_return, 25)`
- For each target: solve minimum variance optimization
- Store results: `{"return": target, "risk": sqrt(variance), "weights": optimal_w}`
- Find max Sharpe ratio: `max((r - rf) / vol)` across frontier points
- Validate feasibility before solving each optimization

**OPT-004: FRED API Integration for Risk-Free Rates**
Status: Completed
Priority: High
Dependencies: None (core module enhancement)

Replace hardcoded risk-free rates with real-time data from Federal Reserve Economic Data (FRED) API.
Integrate authoritative risk-free rate sourcing for Sharpe ratio and optimization calculations.
Add caching and fallback mechanisms for production reliability.

Acceptance Criteria

- Add `fredapi` dependency to Poetry configuration
- Implement `fetch_risk_free_rate()` function in `core/utils.py`
- Fetch 3-month Treasury bill rate (DGS3MO) or 10-year Treasury (DGS10) from FRED
- Implement 24-hour caching to avoid API rate limits and ensure performance
- Add fallback to reasonable default rate (2-3%) if API fails
- Log data source usage (cached vs fresh API call)
- Update Sharpe ratio calculations across optimization engine to use dynamic rate
- Add configuration for FRED API key via environment variables

Technical Notes

- Install: `poetry add fredapi`
- FRED series: DGS3MO (3-month Treasury) or DGS10 (10-year Treasury)
- API usage: `fred = Fred(api_key='KEY'); rate = fred.get_series_latest_release('DGS3MO')`
- Cache implementation: in-memory with 24h TTL or simple file-based cache
- Fallback rate: 2.5% (reasonable default for current economic environment)
- Environment variable: `FRED_API_KEY` for production deployment
- Convert percentage rate to decimal for calculations (divide by 100)
- Integration points: optimization Sharpe ratio calculations, efficient frontier metrics

## Remaining Tasks

**OPT-005: FastAPI Optimization Router**
Status: Not Started
Priority: High
Dependencies: OPT-003

Create FastAPI router for optimization endpoints
Integrate with existing simulation API structure
Add basic portfolio optimization endpoints

Acceptance Criteria

- `/api/optimize/portfolio` endpoint for single portfolio optimization
- `/api/optimize/efficient-frontier` endpoint for frontier calculation (async)
- Request/response models using Pydantic (shared with simulation via core/models)
- Error handling for optimization failures with meaningful messages
- Integration with existing FastAPI app structure

Technical Notes

- Create `optimization/router.py` similar to simulation structure
- Use async endpoints for potentially long-running optimizations
- Request models: portfolio data + optimization parameters
- Response models: optimal weights, metrics, efficient frontier data
- Include optimization in main FastAPI app: `app.include_router(opt_router)`

**OPT-006: Efficient Frontier Visualization Backend Support**
Status: Not Started
Priority: High
Dependencies: OPT-005

Create backend visualization utilities for efficient frontier plotting, similar to simulation's chart generation.
Generate matplotlib-based efficient frontier plots with max Sharpe ratio highlighting for backend testing
and optional frontend integration.

Acceptance Criteria

- Create `optimization/engine/visualization.py` module following simulation patterns
- Implement `plot_efficient_frontier()` function generating risk-return scatter plot
- Highlight maximum Sharpe ratio portfolio with distinct marker/color
- Save plots to `optimization/charts/` directory with consistent naming
- Include portfolio weights visualization (pie chart) for selected point
- Return chart paths for potential API serving (following simulation structure)
- Handle edge cases: empty frontier, single point, visualization failures

Technical Notes

- Follow simulation visualization patterns from `simulation/engine/visualization.py`
- Use matplotlib for scatter plot: X-axis=volatility, Y-axis=returns
- Efficient frontier as connected line/curve with individual points
- Max Sharpe portfolio as starred/highlighted point with legend
- Save charts: `optimization/charts/efficient_frontier_{timestamp}.png`
- Optional: Interactive hover showing portfolio weights for each point
- Consistent styling with simulation charts (colors, fonts, layout)

**OPT-007: Real-time WebSocket Progress Updates**
Status: Not Started
Priority: Medium
Dependencies: OPT-005

Implement WebSocket-based real-time progress updates for efficient frontier calculations.
This is the primary WebSocket use case for the entire project, providing live feedback
during long-running optimization processes (20-40 seconds).

Acceptance Criteria

- Add progress callback parameter to `calculate_efficient_frontier()` function
- Create WebSocket endpoint `/ws/optimize/progress/{session_id}` for real-time updates
- Emit progress events: `{"current": 15, "total": 25, "message": "Calculating portfolio 15/25"}`
- Frontend receives real-time updates and displays progress bar
- Handle WebSocket connection cleanup on completion or error
- Session-based progress tracking for multiple concurrent optimizations

Technical Notes

- Modify efficient frontier loop to call `progress_callback(current, total)`
- Use FastAPI WebSocket with unique session IDs
- Frontend connects to WebSocket before starting optimization
- Progress updates every 1-2 seconds as each portfolio point completes
- Graceful fallback if WebSocket connection failsW

**OPT-008: Production Infrastructure**
Status: Not Started  
Priority: Low
Dependencies: OPT-007

Production-ready deployment enhancements including CI/CD and Docker optimizations.

Acceptance Criteria

- CI/CD pipeline with GitHub Actions (build, test, deploy)
- Docker multi-stage builds (smaller production images, faster builds)
- Enhanced logging for optimization performance monitoring
- Environment-based configuration (dev/prod settings)

Technical Notes

- Multi-stage Docker: separate build stage for Poetry dependencies, lean runtime stage
- CI/CD: automated testing, Docker image builds, deployment to cloud platforms
- Logging: optimization timing, solver performance, error tracking
- Config: environment variables for FRED API, optimization parameters

## Ideas for Advanced Features (Future Considerations)

**Advanced Financial Metrics** (Core Module):

- CAPM Beta calculation against market indices
- Information Ratio for active return vs tracking error
- Stress testing with historical crisis scenarios (2008, COVID)

**UI/UX Enhancements** (Frontend):

- Interactive efficient frontier charts with hover details
- Portfolio comparison tools (side-by-side optimization results)
- Advanced constraint builder interface (sector limits, position sizes)
