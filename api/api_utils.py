from portfolio import GEOPOLITICAL_CRISIS_REGIME, FIAT_DEBASEMENT_REGIME, get_portfolio
from utils import (
    HISTORICAL,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    FIAT_DEBASEMENT_REGIME_NAME,
    calculate_mean_and_covariance,
    fetch_close_prices,
    transform_to_daily_returns_percent,
    InvalidTickersException,
)
from monte_carlo import simulate_portfolio_paths, modify_portfolio_for_regime
from visualization import (
    plot_correlation_heatmap,
    plot_portfolio_pca_analysis,
    plot_simulation_results,
)
from fastapi import HTTPException
from datetime import datetime


def get_available_regimes():
    """
    Returns a list of available regimes, each with key, name, and description.
    """
    regimes = [
        {
            "key": "historical",
            "name": HISTORICAL,
            "description": "Baseline: actual past returns and risk.",
        },
        {
            "key": "fiat_debasement",
            "name": FIAT_DEBASEMENT_REGIME_NAME,
            "description": "Inflation: BTC & gold outperform, higher volatility.",
        },
        {
            "key": "geopolitical_crisis",
            "name": GEOPOLITICAL_CRISIS_REGIME_NAME,
            "description": "Crisis: Equities/EM down, gold & energy up, risk-off.",
        },
    ]
    return {"regimes": regimes}


def run_portfolio_simulation_api(
    tickers, weights, regime, start_date=None, end_date=None
):
    """
    Orchestrates the full Monte Carlo simulation and chart generation for a given portfolio and regime.

    This function is designed for use by API endpoints. It handles regime normalization, data fetching,
    transformation, regime modification, simulation, and chart generation. It returns a minimal response
    dictionary suitable for frontend consumption.

    Parameters:
        tickers (List[str]): List of asset ticker symbols.
        weights (List[float]): List of asset weights (fractions, should sum to 1.0).
        regime (str): The scenario to simulate (e.g., "historical", "fiat_debasement", "geopolitical_crisis").
        start_date (str, optional): Start date for historical data fetching (YYYY-MM-DD).
        end_date (str, optional): End date for historical data fetching (YYYY-MM-DD).

    Returns:
        dict: Contains success flag, regime name, and paths to generated chart images.

    Raises:
        HTTPException: If the regime name is invalid or if any required data is missing or invalid.
    """

    regime_key = regime.strip().lower().replace(" ", "_")

    regime_map = {
        "historical": (HISTORICAL, None),
        "fiat_debasement": (FIAT_DEBASEMENT_REGIME_NAME, FIAT_DEBASEMENT_REGIME),
        "geopolitical_crisis": (
            GEOPOLITICAL_CRISIS_REGIME_NAME,
            GEOPOLITICAL_CRISIS_REGIME,
        ),
    }
    if regime_key not in regime_map:
        raise HTTPException(status_code=400, detail=f"Invalid regime name: {regime}")

    regime_name, regime_dict = regime_map[regime_key]

    try:
        close_values = fetch_close_prices(tickers, start=start_date, end=end_date)
    except InvalidTickersException as e:
        raise HTTPException(status_code=400, detail=str(e))

    daily_returns = transform_to_daily_returns_percent(close_values)
    historical_mean_returns, historical_cov_matrix = calculate_mean_and_covariance(
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

    return {
        "success": True,
        "regime": regime_name,
        "charts": {
            "simulation_chart_path": sim_chart_path,
            "correlation_matrix_chart_path": corr_chart_path,
            "risk_factors_chart_path": risk_chart_path,
        },
    }


def validate_portfolio(tickers, weights, start_date, end_date):
    """
    Internal utility for validating a custom portfolio's tickers and weights for a given date range.
    Used by the /api/portfolio/validate endpoint.

    Returns:
      - dict: {"success": True, "message": ...} if valid
      - dict: {"success": False, "errors": [...]} if invalid
    """

    errors = []
    # 1. Length match
    if len(tickers) != len(weights):
        errors.append("Tickers and weights must have the same length.")

    # 2. Weights: numbers, non-negative, sum to 1.0
    if not all(isinstance(w, (int, float)) for w in weights):
        errors.append("All weights must be numbers.")
    if not all(w >= 0 for w in weights):
        errors.append("All weights must be non-negative.")
    if abs(sum(weights) - 1.0) > 0.0001:
        errors.append("Weights must sum to 100.")

    # 3. No duplicate tickers
    if len(set(tickers)) != len(tickers):
        errors.append("Duplicate tickers are not allowed.")

    # 4. Date validation (only if previous checks passed)
    if not errors:

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                errors.append("Start date must be before or equal to end date.")
        except Exception:
            errors.append("Dates must be in YYYY-MM-DD format.")

    # 5. All tickers fetchable for the given date range
    if not errors:
        try:
            fetch_close_prices(tickers, start=start_date, end=end_date)
        except InvalidTickersException as e:
            errors.append(str(e))

    if errors:
        return {"success": False, "errors": errors}
    return {"success": True, "message": "Portfolio is valid."}


def get_regime_parameters(regime_key):
    """
    Returns the regime modification parameters for a given regime.
    The returned object matches the structure of the regime dicts defined in portfolio.py (a dict of tickers mapping to {mean_factor, vol_factor}, plus 'correlation_move_pct'), with an added 'description' field.
    For 'historical', all mean/vol factors are 1.0 and correlation_move_pct is 0.0.
    """
    tickers, _ = get_portfolio()

    regime_map = {
        "historical": {
            "regime": HISTORICAL,
            "parameters": {
                **{
                    ticker: {"mean_factor": 1.0, "vol_factor": 1.0}
                    for ticker in tickers
                },
                "correlation_move_pct": 0.0,
            },
            "description": "Baseline: actual past returns and risk. No regime modification is applied. All mean and volatility factors are 1.0, and correlation move is 0.0.",
        },
        "fiat_debasement": {
            "regime": FIAT_DEBASEMENT_REGIME_NAME,
            "description": "Inflation: BTC & gold outperform, higher volatility. Regime modifies mean and volatility factors for each asset, and correlation move is negative (risk-on).",
            "parameters": FIAT_DEBASEMENT_REGIME,
        },
        "geopolitical_crisis": {
            "regime": GEOPOLITICAL_CRISIS_REGIME_NAME,
            "description": "Crisis: Equities/EM down, gold & energy up, risk-off. Regime modifies mean and volatility factors for each asset, and correlation move is positive (risk-off).",
            "parameters": GEOPOLITICAL_CRISIS_REGIME,
        },
    }

    regime_key = regime_key.strip().lower().replace(" ", "_")

    if regime_key not in regime_map:
        raise HTTPException(status_code=404, detail=f"Regime '{regime_key}' not found.")

    return regime_map[regime_key]
