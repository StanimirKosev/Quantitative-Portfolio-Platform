import sys

sys.path.append("../src")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portfolio import get_portfolio
from utils import (
    fetch_close_prices,
    transform_to_daily_returns_percent,
    calculate_mean_and_covariance,
)


app = FastAPI(title="Monte Carlo Portfolio Simulator API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "API running"}


@app.get("/api/portfolio/default")
async def get_default_portfolio():
    tickers, weights = get_portfolio()
    return {
        "tickers": tickers,
        "weights": weights,
    }
