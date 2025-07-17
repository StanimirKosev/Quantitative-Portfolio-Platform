import sys

sys.path.append("./src")

from api.api_utils import (
    run_portfolio_simulation_api,
    get_available_regimes,
    validate_portfolio_api,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional


from portfolio import (
    get_portfolio,
)
from utils import fetch_close_prices, InvalidTickersException


app = FastAPI(title="Monte Carlo Portfolio Simulator API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    }


class CustomPortfolioRequest(BaseModel):
    tickers: List[str]
    weights: List[float]
    regime: Optional[str] = "historical"


@app.post("/api/simulate/custom")
async def simulate_custom_portfolio_regime(request: CustomPortfolioRequest):
    """
    Run a Monte Carlo simulation for a custom portfolio under a specified regime.

    Expects a JSON body with:
        - tickers: List of asset ticker symbols (List[str])
        - weights: List of asset weights in fractions
        - regime: Scenario name (str, e.g., "historical", "fiat_debasement", "geopolitical_crisis")

    Returns:
        dict: Contains success flag, regime name, and paths to generated chart images.

    Raises:
        HTTPException: If the regime name is invalid or required data is missing/invalid.
    """
    return run_portfolio_simulation_api(
        request.tickers, request.weights, request.regime
    )


@app.post("/api/simulate/{regime}")
async def simulate_default_portfolio_regime(regime: str):
    """
    Run a Monte Carlo simulation for the default portfolio under a specified regime.

    Args:
        regime (str): The scenario to simulate ("historical", "fiat_debasement", or "geopolitical_crisis").

    Returns:
        dict: Contains success flag, regime name, and paths to generated chart images.

    Raises:
        HTTPException: If the regime name is invalid or required data is missing/invalid.
    """
    tickers, weights = get_portfolio()
    return run_portfolio_simulation_api(tickers, weights, regime)


@app.post("/api/portfolio/validate")
async def validate_custom_portfolio(request: CustomPortfolioRequest):
    """
    Validates a custom portfolio's tickers and weights.
    Expects:
      - tickers: List of asset ticker symbols (List[str])
      - weights: List of asset weights as fractions (List[float], must sum to 1.0)
    Checks:
      - Tickers and weights are same length
      - Weights are numbers, non-negative, and sum to 1.0 (within tolerance)
      - No duplicate tickers
      - All tickers are fetchable (exist in yfinance)
    Returns:
      - dict: {"success": True, "message": ...} if valid
      - dict: {"success": False, "errors": [...]} if invalid
    """
    return validate_portfolio_api(request.tickers, request.weights)


@app.get("/api/regimes")
async def get_regimes():
    """
    Returns a list of available regimes, each with key, name, and description.
    Useful for populating regime selectors in the frontend.
    """
    return {"regimes": get_available_regimes()}
