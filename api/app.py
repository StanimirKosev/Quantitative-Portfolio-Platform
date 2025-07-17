import sys

sys.path.append("./src")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from portfolio import (
    get_portfolio,
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
)
from utils import (
    HISTORICAL,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    FIAT_DEBASEMENT_REGIME_NAME,
    calculate_mean_and_covariance,
    fetch_close_prices,
    transform_to_daily_returns_percent,
)
from monte_carlo import (
    simulate_portfolio_paths,
    modify_portfolio_for_regime,
)
from visualization import (
    plot_correlation_heatmap,
    plot_portfolio_pca_analysis,
    plot_simulation_results,
)


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


@app.post("/api/simulate/{regime}")
async def simulate_default_portfolio_regime(regime: str):
    """
    Run a Monte Carlo simulation for the default portfolio under a given regime.

    Args:
        regime (str): The scenario to simulate ("historical", "fiat_debasement", or "geopolitical_crisis").

    Returns:
        dict: Success flag, regime name, and paths to generated chart images.
    """
    # Normalize input
    regime_key = regime.strip().lower().replace(" ", "_")

    # Map normalized input to internal regime constants/names
    regime_map = {
        "historical": (HISTORICAL, None),
        "fiat_debasement": (FIAT_DEBASEMENT_REGIME_NAME, FIAT_DEBASEMENT_REGIME),
        "geopolitical_crisis": (
            GEOPOLITICAL_CRISIS_REGIME_NAME,
            GEOPOLITICAL_CRISIS_REGIME,
        ),
    }

    if regime_key not in regime_map:
        return {"error": "Invalid regime name"}, 400

    regime_name, regime_dict = regime_map[regime_key]

    tickers, weights = get_portfolio()
    close_values = fetch_close_prices(tickers)
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
