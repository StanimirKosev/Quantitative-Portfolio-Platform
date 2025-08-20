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
    fetch_close_prices,
    transform_to_daily_returns,
    InvalidTickersException,
)
from simulation.engine.monte_carlo import modify_portfolio_for_regime
from optimization.engine.markowitz import (
    calculate_efficient_frontier,
    maximize_sharpe_portfolio,
)
from fastapi import HTTPException
from core.logging_config import log_error, log_info
from optimization.api.models import PortfolioOptimizationResponse
from core.api.api_utils import RegimeFactors


def optimize_portfolio_api(
    tickers: List[str],
    regime: str,
    regime_factors: Optional[RegimeFactors] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> PortfolioOptimizationResponse:
    """
    Calculate optimal portfolios using modern portfolio theory for a given regime scenario.

    Performs comprehensive portfolio optimization including efficient frontier calculation
    and maximum Sharpe ratio optimization. Applies regime-specific adjustments to model
    different economic scenarios (inflation, geopolitical crisis, etc.).

    The function fetches historical data, applies regime modifications to returns and
    covariance, then solves multiple optimization problems to generate the efficient
    frontier and identify the portfolio with the best risk-adjusted return.

    Parameters:
        tickers (List[str]): Asset ticker symbols (e.g., ["BTC-EUR", "SPYL.DE"]).
        regime (str): Economic scenario ("historical", "fiat_debasement", "geopolitical_crisis", "custom").
        regime_factors (RegimeFactors, optional): Custom factors for mean/volatility adjustments and correlations.
        start_date (str, optional): Start date for price data in YYYY-MM-DD format.
        end_date (str, optional): End date for price data in YYYY-MM-DD format.

    Returns:
        PortfolioOptimizationResponse: Contains efficient frontier points, maximum Sharpe portfolio,
                                     and risk-free rate used in calculations.

    Raises:
        HTTPException: If regime is invalid, tickers are invalid, or optimization fails.
    """
    log_info(
        "Portfolio optimization started",
        tickers=tickers,
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
        close_values = fetch_close_prices(tickers, start=start_date, end=end_date)
    except InvalidTickersException as e:
        raise HTTPException(status_code=400, detail=str(e))

    daily_returns = transform_to_daily_returns(close_values)
    historical_mean_returns, _, historical_shrunk_cov = calculate_mean_and_covariance(
        daily_returns
    )

    # Apply regime modifications if needed
    if regime_key == "historical":
        mean_returns, cov_matrix = historical_mean_returns, historical_shrunk_cov
    else:
        mean_returns, cov_matrix = modify_portfolio_for_regime(
            historical_mean_returns, historical_shrunk_cov, regime_dict
        )

    # Calculate efficient frontier and max Sharpe portfolio
    try:
        efficient_frontier = calculate_efficient_frontier(mean_returns, cov_matrix)
        max_sharpe_portfolio = maximize_sharpe_portfolio(mean_returns, cov_matrix)
    except Exception as e:
        msg = f"Optimization failed: {str(e)}. Try with different assets or date range."
        log_error(msg)
        raise HTTPException(
            status_code=500,
            detail=msg,
        )

    log_info(
        "Portfolio optimization completed",
        regime=regime_name,
        frontier_points=len(efficient_frontier),
        max_sharpe_ratio=max_sharpe_portfolio["sharpe_ratio"],
    )

    return PortfolioOptimizationResponse(
        frontier_points=[
            {
                "return_pct": round(point["return"] * 100, 1),
                "volatility_pct": round(point["volatility"] * 100, 1),
                "weights_pct": [round(w * 100, 1) for w in point["weights"].tolist()],
            }
            for point in efficient_frontier
        ],
        max_sharpe_point={
            "sharpe_ratio": round(max_sharpe_portfolio["sharpe_ratio"], 2),
            "return_pct": round(max_sharpe_portfolio["return"] * 100, 1),
            "volatility_pct": round(max_sharpe_portfolio["volatility"] * 100, 1),
            "weights_pct": [
                round(w * 100, 1) for w in max_sharpe_portfolio["weights"].tolist()
            ],
        },
        risk_free_rate_pct=round(max_sharpe_portfolio["risk_free_rate"] * 100, 1),
    )
