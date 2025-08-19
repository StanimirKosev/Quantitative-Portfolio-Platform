from optimization.engine.markowitz import (
    calculate_efficient_frontier,
    maximize_sharpe_portfolio,
)
from core.portfolio import (
    get_portfolio,
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
)
from core.utils import (
    calculate_mean_and_covariance,
    fetch_close_prices,
    transform_to_daily_returns,
)
from simulation.engine.monte_carlo import modify_portfolio_for_regime

tickers, _ = get_portfolio()

close_values = fetch_close_prices(tickers)
daily_returns = transform_to_daily_returns(close_values)

# Historical regime: Baseline scenario using actual past returns and risk.

historical_mean_returns, _, historical_shrunk_cov = calculate_mean_and_covariance(
    daily_returns
)

historical_frontier = calculate_efficient_frontier(
    historical_mean_returns, historical_shrunk_cov
)
historical_max_sharpe = maximize_sharpe_portfolio(
    historical_mean_returns, historical_shrunk_cov
)

# Fiat debasement regime: Simulates strong inflation, BTC and gold outperform, risk-on environment.

fiat_mean_returns, fiat_cov_matrix = modify_portfolio_for_regime(
    historical_mean_returns, historical_shrunk_cov, FIAT_DEBASEMENT_REGIME
)

fiat_frontier = calculate_efficient_frontier(fiat_mean_returns, fiat_cov_matrix)
fiat_max_sharpe = maximize_sharpe_portfolio(fiat_mean_returns, fiat_cov_matrix)

# Geopolitical crisis regime: Simulates global conflict, equities/EM down, gold/energy up, higher volatility.

geo_mean_returns, geo_cov_matrix = modify_portfolio_for_regime(
    historical_mean_returns, historical_shrunk_cov, GEOPOLITICAL_CRISIS_REGIME
)

geo_frontier = calculate_efficient_frontier(geo_mean_returns, geo_cov_matrix)
geo_max_sharpe = maximize_sharpe_portfolio(geo_mean_returns, geo_cov_matrix)
