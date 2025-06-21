from portfolio import get_portfolio
from utils import (
    fetch_close_prices,
    transform_to_daily_returns_percent,
    calculate_mean_and_covariance,
)
from monte_carlo import simulate_portfolio_paths, calculate_risk_metrics
from visualization import plot_simulation_results

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns_percent(close_values)

mean_returns, cov_matrix = calculate_mean_and_covariance(daily_returns)

portfolio_paths = simulate_portfolio_paths(mean_returns, cov_matrix, weights)

calculate_risk_metrics(portfolio_paths)

plot_simulation_results(portfolio_paths)
