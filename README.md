# Monte Carlo Portfolio Simulation

Monte Carlo simulation platform for multi-asset portfolios, featuring regime-dependent risk modeling, scenario-based analytics, and advanced visualizations. Built to explore how real-world macroeconomic shifts impact portfolio outcomes, this project integrates real market data, flexible scenario design, and industry-standard risk metrics. Includes principal component analysis (PCA) and eigenvalue decomposition for deep risk factor insights.

## 🎯 Project Overview

- **Multi-asset portfolio simulation** with 6 diverse assets (Bitcoin, global stocks, commodities)
- **Historical data analysis** using real market data from Yahoo Finance
- **Macroeconomic regime modeling** (fiat debasement, geopolitical crisis, and more)
- **Regime-dependent covariance matrices** for realistic scenario stress-testing
- **Professional risk metrics**: Value at Risk (VaR), Conditional VaR (CVaR)
- **PCA & eigenvalue analysis**: Identify dominant risk factors and explained variance
- **Advanced visualization**: Confidence intervals, percentile bands, and clear analytics

## 📊 Portfolio Composition

| Asset | Ticker | Weight | Description |
|-------|--------|--------|-------------|
| Bitcoin | BTC-EUR | 60% | Cryptocurrency hedge |
| iShares MSCI World Energy Sector | 5MVW.DE | 13% | Global developed energy markets |
| SPDR S&P 500 | SPYL.DE | 10.5% | US large-cap stocks |
| VanEck S&P Global Mining | WMIN.DE | 7% | Global miners |
| iShares Core MSCI EM IMI | IS3N.DE | 6% | Emerging market stocks |
| Gold | 4GLD.DE | 3.5% | Precious metals |

## 🏗️ Architecture & Features

- **portfolio.py**: Portfolio definition and regime factors
- **utils.py**: Data fetching and statistics
- **monte_carlo.py**: Simulation engine, risk metrics, PCA, eigenvalue analysis
- **visualization.py**: Professional plotting and analytics
- **main.py**: Orchestrates all regimes and outputs

**Key features:**
- Historical and regime-based analysis
- Scenario-driven risk and return simulation
- PCA/eigenvalue decomposition for risk factor analysis
- Visual analytics: simulation results, correlation heatmaps, PCA bar charts

## 🚀 Installation

**Prerequisites:** Python 3.8+, pip

```bash
# Clone and install
git clone <repository-url>
cd monte-carlo
pip install -r requirements.txt
mkdir charts  # if not exists
```

## 📈 Usage

Run all scenarios:
```bash
python src/main.py
```

This will:
- Download historical data
- Calculate mean returns and covariance
- Simulate portfolio under historical, fiat debasement, and geopolitical crisis regimes
- Output charts to `charts/`

## 📊 Output & Interpretation

Each regime produces:
- **Simulation results**: Confidence intervals, key paths, risk metrics (VaR, CVaR)
- **Correlation heatmap**: Asset correlations, matrix conditioning
- **PCA analysis**: Principal components, explained variance, factor loadings

**Key metrics:**
- Median, mean, best/worst case outcomes
- VaR/CVaR at 95% and 99% levels
- PCA: top risk factors, asset contributions

## 🔬 Methodology & Assumptions

- Historical daily returns from Yahoo Finance
- Mean/covariance estimation, regime-dependent adjustments
- Multivariate normal sampling for correlated returns
- 1000 simulations, 252 trading days
- No transaction costs, perfect rebalancing

## 🛠️ Customization

**Change portfolio:** Edit `src/portfolio.py`:
```python
def get_portfolio():
    tickers = ["YOUR_TICKERS"]
    weights = [YOUR_WEIGHTS]  # Must sum to 1.0
    return (tickers, weights)
```

**Add new regime:**
```python
NEW_REGIME = {
    "BTC-EUR": {"mean_factor": 1.2, "vol_factor": 1.1},
    # ... all assets ...
    "correlation_move_pct": 0.1
}
```

**Adjust simulation parameters:** Edit `src/monte_carlo.py`:
```python
portfolio_paths = simulate_portfolio_paths(
    mean_returns, cov_matrix, weights, num_simulations=2000, initial_value=50000
)
```

## 📚 Educational Value

Demonstrates:
- Portfolio theory, diversification, correlation
- Monte Carlo methods, risk metrics (VaR, CVaR)
- Regime/sensitivity analysis
- PCA/eigenvalue decomposition for risk factors
- Data science: financial data processing, visualization

## 📄 License & Dependencies

- **numpy**: Numerical computations
- **pandas**: Data analysis
- **matplotlib**: Visualization
- **yfinance**: Data retrieval
- **black**: Code formatting