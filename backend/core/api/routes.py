from fastapi import APIRouter

from core.logging_config import log_info
from core.portfolio import get_portfolio
from core.utils import DEFAULT_PORTFOLIO_DATES
from core.api.models import (
    LogPayload,
    PortfolioDefaultResponse,
    PortfolioRequestPayload,
    RegimeParametersResponse,
    RegimesResponse,
    ValidationResponse,
)
from core.api.api_utils import (
    get_available_regimes,
    get_regime_parameters,
    validate_portfolio,
)

router = APIRouter(prefix="/api", tags=["core"])


@router.post("/logs")
async def receive_frontend_logs(log_data: LogPayload):
    log_info(
        f"Frontend: {log_data.event}",
        level=log_data.level,
        timestamp=log_data.timestamp,
        route=log_data.route,
        context=log_data.context,
    )
    return {"status": "logged"}


@router.get("/portfolio/default")
async def get_default_portfolio() -> PortfolioDefaultResponse:
    """
    Returns the default portfolio as a list of assets, each with ticker, weight_pct (percentage), and description, and the default date range for visualization.

    Response example:
    ```json
    {
      "success": true,
      "portfolio_assets": [
        {"ticker": "BTC-EUR", "weight_pct": 25.0, "description": "Bitcoin - Main hedge against fiat debasement"},
        ...
      ],
      "start_date": "2022-01-01",
      "end_date": "2024-12-31"
    }
    ```
    """
    tickers, weights = get_portfolio()

    descriptions = {
        "BTC-EUR": "Bitcoin - Main hedge against fiat debasement",
        "5MVW.DE": "Energy Sector - Global energy infrastructure",
        "SPYL.DE": "S&P 500 - US large-cap stocks",
        "WMIN.DE": "Global Miners - Commodity producers",
        "IS3N.DE": "Emerging Markets - High-growth economies",
        "4GLD.DE": "Gold - Traditional safe haven",
    }

    default_portfolio_assets = [
        {
            "ticker": ticker,
            "weight_pct": round(weight * 100, 2),
            "description": descriptions.get(ticker, ""),
        }
        for ticker, weight in zip(tickers, weights)
    ]

    return {
        "portfolio_assets": default_portfolio_assets,
        "start_date": DEFAULT_PORTFOLIO_DATES["start"],
        "end_date": DEFAULT_PORTFOLIO_DATES["end"],
    }


@router.post("/portfolio/validate")
async def validate_custom_portfolio(
    request: PortfolioRequestPayload,
) -> ValidationResponse:
    """
    Validates a custom portfolio's tickers and weights for a given date range.
    Expects:
      - tickers: List of asset ticker symbols (List[str])
      - weights: List of asset weights as fractions (List[float], must sum to 1.0)
      - start_date: Start date for historical data fetching (YYYY-MM-DD)
      - end_date: End date for historical data fetching (YYYY-MM-DD)
    Checks:
      - Tickers and weights are same length
      - Weights are numbers, non-negative, and sum to 1.0 (within tolerance)
      - No duplicate tickers
      - All tickers are fetchable (exist in yfinance) for the given date range

    Response example (valid):
    ```json
    { "success": true, "message": "Portfolio is valid." }
    ```
    Response example (invalid):
    ```json
    { "success": false, "errors": ["Weights must sum to 1.0.", "Ticker 'XYZ' is invalid."] }
    ```
    """
    return validate_portfolio(
        request.tickers,
        request.weights,
        request.regime_factors,
        request.start_date,
        request.end_date,
    )


@router.get("/regimes")
async def get_regimes() -> RegimesResponse:
    """
    Returns a list of available regimes, each with key, name, and description.

    Response example:
    ```json
    {
      "regimes": [
        {"key": "historical", "name": "Historical", "description": "Baseline: actual past returns and risk."},
        ...
      ]
    }
    ```
    """
    return get_available_regimes()


@router.get("/regimes/{regime}/parameters")
async def get_regime_parameters_endpoint(
    regime: str,
) -> RegimeParametersResponse:
    """
    Returns the regime modification parameters for the given regime.

    Response example:
    ```json
    {
      "regime": "fiat_debasement",
      "parameters": [
        {"ticker": "BTC-EUR", "mean_factor": 1.3, "vol_factor": 1.1, "correlation_move_pct": -0.15},
        {"ticker": "4GLD.DE", "mean_factor": 1.15, "vol_factor": 1.05, "correlation_move_pct": -0.15},
        ...
      ],
      "description": "Inflation: BTC & gold outperform, higher volatility. ..."
    }
    ```
    """
    return get_regime_parameters(regime)
