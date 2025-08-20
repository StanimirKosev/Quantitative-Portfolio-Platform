from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from optimization.api.models import (
    OptimizationRequestPayload,
    PortfolioOptimizationResponse,
)
from optimization.api.api_utils import (
    broadcaster,
    create_progress_callback,
    optimize_portfolio_api,
)

from core.portfolio import get_portfolio
import asyncio


router = APIRouter(prefix="/api/optimize", tags=["optimization"])


@router.websocket("/ws/progress")
async def websocket_progress_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for optimization progress updates.
    Connect here to receive live progress during efficient frontier calculations.
    """
    await broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)


@router.post("/custom")
async def optimize_custom_portfolio_regime(
    request: OptimizationRequestPayload,
) -> PortfolioOptimizationResponse:
    """
    Run portfolio optimization for a custom portfolio under a specified regime.

    Calculates efficient frontier and maximum Sharpe ratio portfolio for custom asset
    allocation and regime parameters. Returns complete optimization analysis.

    Expects a JSON body with:
      - tickers: List of asset ticker symbols (List[str])
      - regime: Scenario name (str, e.g., "historical", "fiat_debasement", "geopolitical_crisis")
      - regime_factors: (optional) Custom regime parameters (RegimeFactors)
      - start_date: (optional) Start date for historical data fetching (YYYY-MM-DD)
      - end_date: (optional) End date for historical data fetching (YYYY-MM-DD)

    Response includes:
      - frontier_points: Array of optimal portfolios across risk-return spectrum
      - max_sharpe_point: Single portfolio with maximum risk-adjusted return
      - risk_free_rate: Current Treasury rate used in Sharpe calculations
    """
    regime = "custom"
    progress = create_progress_callback()

    # Move CPU-intensive math to background thread, keep main event loop responsive
    return await asyncio.to_thread(
        optimize_portfolio_api,
        request.tickers,
        regime,
        request.regime_factors,
        request.start_date,
        request.end_date,
        progress,
    )


@router.post("/{regime}")
async def optimize_default_portfolio_regime(
    regime: str,
) -> PortfolioOptimizationResponse:
    """
    Run portfolio optimization for the default portfolio under a specified regime.

    Calculates efficient frontier and maximum Sharpe ratio portfolio for the default
    6-asset portfolio under different economic scenarios.

    Args:
      regime (str): The scenario to optimize for ("historical", "fiat_debasement", or "geopolitical_crisis").

    Response includes:
      - frontier_points: Array of optimal portfolios across risk-return spectrum
      - max_sharpe_point: Single portfolio with maximum risk-adjusted return
      - risk_free_rate: Current Treasury rate used in Sharpe calculations
    """
    tickers, _ = get_portfolio()
    progress = create_progress_callback()

    # Move CPU-intensive math to background thread, keep main event loop responsive
    return await asyncio.to_thread(
        optimize_portfolio_api,
        tickers=tickers,
        regime=regime,
        progress_callback=progress,
    )
