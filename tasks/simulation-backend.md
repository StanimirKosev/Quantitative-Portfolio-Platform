Current Sprint Tasks
MC-001: Create Portfolio Assets Data
Status: Completed
Priority: High
Dependencies: None

Define 6 different assets (stocks) in portfolio.py
Store asset tickers as a list
Add portfolio weights (how much of each asset)

Acceptance Criteria

List of 6 stock tickers exists
Portfolio weights sum to 1.0
Weights are stored in a list/array

Technical Notes

Use simple Python lists for now
Example: tickers = ['AAPL', 'GOOGL', ...]
Example: weights = [0.2, 0.15, ...]

MC-002: Download Historical Stock Data
Status: Completed
Priority: High
Dependencies: MC-001

Create function to download stock price data
Use yahoo finance or similar free source
Store daily returns data

Acceptance Criteria

Function downloads data for given ticker
Function calculates daily returns
Returns are stored as percentage changes

Technical Notes

Use pandas for data handling
Daily return = (today_price - yesterday_price) / yesterday_price
Store returns, not prices

MC-003: Calculate Mean Returns and Covariance
Status: Completed
Priority: High
Dependencies: MC-002

Calculate average daily return for each asset
Calculate covariance matrix between all assets
Store these as numpy arrays

Acceptance Criteria

Mean returns calculated for all 6 assets
6x6 covariance matrix created
Results stored in variables for later use

Technical Notes

Use numpy.mean() for returns
Use numpy.cov() for covariance matrix
Covariance shows how assets move together

MC-004: Generate Random Samples
Status: Completed
Priority: High
Dependencies: MC-003

Create function to generate random numbers
Use multivariate normal distribution
Generate samples for portfolio simulation

Acceptance Criteria

Function generates random return samples
Samples follow multivariate normal distribution
Can specify number of simulations and time steps

Technical Notes

Use numpy.random.multivariate_normal()
Input: mean returns, covariance matrix
Output: random daily returns for simulation

MC-005: Run Basic Portfolio Simulation
Status: Completed
Priority: High
Dependencies: MC-004

Simulate portfolio value over time
Start with initial portfolio value
Apply random returns day by day

Acceptance Criteria

Portfolio starts at $10,000 (or chosen amount)
Each day applies random returns to portfolio
Tracks total portfolio value over time
Runs multiple simulations (e.g., 1000 times)

Technical Notes

portfolio_value[day] = portfolio_value[day-1] \* (1 + daily_return)
Store all simulation paths
Each simulation is one possible future

MC-006: Visualize Monte Carlo Results
Status: Completed
Priority: High
Dependencies: MC-005

Create plots to visualize Monte Carlo simulation results
Show portfolio paths, statistics, and risk metrics
Display uncertainty and confidence intervals

Acceptance Criteria

Plot all 1000 simulation paths (transparent)
Display confidence intervals (e.g., 90% range)
Include key statistics (mean, median, best/worst case)
Professional-looking visualization with proper labels

Technical Notes

Use matplotlib for plotting
Plot individual paths with low alpha for transparency
Use different colors for mean, median, and confidence bands
Add statistics text box on the plot
Include proper axis labels and title

MC-007: Calculate Risk Metrics
Status: Completed
Priority: High
Dependencies: MC-006

Calculate industry-standard risk measures for portfolio analysis
Implement Value at Risk (VaR) and Expected Shortfall calculations
Analyze maximum drawdown and other risk indicators
Create risk-return scatter plot visualization

Acceptance Criteria

Calculate VaR at 90%, 95% and 99% confidence levels (on loss distribution)
Calculate Conditional VaR (Expected Shortfall) at same levels (tail mean)
Guard for empty tails (CVaR falls back to VaR if tail is empty)
Determine maximum drawdown from all simulation paths (moved to MC-007A)
Display risk metrics in clear, interpretable format
Support documented annualization for different horizons
Validate VaR/CVaR against known test cases

Technical Notes

Work with cumulative returns: R = V_T / V_0 - 1; define Loss L = -R
VaR (95%) = percentile(L, 95); CVaR (95%) = mean(L[L >= VaR95])
Report both absolute loss amounts and percentage losses
Max drawdown = largest peak-to-trough decline (see MC-007A)
Use numpy.percentile() and conditional tail means
Support multiple confidence levels and document annualization conventions

MC-008: Add Your Unique Angle
Status: Completed
Priority: Medium
Dependencies: MC-007

Implement forward-looking macroeconomic scenario analysis
Create generalized system for modifying simulation parameters with simple arithmetic
Test how different parameter adjustments affect portfolio outcomes

Acceptance Criteria

Test different parameter combinations:

- Fiat debasement scenario (your macro view)
- High inflation vs deflation scenarios
- High vs low volatility scenarios

Show sensitivity analysis:

- How small parameter changes affect final outcomes
- Risk/return profiles under different assumptions
- Visualization of multiple scenarios

Technical Notes

Use simple arithmetic operations:

- mean_returns \* inflation_factor
- cov_matrix \* volatility_multiplier
- correlation_adjustments for asset relationships

MC-009: Documentation & README
Status: Completed
Priority: High
Dependencies: MC-008

Create comprehensive project documentation
Write clear README with methodology explanation
Provide usage instructions and result interpretation

Acceptance Criteria

Clear README.md explaining project purpose and methodology
Installation and usage instructions
Interpretation guide for simulation results
Professional project structure and documentation

Technical Notes

Include problem statement and solution approach
Document all dependencies and installation steps
Explain key concepts and statistical methodology
Provide examples of how to interpret results

MC-010: Covariance Matrix Deep Analysis
Status: Completed
Priority: High
Dependencies: MC-003

Enhance covariance matrix analysis with eigenvalue decomposition and correlation visualization

Acceptance Criteria

Calculate eigenvalues and eigenvectors of covariance (or correlation) matrix
Identify dominant risk factors (top 2-3 eigenvalues)
Create correlation matrix heatmap visualization
Compute conditioning diagnostics (condition number and min eigenvalue)
Validate PSD after any covariance/correlation modification (min eigenvalue ≥ tolerance)
If needed, apply nearest-PSD projection and re-validate # Note: PSD projection intentionally omitted by design to let users see invalid matrices
Add interpretation text explaining main risk drivers

Technical Notes

Use np.linalg.eigh() for symmetric (co)variance/correlation matrices
Create correlation matrix from covariance: corr = cov / (std_outer_product)
Use plt.imshow() or seaborn.heatmap() for correlation visualization
Condition number = max_eigenvalue / min_eigenvalue; also report min eigenvalue to indicate PSD status
Nearest-PSD projection via eigenvalue clipping; symmetrize result, set diagonal to 1.0, clip to [-1, 1]
Log/warn when projection was required

MC-011: Principal Component Analysis (PCA)
Status: Completed
Priority: Medium
Dependencies: MC-010

Add PCA analysis to identify and visualize main risk factors in portfolio

Acceptance Criteria

Calculate principal components of returns data
Show explained variance ratio for each component
Create factor loadings visualization
Identify which assets contribute most to each principal component
Add interpretation of top 2-3 factors

Technical Notes

Use eigh()-based eigen decomposition from MC-010
Sort eigenvalues/eigenvectors by importance
Calculate explained variance ratio
Create bar charts for factor loadings
Focus on components explaining >10% of variance

MC-007A: Maximum Drawdown Calculation
Status: Completed
Priority: Medium
Dependencies: MC-007

Calculate maximum drawdown across all simulation paths and integrate into risk metrics output.

Acceptance Criteria

- Compute per-path max drawdown (peak-to-trough) and summary stats (mean, median, worst)
- Display max drawdown in risk metrics panel
- Unit test drawdown logic on synthetic monotone and V-shaped paths

Technical Notes

- Use rolling peak tracking with vectorized operations when possible
- Drawdown = (trough - peak) / peak; report as negative percentage

MC-008A: Regime-Dependent Covariance Matrices
Status: Completed
Priority: High
Dependencies: MC-008

Implement the ability to adjust the covariance matrix for each macroeconomic regime (e.g., crisis, debasement). Simulate and analyze portfolio risk using regime-specific covariance matrices.

Acceptance Criteria

- Allow scaling or modifying the covariance matrix for each regime
- Simulate portfolio paths using regime-specific covariance matrices
- Visualize and analyze risk metrics, eigenvalues, and principal components for each regime
- All statistics and visualizations are consistent with the scenario

Technical Notes

- Start with simple scaling (e.g., cov_matrix \* factor)
- Optionally, allow for custom correlation adjustments
- Update all analysis and visualization scripts to use the correct matrix for each regime

MC-012: Docker and GCP Deployment
Status: Completed
Priority: High
Dependencies: FE-002, FE-003

Objective: Containerize backend and frontend, run both locally, push images to GCP Artifact Registry, and deploy on Cloud Run.

Acceptance Criteria

- Backend image builds and runs locally:
  - `docker build -t montecarlo-backend ./api`
  - `docker run --rm -p 8000:8000 montecarlo-backend`
  - API reachable at `http://localhost:8000/`
- Frontend image builds and runs locally (Vite preview on port 8080):
  - `docker build --build-arg VITE_API_URL=http://localhost:8000 -t montecarlo-frontend ./frontend`
  - `docker run --rm -p 5173:8080 montecarlo-frontend`
  - App reachable at `http://localhost:5173/` and calls the API
- Local container testing done individually:
  - Backend: `docker build -t montecarlo-backend ./api && docker run --rm -p 8000:8000 montecarlo-backend`
  - Frontend: `docker build --build-arg VITE_API_URL=http://localhost:8000 -t montecarlo-frontend ./frontend && docker run --rm -p 5173:8080 montecarlo-frontend`
- GCP Artifact Registry repositories created and images pushed for both services
- Two Cloud Run services created from Artifact Registry images:
  - Backend: listens on `$PORT` (Dockerfile defaults to 8000 locally)
  - Frontend: listens on `$PORT` (Dockerfile defaults to 8080 locally) and is built with `VITE_API_URL=<backend Cloud Run URL>`
- Visiting the frontend Cloud Run URL shows data loaded from the backend Cloud Run URL

MC-013: Add Type Hints and Python Typing
Status: Completed
Priority: High
Dependencies: MC-012
Add comprehensive type hints throughout the Monte Carlo simulation codebase
Improve code clarity, IDE support, and catch potential type-related bugs
Prepare foundation for core module extraction

Acceptance Criteria

All functions have proper type hints for parameters and return values
Import necessary typing modules (List, Dict, Tuple, Optional, etc.)
Portfolio data structures properly typed
NumPy arrays typed with appropriate shape annotations
API endpoint functions include proper FastAPI type annotations

Technical Notes

Use from typing import List, Dict, Tuple, Optional, Union
NumPy arrays: np.ndarray or npt.NDArray[np.floating]
Portfolio weights: List[float] or np.ndarray
Return data: pd.DataFrame for historical data
Follow PEP 484 typing conventions

MC-014: Replace Nested Dicts with Pydantic Models
Status: Completed
Priority: High
Dependencies: MC-013
Convert nested dictionary structures to typed Pydantic models
Improve data validation, serialization, and API documentation
Create foundation for shared data models in core module
Acceptance Criteria

Create Portfolio model with tickers, weights, date_range fields
Create SimulationResult model for Monte Carlo outputs
Create RegimeParameters model for scenario configurations
Replace all nested dict usage with these models
Automatic API documentation generation via FastAPI + Pydantic

Technical Notes

Install pydantic: pip install pydantic
Use BaseModel for all data structures
Add field validation (weights sum to 1.0, positive values)
Include Config class for JSON serialization
Update API endpoints to use Pydantic models

MC-015: Implement Comprehensive Testing Suite
Status: Not Started
Priority: High
Dependencies: MC-014
Create unit tests for mathematical functions and integration tests for API endpoints
Focus on core financial calculations that will be reused in optimization module
Establish TDD foundation for future development
Acceptance Criteria

Unit tests for covariance matrix calculations (including PSD properties)
Unit tests for PCA and eigenvalue decomposition functions
Unit tests for portfolio simulation logic
Integration tests for all API endpoints
Tests for regime parameter adjustments
Achieve >80% code coverage on core mathematical functions

Technical Notes

Use pytest framework: pip install pytest pytest-cov
Create tests/ directory with test\_\*.py files
Test mathematical properties: matrix symmetry, eigenvalue ordering
Use pytest.approx() for floating-point comparisons
Mock external data sources (yfinance) in tests
Run tests with: pytest --cov=app tests/

MC-016: Add GCP Structured Logging
Status: Not Started
Priority: Medium
Dependencies: MC-010
Implement structured logging compatible with Google Cloud Platform
Add comprehensive logging throughout simulation pipeline
Prepare logging infrastructure for production deployment and debugging
Acceptance Criteria

Configure structured JSON logging for GCP Cloud Logging
Add INFO level logs for simulation start/completion
Add DEBUG level logs for intermediate calculation steps
Add ERROR level logs with proper exception handling
Include request IDs for API endpoint tracing
Log performance metrics (simulation timing, data fetch duration)

Technical Notes

Use Python logging module with JSON formatter
Install google-cloud-logging: pip install google-cloud-logging
Configure different log levels for development vs production
Include correlation IDs for request tracing
Log statistical validation (matrix properties, convergence)
Avoid logging sensitive data (only metadata and metrics)

MC-017: Core Module Foundation Setup
Status: Not Started
Priority: High
Dependencies: MC-016
Create the foundation for shared core module that will support both simulation and optimization
Extract reusable components while maintaining simulation functionality
Prepare architecture for portfolio optimization integration
Acceptance Criteria

Create core/ package with proper **init**.py structure
Move data fetching logic to core/data/ module
Move statistical calculations to core/stats/ module
Move validation logic to core/validation/ module
Update simulation module to import from core
All existing functionality continues to work unchanged
Clear separation between simulation-specific and shared logic

Technical Notes

Create package structure: core/**init**.py, core/data/**init**.py, etc.
Move yfinance wrapper to core/data/market_data.py
Move covariance, PCA, VaR/CVaR to core/stats/risk_metrics.py
Move portfolio validation to core/validation/portfolio.py
Update imports in simulation module
Maintain backward compatibility during transition
Document core module API for optimization phase
