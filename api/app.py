import sys

sys.path.append("./src")

from api.api_utils import (
    run_portfolio_simulation_api,
    get_available_regimes,
    validate_portfolio,
    get_regime_parameters,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional


from portfolio import (
    get_portfolio,
)
from utils import DEFAULT_PORTFOLIO_DATES


app = FastAPI(title="Monte Carlo Portfolio Simulator API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/charts", StaticFiles(directory="charts"), name="charts")


@app.get("/")
async def root():
    return {"message": "API running"}


@app.get("/api/portfolio/default")
async def get_default_portfolio():
    """
    Returns the default portfolio as a list of assets, each with ticker, weight_pct (percentage), and description, and the default date range for visualization.

    Response example:
    ```json
    {
      "success": true,
      "default_portfolio_assets": [
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
        "success": True,
        "default_portfolio_assets": default_portfolio_assets,
        "start_date": DEFAULT_PORTFOLIO_DATES["start"],
        "end_date": DEFAULT_PORTFOLIO_DATES["end"],
    }


class CustomPortfolioRequest(BaseModel):
    tickers: List[str]
    weights: List[float]
    regime: Optional[str] = "historical"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@app.post("/api/simulate/custom")
async def simulate_custom_portfolio_regime(request: CustomPortfolioRequest):
    """
    Run a Monte Carlo simulation for a custom portfolio under a specified regime.

    Expects a JSON body with:
      - tickers: List of asset ticker symbols (List[str])
      - weights: List of asset weights in fractions
      - regime: Scenario name (str, e.g., "historical", "fiat_debasement", "geopolitical_crisis")
      - start_date: (optional) Start date for historical data fetching (YYYY-MM-DD)
      - end_date: (optional) End date for historical data fetching (YYYY-MM-DD)

    Response example:
    ```json
    {
      "success": true,
      "regime": "Fiat Debasement",
      "charts": {
        "simulation_chart_path": "/charts/fiat_debasement/monte_carlo_simulation_fiat_debasement.png",
        "correlation_matrix_chart_path": "/charts/fiat_debasement/correlation_matrix_fiat_debasement.png",
        "risk_factors_chart_path": "/charts/fiat_debasement/risk_factor_analysis_fiat_debasement.png"
      }
    }
    ```
    """
    return run_portfolio_simulation_api(
        request.tickers,
        request.weights,
        request.regime,
        start_date=request.start_date,
        end_date=request.end_date,
    )


@app.post("/api/simulate/{regime}")
async def simulate_default_portfolio_regime(regime: str):
    """
    Run a Monte Carlo simulation for the default portfolio under a specified regime.

    Args:
      regime (str): The scenario to simulate ("historical", "fiat_debasement", or "geopolitical_crisis").

    Response example:
    ```json
    {
      "success": true,
      "regime": "Historical",
      "charts": {
        "simulation_chart_path": "/charts/historical/monte_carlo_simulation_historical.png",
        "correlation_matrix_chart_path": "/charts/historical/correlation_matrix_historical.png",
        "risk_factors_chart_path": "/charts/historical/risk_factor_analysis_historical.png"
      }
    }
    ```
    """
    tickers, weights = get_portfolio()
    return run_portfolio_simulation_api(tickers, weights, regime)


@app.post("/api/portfolio/validate")
async def validate_custom_portfolio(request: CustomPortfolioRequest):
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
        request.tickers, request.weights, request.start_date, request.end_date
    )


@app.get("/api/regimes")
async def get_regimes():
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


@app.get("/api/regimes/{regime}/parameters")
async def get_regime_parameters_endpoint(regime: str):
    """
    Returns the regime modification parameters for the given regime.

    Response example:
    ```json
    {
      "regime": "fiat_debasement",
      "parameters": {
        "BTC-EUR": {"mean_factor": 1.3, "vol_factor": 1.1},
        ...
        "correlation_move_pct": -0.15
      },
      "description": "Inflation: BTC & gold outperform, higher volatility. ..."
    }
    ```
    """
    return get_regime_parameters(regime)
