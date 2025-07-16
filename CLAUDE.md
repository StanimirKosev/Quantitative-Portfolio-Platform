# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
python src/main.py
```
This is the main entry point that executes all Monte Carlo simulations for historical, fiat debasement, and geopolitical crisis regimes.

### Code Formatting
```bash
black src/
```
Format all Python files using Black formatter (configured in requirements.txt).

### Dependencies
```bash
pip install -r requirements.txt
```
Install all required packages: numpy, pandas, matplotlib, yfinance, black, seaborn.

## Architecture Overview

This is a Monte Carlo portfolio simulation platform with regime-dependent risk modeling. The codebase is organized into 5 main modules:

### Core Architecture
- **main.py**: Orchestrates simulation for 3 regimes (historical, fiat debasement, geopolitical crisis)
- **portfolio.py**: Defines 6-asset portfolio (Bitcoin, energy, stocks, mining, emerging markets, gold) with regime modification parameters
- **utils.py**: Data fetching from Yahoo Finance, return calculations, covariance matrix computation
- **monte_carlo.py**: Core simulation engine with regime parameter modifications, risk metrics (VaR, CVaR), and PCA analysis
- **visualization.py**: Professional charts including simulation results, correlation heatmaps, and PCA analysis

### Key Design Patterns
- **Regime-based modeling**: Each regime (historical, fiat debasement, geopolitical crisis) modifies mean returns and covariance matrices using multiplicative factors
- **Multi-asset correlation**: Uses multivariate normal distribution sampling with full covariance matrix
- **Risk factor decomposition**: Implements eigenvalue decomposition and PCA to identify dominant risk factors
- **Professional visualization**: Creates publication-ready charts with confidence intervals, percentile bands, and statistical annotations

### Data Flow
1. **Data Acquisition**: Yahoo Finance API fetches historical prices → daily returns calculation
2. **Regime Modification**: Base historical statistics modified by regime-specific factors for mean returns and volatility
3. **Monte Carlo Simulation**: 1000 simulation paths over 252 trading days using multivariate normal sampling
4. **Risk Analysis**: VaR, CVaR, maximum drawdown, and PCA analysis
5. **Visualization**: Charts saved to `charts/` directory organized by regime

### Portfolio Configuration
The portfolio uses 6 assets with fixed weights:
- Bitcoin (BTC-EUR): 60% - Primary hedge against fiat debasement
- Energy Sector (5MVW.DE): 13% - Inflation hedge
- S&P 500 (SPYL.DE): 10.5% - Large cap exposure
- Mining (WMIN.DE): 7% - Commodity exposure
- Emerging Markets (IS3N.DE): 6% - Diversification
- Gold (4GLD.DE): 3.5% - Safe haven asset

### Regime Parameters
Regimes modify base statistics through:
- `mean_factor`: Multiplicative adjustment to expected returns
- `vol_factor`: Multiplicative adjustment to asset volatility
- `correlation_move_pct`: Percentage adjustment to correlation matrix

## Key Implementation Details

### Simulation Parameters
- **Simulations**: 1000 paths per regime
- **Time horizon**: 252 trading days (1 year)
- **Initial portfolio value**: $10,000
- **Risk metrics**: VaR/CVaR at 95% and 99% confidence levels

### File Organization
- `/src/`: All Python source code
- `/charts/`: Output directory for visualization (auto-created)
- `/charts/{regime_name}/`: Regime-specific chart directories
- Chart types: monte_carlo_simulation, correlation_matrix, risk_factor_analysis
- `/tasks/`: Task management and planning documentation
- `/tasks/backend-tasks.md`: Backend development tasks and priorities
- `/tasks/frontend-tasks.md`: Frontend integration sprint tasks

### Testing and Validation
No formal test suite exists. Validation is done through:
- Visual inspection of simulation results
- Statistical validation of risk metrics
- Correlation matrix eigenvalue analysis
- PCA explained variance ratios

## Customization Guidelines

### Adding New Assets
1. Update `get_portfolio()` in `portfolio.py` with new tickers and weights
2. Add regime factors for new assets in regime dictionaries
3. Ensure weights sum to 1.0

### Adding New Regimes
1. Define regime dictionary in `portfolio.py` with `mean_factor`, `vol_factor` for each asset
2. Add `correlation_move_pct` for correlation adjustments
3. Update `main.py` to include new regime simulation and visualization

### Modifying Simulation Parameters
Edit `simulate_portfolio_paths()` calls in `main.py`:
- `num_simulations`: Number of Monte Carlo paths
- `time_steps`: Trading days to simulate
- `initial_value`: Starting portfolio value