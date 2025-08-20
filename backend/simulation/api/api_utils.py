from typing import List, Optional
from core.portfolio import (
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
)
from core.utils import (
    HISTORICAL,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    FIAT_DEBASEMENT_REGIME_NAME,
    calculate_mean_and_covariance,
    get_cached_prices,
    transform_to_daily_returns,
    InvalidTickersException,
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
from fastapi import HTTPException
from core.logging_config import log_info
from simulation.api.models import SimulationChartsResponse
from core.api.api_utils import RegimeFactors


def run_portfolio_simulation_api(
    tickers: List[str],
    weights: List[float],
    regime: str,
    regime_factors: Optional[RegimeFactors] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> SimulationChartsResponse:
    """
    Orchestrates the full Monte Carlo simulation and chart generation for a given portfolio and regime.

    This function is designed for use by API endpoints. It handles regime normalization, data fetching,
    transformation, regime modification, simulation, and chart generation. It returns a minimal response
    dictionary suitable for frontend consumption.

    Parameters:
        tickers (List[str]): List of asset ticker symbols.
        weights (List[float]): List of asset weights (fractions, should sum to 1.0).
        regime (str): The scenario to simulate (e.g., "historical", "fiat_debasement", "geopolitical_crisis").
        regime_factors (RegimeFactors, optional): Custom regime parameters with factors dict and correlation_move_pct.
        start_date (str, optional): Start date for historical data fetching (YYYY-MM-DD).
        end_date (str, optional): End date for historical data fetching (YYYY-MM-DD).

    Returns:
        dict: paths to generated chart images.

    Raises:
        HTTPException: If the regime name is invalid or if any required data is missing or invalid.
    """
    log_info(
        "Portfolio simulation started",
        ticker=tickers,
        regime=regime,
        date_range=f"{start_date} to {end_date}",
    )

    regime_key = regime.strip().lower().replace(" ", "_")

    regime_map = {
        "historical": (HISTORICAL, None),
        "fiat_debasement": (FIAT_DEBASEMENT_REGIME_NAME, FIAT_DEBASEMENT_REGIME),
        "geopolitical_crisis": (
            GEOPOLITICAL_CRISIS_REGIME_NAME,
            GEOPOLITICAL_CRISIS_REGIME,
        ),
        "custom": ("Custom", regime_factors),
    }
    if regime_key not in regime_map:
        raise HTTPException(status_code=400, detail=f"Invalid regime name: {regime}")

    regime_name, regime_dict = regime_map[regime_key]

    try:
        tickers_key = ','.join(tickers)
        close_values = get_cached_prices(tickers_key, start_date, end_date)
    except InvalidTickersException as e:
        raise HTTPException(status_code=400, detail=str(e))

    daily_returns = transform_to_daily_returns(close_values)
    historical_mean_returns, historical_cov_matrix, _ = calculate_mean_and_covariance(
        daily_returns
    )

    if regime_key == "historical":
        mean_returns, cov_matrix = historical_mean_returns, historical_cov_matrix
    else:
        mean_returns, cov_matrix = modify_portfolio_for_regime(
            historical_mean_returns, historical_cov_matrix, regime_dict
        )

    paths = simulate_portfolio_paths(mean_returns, cov_matrix, weights)

    sim_chart_path = plot_simulation_results(paths, regime_name, show=False)
    corr_chart_path = plot_correlation_heatmap(cov_matrix, regime_name, show=False)
    risk_chart_path = plot_portfolio_pca_analysis(cov_matrix, regime_name, show=False)

    log_info("Charts generated successfully", regime=regime_name, chart_count=3)

    return {
        "simulation_chart_path": sim_chart_path,
        "correlation_matrix_chart_path": corr_chart_path,
        "risk_factors_chart_path": risk_chart_path,
    }
