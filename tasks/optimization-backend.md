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

**OPT-005: Data Caching and FastAPI Optimization Router**
Status: Completed
Priority: High
Dependencies: OPT-003

Implement intelligent caching for expensive data fetching operations and create FastAPI optimization endpoints.
Address performance bottleneck where Yahoo Finance API calls are repeated across simulation, optimization, and validation endpoints.

Acceptance Criteria

**Caching Implementation:**

- Add LRU caching with `@lru_cache(maxsize=128)` to `get_cached_prices()` in `core/utils.py`
- Implement automatic memory management (no TTL needed for historical data)
- Create cache key from comma-separated tickers + date range for proper cache hits
- Cache hit/miss logging for monitoring via existing fetch_close_prices logs
- Automatic LRU cache cleanup to prevent memory leaks

**Optimization Endpoints:**

- `/api/optimize/{regime}` endpoint for default portfolio (already existed)
- `/api/optimize/custom` endpoint for custom portfolio (already existed)
- Pydantic models for optimization requests/responses (already existed)
- Integration with existing FastAPI app structure (already existed)

**Additional Achievements:**

- Added caching to validation endpoint for complete user workflow optimization
- Updated all test mocks from `fetch_close_prices` to `get_cached_prices`
- Added comprehensive cache functionality tests (3 new test methods)
- Verified 386,000x speedup on cache hits vs cache misses

Technical Notes

**Actual Implementation:**

- Used `@lru_cache(maxsize=128)` instead of manual dictionary - more robust and thread-safe
- Cache key: `f"{comma_separated_tickers}_{start}_{end}"` without sorting to preserve user intent
- No TTL needed - historical data never changes, perfect for LRU cache
- Transparent caching - existing API code only needed 2-line changes per endpoint
- Production-ready: handles concurrent requests, automatic memory management

**Performance Impact:**

- **Before:** Frontend carousel = 2+ Yahoo Finance API calls (slow)
- **After:** Frontend carousel = 1 Yahoo Finance call + cache hits (instant)
- **User workflow:** Validation → Simulation → Optimization = 1 API call + 2 cache hits

**OPT-006: Real-time WebSocket Progress Updates**
Status: Completed ✅
Priority: Medium
Dependencies: OPT-005

Implement WebSocket-based real-time progress updates for efficient frontier calculations.
Professional asyncio implementation with background thread coordination and WebSocket broadcasting.

Acceptance Criteria

- ✅ Added `progress_callback` parameter to `calculate_efficient_frontier()` function
- ✅ Created WebSocket endpoint `/api/optimize/ws/progress` for real-time updates  
- ✅ Emit progress events: `{"current": 15, "total": 25, "message": "...", "percentage": 60.0}`
- ✅ Implemented `ProgressBroadcaster` class for WebSocket connection management
- ✅ Background thread coordination with `asyncio.to_thread()` and `run_coroutine_threadsafe()`
- ✅ Clean connection lifecycle management (connect/disconnect/broadcast)

Technical Implementation

- **Threading Architecture**: Main event loop handles WebSockets/HTTP, background thread runs CPU-intensive optimization
- **Bridge Pattern**: `create_progress_callback()` bridges background thread to main event loop via `asyncio.run_coroutine_threadsafe()`  
- **WebSocket Management**: `ProgressBroadcaster` handles multiple concurrent connections with dead connection cleanup
- **Production Ready**: Error handling, connection lifecycle management, clean separation of concerns

**OPT-007: Production Infrastructure**
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
