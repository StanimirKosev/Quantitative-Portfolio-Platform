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

portfolio_value[day] = portfolio_value[day-1] * (1 + daily_return)
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
Status: Not Started
Priority: High
Dependencies: MC-006

Calculate industry-standard risk measures for portfolio analysis
Implement Value at Risk (VaR) and Expected Shortfall calculations
Analyze maximum drawdown and other risk indicators
Create risk-return scatter plot visualization

Acceptance Criteria

Calculate VaR at 95% and 99% confidence levels
Calculate Conditional VaR (Expected Shortfall) at same levels
Determine maximum drawdown from all simulation paths
Display risk metrics in clear, interpretable format

Technical Notes

VaR = percentile of final portfolio values
CVaR = mean of values below VaR threshold
Max drawdown = largest peak-to-trough decline
Use numpy.percentile() and conditional calculations

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
- mean_returns * inflation_factor
- cov_matrix * volatility_multiplier
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

Calculate eigenvalues and eigenvectors of covariance matrix
Identify dominant risk factors (top 2-3 eigenvalues)
Create correlation matrix heatmap visualization
Check matrix conditioning number
Add interpretation text explaining main risk drivers

Technical Notes

Use np.linalg.eig() for eigenvalue decomposition
Create correlation matrix from covariance: corr = cov / (std_outer_product)
Use plt.imshow() or seaborn.heatmap() for correlation visualization
Conditioning number = max_eigenvalue / min_eigenvalue


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

Use eigenvalue decomposition from MC-010
Sort eigenvalues/eigenvectors by importance
Calculate explained variance ratio
Create bar charts for factor loadings
Focus on components explaining >10% of variance

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

- Start with simple scaling (e.g., cov_matrix * factor)
- Optionally, allow for custom correlation adjustments
- Update all analysis and visualization scripts to use the correct matrix for each regime