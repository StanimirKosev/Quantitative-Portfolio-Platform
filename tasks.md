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

Current Focus
Project Complete! All core simulation and visualization tasks are finished.