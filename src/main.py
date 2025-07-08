from portfolio import (
    get_portfolio,
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
)
from utils import (
    fetch_close_prices,
    transform_to_daily_returns_percent,
    calculate_mean_and_covariance,
)
from monte_carlo import (
    simulate_portfolio_paths,
    modify_returns_for_regime,
    get_cov_matrix_analysis,
)
from visualization import plot_simulation_results

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns_percent(close_values)

mean_historical_returns, cov_matrix = calculate_mean_and_covariance(daily_returns)

historical_paths = simulate_portfolio_paths(
    mean_historical_returns, cov_matrix, weights
)

mean_fiat_debasement_returns = modify_returns_for_regime(
    mean_historical_returns, tickers, FIAT_DEBASEMENT_REGIME
)
fiat_debasement_path = simulate_portfolio_paths(
    mean_fiat_debasement_returns, cov_matrix, weights
)

mean_geopolitical_crisis_returns = modify_returns_for_regime(
    mean_historical_returns,
    tickers,
    GEOPOLITICAL_CRISIS_REGIME,
)
geopolitical_crisis_path = simulate_portfolio_paths(
    mean_geopolitical_crisis_returns, cov_matrix, weights
)

plot_simulation_results(historical_paths, "Historical")
plot_simulation_results(fiat_debasement_path, "Fiat Debasement")
plot_simulation_results(geopolitical_crisis_path, "Geopolitical Crisis")

get_cov_matrix_analysis(cov_matrix)
