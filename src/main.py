from portfolio import get_portfolio
from utils import (
    fetch_close_prices,
    transform_to_daily_returns_percent,
    calculate_mean_and_covariance,
)
from monte_carlo import generate_sample

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns_percent(close_values)

mean_returns, cov_matrix = calculate_mean_and_covariance(daily_returns)

portfolio_returns = generate_sample(mean_returns, cov_matrix, weights)

print(portfolio_returns)
