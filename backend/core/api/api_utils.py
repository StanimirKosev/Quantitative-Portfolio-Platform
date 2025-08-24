from typing import List, Optional, Tuple
import asyncio
import json
import yfinance as yf
from fastapi import WebSocket, WebSocketDisconnect
from core.portfolio import (
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
    get_portfolio,
)
from core.utils import (
    HISTORICAL,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    FIAT_DEBASEMENT_REGIME_NAME,
    calculate_mean_and_covariance,
    get_cached_prices,
    InvalidTickersException,
    transform_to_daily_returns,
)
from fastapi import HTTPException
from datetime import datetime
from core.logging_config import log_info, log_error
from core.api.models import (
    RegimeParametersResponse,
    RegimesResponse,
    StockQuote,
    ValidationResponse,
    RegimeFactors,
)
import pandas as pd


def get_available_regimes() -> RegimesResponse:
    """
    Returns a list of available regimes, each with key and name.
    """
    regimes = [
        {
            "key": "historical",
            "name": HISTORICAL,
        },
        {
            "key": "fiat_debasement",
            "name": FIAT_DEBASEMENT_REGIME_NAME,
        },
        {
            "key": "geopolitical_crisis",
            "name": GEOPOLITICAL_CRISIS_REGIME_NAME,
        },
    ]
    return {"regimes": regimes}


def validate_portfolio(
    tickers: List[str],
    weights: List[float],
    regime_factors: Optional[RegimeFactors],
    start_date: Optional[str],
    end_date: Optional[str],
) -> ValidationResponse:
    """
    Internal utility for validating a custom portfolio's tickers and weights for a given date range.
    Used by the /api/portfolio/validate endpoint.

    Returns:
      - dict: {"success": True, "message": ...} if valid
      - dict: {"success": False, "errors": [...]} if invalid
    """
    log_info(
        "Portfolio validation started",
        ticker=tickers,
    )

    errors = []
    # 1. Length match
    if len(tickers) != len(weights):
        errors.append("Tickers and weights must have the same length.")

    # 2. No empty tickers
    if any(not t or not isinstance(t, str) or not t.strip() for t in tickers):
        errors.append("All tickers must be non-empty strings.")

    # 3. Weights: numbers, non-negative, sum to 1.0
    if not all(isinstance(w, (int, float)) for w in weights):
        errors.append("All weights must be numbers.")
    if not all(w >= 0 for w in weights):
        errors.append("All weights must be non-negative.")
    if not all(w > 0 for w in weights):
        errors.append("All weights must be greater than zero.")
    if abs(sum(weights) - 1.0) > 0.0001:
        errors.append("Weights must sum to 100%.")

    # 4. No duplicate tickers
    if len(set(tickers)) != len(tickers):
        errors.append("Duplicate tickers are not allowed.")

    # 5. Date validation (only if previous checks passed)
    if not errors:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            today = datetime.now().date()

            if start > end:
                errors.append("Start date must be before or equal to end date.")
            # Add future date validation
            if start.date() > today:
                errors.append("Start date cannot be in the future.")

            if end.date() > today:
                errors.append("End date cannot be in the future.")

        except Exception:
            errors.append("Dates must be in YYYY-MM-DD format.")

    # 6. Validate regime factors
    if regime_factors is not None and not errors:

        correlation_move_pct = regime_factors.get("correlation_move_pct")
        if correlation_move_pct is None:
            errors.append("Correlation move is required when using power user mode.")
        elif abs(correlation_move_pct) >= 1.0:
            errors.append("Correlation move must be between -0.99 and 0.99.")

        for ticker, factor_dict in regime_factors.items():
            if ticker == "correlation_move_pct":
                continue

            mean_factor = factor_dict.get("mean_factor")
            vol_factor = factor_dict.get("vol_factor")

            if mean_factor is None:
                errors.append(f"{ticker}: Mean factor is required.")

            if vol_factor is None:
                errors.append(f"{ticker}: Vol factor is required.")
            elif vol_factor <= 0:
                errors.append(f"{ticker}: Vol factor must be positive.")

    # 7. All tickers fetchable for the given date range (only if no regime test errors)
    if not errors:
        try:
            tickers_key = ",".join(tickers)
            get_cached_prices(tickers_key, start_date, end_date)
        except InvalidTickersException as e:
            errors.append(str(e))

    if errors:
        log_error(
            "Portfolio validation failed",
            error_count=len(errors),
            errors=errors,
            tickers=tickers,
        )
        return {"success": False, "errors": errors}

    log_info("Portfolio validation successful", tickers=tickers)
    return {"success": True, "message": "Portfolio is valid."}


def get_regime_parameters(
    regime_key: str,
) -> RegimeParametersResponse:
    """
    Returns the regime modification parameters for a given regime.
    The returned object has the following structure:
    {
        "regime": <regime_name>,
        "parameters": [
            {"ticker": <str>, "mean_factor": <float>, "vol_factor": <float>, "correlation_move_pct": <float>},
            ...
        ],
        "description": <str>
    }
    For 'historical', all mean/vol factors are 1.0 and correlation_move_pct is 0.0 for each asset.
    """
    tickers, _ = get_portfolio()

    def parameters_dict_to_array(params):
        params = dict(params)
        corr = params.pop("correlation_move_pct", None)
        return [
            {
                "ticker": ticker,
                **factors,
                "correlation_move_pct": corr,
            }
            for ticker, factors in params.items()
        ]

    regime_map = {
        "historical": {
            "regime": HISTORICAL,
            "parameters": [
                {
                    "ticker": ticker,
                    "mean_factor": 1.0,
                    "vol_factor": 1.0,
                    "correlation_move_pct": 0.0,
                }
                for ticker in tickers
            ],
            "description": "Baseline: actual past returns, volatility, and correlations. No regime modification is applied. All mean and volatility factors are 1.0, and correlation move is 0.0.",
        },
        "fiat_debasement": {
            "regime": FIAT_DEBASEMENT_REGIME_NAME,
            "description": "Fiat debasement: BTC & gold outperform, higher volatility. Mean/volatility factors rise for hard assets; equities/EM up moderately. Correlation move is negative (-0.15), reflecting risk-on dispersion.",
            "parameters": parameters_dict_to_array(FIAT_DEBASEMENT_REGIME),
        },
        "geopolitical_crisis": {
            "regime": GEOPOLITICAL_CRISIS_REGIME_NAME,
            "description": "Geopolitical crisis: Equities/EM down, gold & energy up, all more volatile. Mean factors drop for risk assets, rise for havens. Correlation move is positive (+0.1), showing risk-off co-movement.",
            "parameters": parameters_dict_to_array(GEOPOLITICAL_CRISIS_REGIME),
        },
    }

    regime_key = regime_key.strip().lower().replace(" ", "_")

    if regime_key not in regime_map:
        raise HTTPException(status_code=404, detail=f"Regime '{regime_key}' not found.")

    return regime_map[regime_key]


def resolve_regime(
    regime: str, regime_factors: Optional[RegimeFactors]
) -> Tuple[str, str, Optional[RegimeFactors]]:
    """
    Normalize a regime string and return (regime_key, regime_name, regime_dict).
    - 'custom' uses the provided regime_factors as its dict (can be None).
    """
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
    return regime_key, regime_name, regime_dict


def prepare_market_data(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    """
    Fetch close prices, compute daily returns, and compute mean + sample/shrunk covariance.
    Returns: (daily_returns, mean_returns, cov_sample, cov_shrunk)
    """
    try:
        tickers_key = ",".join(tickers)
        close_values = get_cached_prices(tickers_key, start_date, end_date)
    except InvalidTickersException as e:
        raise HTTPException(status_code=400, detail=str(e))

    daily_returns = transform_to_daily_returns(close_values)
    mean_returns, cov_sample, cov_shrunk = calculate_mean_and_covariance(daily_returns)
    return daily_returns, mean_returns, cov_sample, cov_shrunk


class LivePriceStreamer:
    """
    Streams live price updates from Yahoo Finance to the frontend via WebSocket.

    - On client connection, subscribes to the default portfolio tickers.
    - Forwards real-time price updates from Yahoo Finance to the frontend.
    - Listens for subscription change messages from the frontend (custom tickers).
    - Updates Yahoo Finance subscriptions accordingly and continues streaming.
    - Handles client disconnects and errors gracefully.
    """

    def __init__(self, websocket: WebSocket):
        self.fastapi_websocket = websocket
        self.current_tickers, _ = get_portfolio()

    async def start(self):
        """Main entry point - handles everything."""

        await self.fastapi_websocket.accept()
        log_info(f"Live price client connected: {self.current_tickers}")

        try:
            async with yf.AsyncWebSocket(verbose=False) as yf_websocket:

                await yf_websocket.subscribe(self.current_tickers)

                # Listen to Yahoo finance for updates
                yf_task = asyncio.create_task(
                    yf_websocket.listen(self._forward_to_frontend)
                )

                # Listen for frontend subscription changes
                while True:
                    try:
                        data = await self.fastapi_websocket.receive_text()
                        custom_tickers: List[str] = json.loads(data)

                        yf_websocket, yf_task = await self._update_subscription(
                            yf_websocket, yf_task, custom_tickers
                        )

                    except WebSocketDisconnect:
                        log_info("Live price client disconnected")
                        break

                yf_task.cancel()

        except Exception as e:
            log_error(f"Live price stream error: {str(e)}")

    def _forward_to_frontend(self, yahoo_message: StockQuote):
        """
        Forwards a Yahoo Finance message to the frontend WebSocket client.
        """
        asyncio.create_task(self.fastapi_websocket.send_text(json.dumps(yahoo_message)))

    async def _update_subscription(
        self,
        yf_websocket: yf.AsyncWebSocket,
        yf_task: asyncio.Task[None],
        custom_tickers: List[str],
    ) -> tuple[yf.AsyncWebSocket, asyncio.Task[None]]:
        """
        Updates the Yahoo Finance subscription to a new set of tickers
        when the frontend requests a portfolio change.
        """
        # Skip if subscription unchanged (critical for performance)
        if set(custom_tickers) == set(self.current_tickers):
            log_info(f"Subscription unchanged: {custom_tickers}")
            return yf_websocket, yf_task

        # Create fresh connection to avoid corrupted state after changes
        yf_task.cancel()
        await yf_websocket.close()

        # Create fresh WebSocket connection
        new_yf_websocket = yf.AsyncWebSocket(verbose=False)
        await new_yf_websocket.subscribe(custom_tickers)

        # Update current state to new subscription
        self.current_tickers = custom_tickers

        new_task = asyncio.create_task(
            new_yf_websocket.listen(self._forward_to_frontend)
        )
        return new_yf_websocket, new_task
