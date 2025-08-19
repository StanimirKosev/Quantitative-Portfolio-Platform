from fastapi import APIRouter

from core.portfolio import get_portfolio
from simulation.api.utils import run_portfolio_simulation_api
from simulation.api.models import SimulationChartsResponse
from core.api.models import PortfolioRequestPayload

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


@router.post("/custom")
async def simulate_custom_portfolio_regime(
    request: PortfolioRequestPayload,
) -> SimulationChartsResponse:
    """
    Run a Monte Carlo simulation for a custom portfolio under a specified regime.

    Expects a JSON body with:
      - tickers: List of asset ticker symbols (List[str])
      - weights: List of asset weights in fractions
      - regime: Scenario name (str, e.g., "historical", "fiat_debasement", "geopolitical_crisis")
      - regime_factors: (optional) Custom regime parameters (RegimeFactors)
        - factors: Dict mapping ticker to {"mean_factor": float, "vol_factor": float}
        - correlation_move_pct: Global correlation adjustment (float)
      - start_date: (optional) Start date for historical data fetching (YYYY-MM-DD)
      - end_date: (optional) End date for historical data fetching (YYYY-MM-DD)

    Response example:
    ```json
    {
      "simulation_chart_path": "/charts/fiat_debasement/monte_carlo_simulation_fiat_debasement.png",
      "correlation_matrix_chart_path": "/charts/fiat_debasement/correlation_matrix_fiat_debasement.png",
      "risk_factors_chart_path": "/charts/fiat_debasement/risk_factor_analysis_fiat_debasement.png"
    }
    ```
    """
    regime = "custom"
    return run_portfolio_simulation_api(
        request.tickers,
        request.weights,
        regime,
        request.regime_factors,
        start_date=request.start_date,
        end_date=request.end_date,
    )


@router.post("/{regime}")
async def simulate_default_portfolio_regime(regime: str) -> SimulationChartsResponse:
    """
    Run a Monte Carlo simulation for the default portfolio under a specified regime.

    Args:
      regime (str): The scenario to simulate ("historical", "fiat_debasement", or "geopolitical_crisis").

    Response example:
    ```json
    {
      "simulation_chart_path": "/charts/historical/monte_carlo_simulation_historical.png",
      "correlation_matrix_chart_path": "/charts/historical/correlation_matrix_historical.png",
      "risk_factors_chart_path": "/charts/historical/risk_factor_analysis_historical.png"
    }
    ```
    """
    tickers, weights = get_portfolio()
    return run_portfolio_simulation_api(tickers, weights, regime)
