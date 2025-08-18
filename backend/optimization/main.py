from core.portfolio import get_portfolio
from core.utils import (
    calculate_mean_and_covariance,
    fetch_close_prices,
    transform_to_daily_returns,
)

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns(close_values)

mean_returns, cov_matrix = calculate_mean_and_covariance(daily_returns)
