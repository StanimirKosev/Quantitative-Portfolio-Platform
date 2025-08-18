OPT-001: Migration to Poetry and Dependency Management
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

OPT-002: PostgreSQL Database Schema Design
Status: Not Started
Priority: High
Dependencies: OPT-001

Design and implement PostgreSQL database schema for portfolio optimization
Create SQLAlchemy models for portfolios, optimizations, and market data
Set up database connection and migration system

Acceptance Criteria

- SQLAlchemy models for: Portfolio, PortfolioAsset, Optimization, PriceData tables
- Database connection configuration with environment variables
- Alembic migrations for schema versioning
- Portfolio table: id, name, constraints (JSON), created_at
- PortfolioAsset table: portfolio_id (FK), ticker, weight (indexable, numeric)
- Optimization table: id, portfolio_id, objective, params_json, results_json, duration_ms, created_at
- PriceData: composite PK (ticker, date), indexes for lookups
- Local PostgreSQL development setup documented

Technical Notes

- Use SQLAlchemy 2.0 syntax with async support
- JSON columns for flexible portfolio configurations
- Foreign key relationships between tables
- Connection string: `postgresql://user:pass@localhost/portfolio_db`
- Alembic for migrations: `alembic init` and `alembic revision --autogenerate`

OPT-003: Basic CVXPY Optimization Engine
Status: Not Started
Priority: High
Dependencies: OPT-002

Implement core portfolio optimization using CVXPY
Start with basic mean-variance optimization (Markowitz model)
Create foundation for efficient frontier calculations

Acceptance Criteria

- Minimize risk optimization: given target return, find minimum variance portfolio
- Maximize Sharpe ratio optimization: find optimal risk-adjusted return
- Basic constraint handling: long-only, budget constraint (weights sum to 1), bounds per asset
- Return optimal weights and portfolio metrics (expected return, volatility, Sharpe)
- Solver controls: time limit, fallback solver, clear infeasibility messages
- Use shrinkage covariance from core by default

Technical Notes

- Use CVXPY for quadratic programming: `cp.Minimize(cp.quad_form(w, cov_matrix))`
- Variables: weights `w = cp.Variable(n_assets)`
- Constraints: `cp.sum(w) == 1`, `w >= 0` for long-only
- Objective functions: minimize variance or maximize return/risk ratio
- Solver selection: OSQP or ECOS for quadratic problems

OPT-004: Efficient Frontier Calculation
Status: Not Started
Priority: High
Dependencies: OPT-003

Implement efficient frontier calculation across risk-return spectrum
Generate multiple optimal portfolios for different target returns
Prepare data structure for frontend visualization

Acceptance Criteria

- Calculate 20-30 optimal portfolios across return range
- Each point: target return, minimum risk, optimal weights
- Identify portfolio with maximum Sharpe ratio on frontier
- Return structured data for efficient frontier plotting
- Emit progress events (step/total, best Sharpe so far) to a WS topic
- Handle edge cases: infeasible targets (skip/mark), numerical issues (retry/fallback)

Technical Notes

- Iterate over target returns: `np.linspace(min_return, max_return, 25)`
- For each target: solve minimum variance optimization
- Store results: `{"return": target, "risk": sqrt(variance), "weights": optimal_w}`
- Find max Sharpe ratio: `max((r - rf) / vol)` across frontier points
- Validate feasibility before solving each optimization

OPT-005: FastAPI Optimization Router
Status: Not Started
Priority: Medium
Dependencies: OPT-004

Create FastAPI router for optimization endpoints
Integrate with existing simulation API structure
Add basic portfolio optimization endpoints

Acceptance Criteria

- `/api/optimize/portfolio` endpoint for single portfolio optimization
- `/api/optimize/efficient-frontier` endpoint for frontier calculation (async)
- WebSocket `/ws/optimize/progress/{run_id}` for real-time updates
- Request/response models using Pydantic (shared with simulation via core/models)
- Error handling for optimization failures with meaningful messages
- Integration with existing FastAPI app structure

Technical Notes

- Create `optimization/router.py` similar to simulation structure
- Use async endpoints for potentially long-running optimizations
- Request models: portfolio data + optimization parameters
- Response models: optimal weights, metrics, efficient frontier data
- Include optimization in main FastAPI app: `app.include_router(opt_router)`

OPT-006: Portfolio Risk Attribution Foundation
Status: Not Started
Priority: Low
Dependencies: OPT-005

Create foundation for portfolio risk attribution analysis
Implement factor-based risk decomposition using core module components
Prepare for advanced constraint handling in optimization

Acceptance Criteria

- Calculate portfolio risk contribution by asset
- Implement marginal contribution to risk (MCTR) calculations
- Factor-based risk attribution using PCA from core module
- Foundation for sector/factor-based optimization constraints
- Risk attribution data structure for future frontend display

Technical Notes

- MCTR calculation: `(cov_matrix @ weights) * weights / portfolio_variance`
- Component contribution: `weights * MCTR`
- Use core module PCA for factor attribution
- Prepare constraint framework: sector limits, factor exposures
- Document risk attribution methodology for optimization constraints

OPT-007: Core Covariance and PSD Utilities (Shared)
Status: Not Started
Priority: High
Dependencies: OPT-001, MC-019

Create shared covariance utilities (Ledoit–Wolf/OAS shrinkage), PSD projection helpers, and Sharpe/annualization utilities in `core/stats`. Both simulation and optimization must consume these.

Acceptance Criteria

- Implement shrinkage covariance (Ledoit–Wolf or OAS)
- Implement nearest-PSD projection via eigenvalue clipping and symmetrization
- Provide Sharpe/annualization helpers with clear period/rf handling
- Unit tests cover PSD, shrinkage outputs, and Sharpe conventions

## Additional Features & Ideas (Future Tasks)

**WebSocket Real-time Progress**: Live optimization progress updates ("Iteration 47/100, current Sharpe ratio: 1.23") for complex optimizations that take 5-30 seconds. Essential for user experience during efficient frontier calculations.

**Advanced Financial Metrics**:

- CAPM (Beta calculation against market index) - belongs in core module for both simulation and optimization
- Information Ratio (active return vs tracking error) - core module, useful for optimization constraints
- Stress Testing (scenario analysis with extreme market conditions like 2008 crisis, COVID crash) - simulation module feature
- Sharpe Ratio standardization (ensure industry standard annualized calculations with risk-free rate handling)

**Optimization Constraints & Features**:

- Custom constraint builder: no short-selling, sector limits, max position size, budget constraints
- Efficient frontier visualization with 20-30 optimal portfolios across risk spectrum
- Risk-return scatter plots with optimal portfolio highlighted
- Optimal portfolio weights display (pie charts, allocation tables)
- Historical optimization comparison and performance tracking
- Factor-based optimization constraints (sector allocation limits, factor exposures)

**Production & Architecture**:

- CI/CD pipelines (skip for now - add during production polish phase after 7+ weeks of development)
- Monitoring and logging enhancements for optimization performance
- Docker multi-stage builds optimization
- Portfolio management: save/load configurations, optimization history, export results (JSON, CSV)

**Integration Points**:

- Shared portfolio validation between simulation and optimization modules
- Unified risk metrics calculation (VaR/CVaR) across both modules
- Consistent data models and API response formats
- Single UI with two tabs (simulation + optimization) sharing common components

**Technical Debt & Improvements**:

- Vectorization for optimization engine (skip for simulation - already working code)
- Advanced numerical stability for large portfolio optimizations
- Performance optimization for real-time efficient frontier calculations
- Database query optimization for portfolio history and caching
