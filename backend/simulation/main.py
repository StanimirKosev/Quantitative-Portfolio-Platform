from core.portfolio import (
    get_portfolio,
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
)
from core.utils import (
    FIAT_DEBASEMENT_REGIME_NAME,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    HISTORICAL,
    fetch_close_prices,
    transform_to_daily_returns,
    calculate_mean_and_covariance,
)
from simulation.engine.monte_carlo import (
    simulate_portfolio_paths,
    modify_portfolio_for_regime,
)
from simulation.engine.visualization import (
    plot_correlation_heatmap,
    plot_portfolio_pca_analysis,
    plot_simulation_results,
)

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns(close_values)

# Historical regime: Baseline scenario using actual past returns and risk.
historical_mean_returns, historical_cov_matrix = calculate_mean_and_covariance(
    daily_returns
)

historical_paths = simulate_portfolio_paths(
    historical_mean_returns, historical_cov_matrix, weights
)

plot_simulation_results(historical_paths, HISTORICAL)

plot_correlation_heatmap(
    historical_cov_matrix,
    HISTORICAL,
)

plot_portfolio_pca_analysis(
    historical_cov_matrix,
    HISTORICAL,
)


# Fiat debasement regime: Simulates strong inflation, BTC and gold outperform, risk-on environment.
fiat_debasement_mean_returns, fiat_debasement_cov_matrix = modify_portfolio_for_regime(
    historical_mean_returns, historical_cov_matrix, FIAT_DEBASEMENT_REGIME
)

fiat_debasement_paths = simulate_portfolio_paths(
    fiat_debasement_mean_returns, fiat_debasement_cov_matrix, weights
)

plot_simulation_results(fiat_debasement_paths, FIAT_DEBASEMENT_REGIME_NAME)

plot_correlation_heatmap(
    fiat_debasement_cov_matrix,
    FIAT_DEBASEMENT_REGIME_NAME,
)

plot_portfolio_pca_analysis(
    fiat_debasement_cov_matrix,
    FIAT_DEBASEMENT_REGIME_NAME,
)

# Geopolitical crisis regime: Simulates global conflict, equities/EM down, gold/energy up, higher volatility.
geopolitical_crisis_mean_returns, geopolitical_crisis_cov_matrix = (
    modify_portfolio_for_regime(
        historical_mean_returns,
        historical_cov_matrix,
        GEOPOLITICAL_CRISIS_REGIME,
    )
)

geopolitical_crisis_paths = simulate_portfolio_paths(
    geopolitical_crisis_mean_returns, geopolitical_crisis_cov_matrix, weights
)

plot_simulation_results(geopolitical_crisis_paths, GEOPOLITICAL_CRISIS_REGIME_NAME)

plot_correlation_heatmap(
    geopolitical_crisis_cov_matrix,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
)

plot_portfolio_pca_analysis(
    geopolitical_crisis_cov_matrix,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
)
