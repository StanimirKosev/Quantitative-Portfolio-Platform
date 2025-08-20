from typing import List, Optional
from core.portfolio import (
    GEOPOLITICAL_CRISIS_REGIME,
    FIAT_DEBASEMENT_REGIME,
    get_portfolio,
)
from core.utils import (
    HISTORICAL,
    GEOPOLITICAL_CRISIS_REGIME_NAME,
    FIAT_DEBASEMENT_REGIME_NAME,
    get_cached_prices,
    InvalidTickersException,
)
from fastapi import HTTPException
from datetime import datetime
from core.logging_config import log_info, log_error
from core.api.models import (
    RegimeParametersResponse,
    RegimesResponse,
    ValidationResponse,
    RegimeFactors,
)


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
            tickers_key = ','.join(tickers)
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
