from optimization.engine.markowitz import (
    calculate_efficient_frontier,
    maximize_sharpe_portfolio,
)
from core.portfolio import get_portfolio
from core.utils import (
    calculate_mean_and_covariance,
    fetch_close_prices,
    transform_to_daily_returns,
)

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns(close_values)

mean_returns, _, shrunk_cov_matrix = calculate_mean_and_covariance(daily_returns)

efficient_frontier = calculate_efficient_frontier(mean_returns, shrunk_cov_matrix)

sharpe_portfolio = maximize_sharpe_portfolio(mean_returns, shrunk_cov_matrix)
