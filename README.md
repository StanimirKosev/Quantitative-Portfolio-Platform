# Monte Carlo Portfolio Simulation

A comprehensive Monte Carlo simulation tool for multi-asset portfolio analysis with macroeconomic scenario modeling. This educational project demonstrates advanced statistical concepts in portfolio risk management and provides forward-looking analysis under different economic regimes.

## 🎯 Project Overview

This project implements a sophisticated Monte Carlo simulation framework for portfolio analysis, featuring:

- **Multi-asset portfolio simulation** with 6 diverse assets (cryptocurrency, global stocks, commodities, bonds)
- **Historical data analysis** using real market data from Yahoo Finance
- **Macroeconomic scenario modeling** including dollar debasement and geopolitical crisis scenarios
- **Professional risk metrics** including Value at Risk (VaR), Conditional VaR (CVaR), and maximum drawdown
- **Advanced visualization** with confidence intervals and percentile bands

## 📊 Portfolio Composition

The simulation analyzes a diversified portfolio with the following assets:

| Asset | Ticker | Weight | Description |
|-------|--------|--------|-------------|
| Bitcoin | BTC-EUR | 60% | Cryptocurrency hedge |
| MSCI World Energy | 5MVW.DE | 13% | Global developed markets |
| S&P 500 | SPYL.DE | 10.5% | US large-cap stocks |
| Commodities | WMIN.DE | 7% | Global commodities |
| Emerging Markets | IS3N.DE | 6% | Emerging market stocks |
| Gold | 4GLD.DE | 3.5% | Precious metals |

## 🏗️ Architecture

### Core Components

- **`portfolio.py`**: Portfolio definition and macroeconomic regime factors
- **`utils.py`**: Data fetching and statistical calculations
- **`monte_carlo.py`**: Monte Carlo simulation engine and risk metrics
- **`visualization.py`**: Professional plotting and result presentation
- **`main.py`**: Orchestration and execution of all scenarios

### Key Features

1. **Historical Analysis**: Uses 2022-2024 market data to establish baseline parameters
2. **Scenario Modeling**: Tests portfolio performance under different economic conditions
3. **Risk Management**: Calculates industry-standard risk metrics
4. **Visual Analytics**: Professional charts with confidence intervals and statistics

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd monte-carlo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create charts directory** (if not exists):
   ```bash
   mkdir charts
   ```

## 📈 Usage

### Basic Execution

Run the complete simulation with all scenarios:

```bash
python src/main.py
```

This will:
- Download historical data for all portfolio assets
- Calculate mean returns and covariance matrix
- Run Monte Carlo simulations for three scenarios:
  - Historical (baseline)
  - Dollar Debasement
  - Geopolitical Crisis
- Generate visualization charts saved to `charts/` directory

### Understanding the Output

The simulation generates three key visualizations:

1. **Historical Scenario**: Baseline performance using historical market data
2. **Dollar Debasement**: Scenario where USD weakens, benefiting inflation hedges
3. **Geopolitical Crisis**: Risk-off scenario favoring safe-haven assets

Each chart displays:
- **Confidence intervals**: 50%, 80%, and 90% bands showing uncertainty
- **Key paths**: Median (most likely), best case, and worst case scenarios
- **Risk metrics**: VaR, CVaR, and performance statistics
- **Performance summary**: Final values and percentage returns

## 📊 Interpreting Results

### Key Metrics Explained

#### Performance Metrics
- **Median Path**: The most likely outcome (50th percentile)
- **Mean Path**: Average across all simulations
- **Best/Worst Case**: Extreme outcomes from 1000 simulations

#### Risk Metrics
- **Value at Risk (VaR)**: Maximum expected loss at given confidence level
  - 95% VaR: Portfolio value that 95% of outcomes exceed
  - 99% VaR: Portfolio value that 99% of outcomes exceed
- **Conditional VaR (CVaR)**: Average loss when VaR threshold is breached
- **Confidence Intervals**: Range of likely outcomes (e.g., 90% of paths fall within the light blue band)

### Scenario Analysis

#### Historical Scenario
- Uses actual market data from 2022-2024
- Represents baseline expectations based on recent market behavior

#### Dollar Debasement Scenario
- Models USD weakness and inflationary pressures
- **Winners**: Bitcoin (+20%), Gold (+15%), Commodities (+15%)
- **Losers**: US stocks (-10%) due to higher rates

#### Geopolitical Crisis Scenario
- Models risk-off environment with flight to safety
- **Winners**: Gold (+30%) as safe haven
- **Losers**: Emerging markets (-60%), US stocks (-50%), Bitcoin (-30%)

## 🔬 Statistical Methodology

### Monte Carlo Simulation
1. **Data Collection**: Historical daily returns from Yahoo Finance
2. **Parameter Estimation**: Mean returns and covariance matrix calculation
3. **Random Sampling**: Multivariate normal distribution for correlated returns
4. **Path Generation**: 1000 simulations over 252 trading days
5. **Risk Analysis**: Percentile-based risk metrics and statistics

### Key Assumptions
- **Normal Distribution**: Asset returns follow multivariate normal distribution
- **Stationarity**: Historical relationships persist into the future
- **No Transaction Costs**: Perfect rebalancing at portfolio weights
- **252 Trading Days**: Standard annual trading period

## 🛠️ Customization

### Modifying Portfolio
Edit `src/portfolio.py` to change assets or weights:

```python
def get_portfolio():
    tickers = ["YOUR_TICKERS"]
    weights = [YOUR_WEIGHTS]  # Must sum to 1.0
    return (tickers, weights)
```

### Adding New Scenarios
Create new regime factors in `src/portfolio.py`:

```python
NEW_SCENARIO = {
    "TICKER1": 1.1,  # 10% higher returns
    "TICKER2": 0.9,  # 10% lower returns
}
```

### Adjusting Simulation Parameters
Modify simulation settings in `src/monte_carlo.py`:

```python
# Change number of simulations
portfolio_paths = simulate_portfolio_paths(
    mean_returns, cov_matrix, weights, 
    num_simulations=2000  # Default: 1000
)

# Change initial portfolio value
portfolio_paths = simulate_portfolio_paths(
    mean_returns, cov_matrix, weights,
    initial_value=50000  # Default: 10000
)
```

## 📚 Educational Value

This project demonstrates key concepts in:
- **Portfolio Theory**: Diversification, correlation, and risk-return relationships
- **Statistical Modeling**: Monte Carlo methods, probability distributions
- **Risk Management**: VaR, CVaR, and confidence intervals
- **Macroeconomic Analysis**: Scenario modeling and sensitivity analysis
- **Data Science**: Financial data processing and visualization

## 🤝 Contributing

This is an educational project focused on learning Monte Carlo methods and portfolio analysis. Contributions that improve:
- Statistical methodology
- Risk metrics
- Visualization quality
- Documentation clarity

are welcome and encouraged.

## 📄 License

This project is for educational purposes. Please ensure compliance with data provider terms of service when using financial data.

## 🔗 Dependencies

- **numpy**: Numerical computations and random sampling
- **pandas**: Data manipulation and analysis
- **matplotlib**: Professional visualization
- **yfinance**: Financial data retrieval
- **black**: Code formatting (development)

---

*Built for educational purposes to explore Monte Carlo simulation in portfolio analysis and risk management.*