import yfinance as yf
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Union
from core.logging_config import log_info, log_error

HISTORICAL = "Historical"
GEOPOLITICAL_CRISIS_REGIME_NAME = "Geopolitical Crisis"
FIAT_DEBASEMENT_REGIME_NAME = "Fiat Debasement"

DEFAULT_PORTFOLIO_DATES = {"start": "2022-01-01", "end": "2024-12-31"}


class InvalidTickersException(Exception):
    def __init__(self, message: str, invalid_tickers: Optional[List[str]] = None):
        super().__init__(message)
        self.invalid_tickers = invalid_tickers


def fetch_close_prices(
    tickers: Union[List[str], str],
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Fetches daily closing prices for specified tickers within a date range using yfinance.

    Parameters:
        tickers (list): List of ticker symbols or a single ticker symbol.
        start (str): Start date in 'YYYY-MM-DD' format. Default is '2022-01-01'.
        end (str): End date in 'YYYY-MM-DD' format. Default is '2024-12-31'.

    Returns:
        pd.DataFrame or None: DataFrame of closing prices (dates as index, tickers as columns),
                              or None if data is unavailable.
    """

    if start is None or end is None:
        start = DEFAULT_PORTFOLIO_DATES["start"]
        end = DEFAULT_PORTFOLIO_DATES["end"]

    log_info(
        "Fetching price data from Yahoo Finance",
        tickers=tickers[:3] if isinstance(tickers, list) else [tickers],
        date_range=f"{start} to {end}",
    )

    # yfinance now defaults auto_adjust=True (adjusted prices). Set explicitly for clarity and to silence FutureWarning.
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)

    if data is None or data.empty or "Close" not in data:
        log_error(
            "Yahoo Finance returned no data",
            tickers=tickers,
            error="Empty response or missing Close column",
        )
        raise InvalidTickersException(
            f"Could not fetch price data for tickers: {tickers}.",
            invalid_tickers=tickers,
        )

    close = data["Close"]

    invalid_tickers = []
    for t in tickers:
        # Ticker column is missing OR the entire column is NaN
        if t not in close.columns or close[t].isnull().all():
            invalid_tickers.append(t)

    if invalid_tickers:
        log_error(
            "Invalid tickers detected",
            invalid_tickers=invalid_tickers,
            valid_tickers=[t for t in tickers if t not in invalid_tickers],
        )
        raise InvalidTickersException(
            f"Could not fetch valid price data for tickers: {', '.join(invalid_tickers)}.",
            invalid_tickers=invalid_tickers,
        )

    log_info(
        "Price data fetched successfully",
        num_tickers=len(close.columns),
        data_points=len(close),
        tickers=list(close.columns)[:3],
    )

    return close


def transform_to_daily_returns(
    close_prices: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """
    Convert a DataFrame of closing prices to daily returns.

    Parameters:
        close_prices (pd.DataFrame): DataFrame of asset closing prices, indexed by date.

    Returns:
        pd.DataFrame: DataFrame of daily returns (decimal fraction), indexed by date.
                      Returns None if input is None.
    """

    if close_prices is None:
        return None

    # Set fill_method=None to avoid FutureWarning and ensure no forward-filling of missing values.
    daily_returns = close_prices.pct_change(fill_method=None).dropna()

    return daily_returns


def calculate_mean_and_covariance(
    daily_returns: pd.DataFrame,
) -> Tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    """
    Calculate mean daily returns, sample covariance, and shrunk covariance matrix.

    Parameters:
        daily_returns (pd.DataFrame): DataFrame of daily returns (percentage change) for each asset,
                                      indexed by date.

    Returns:
        tuple:
            - mean_returns (pd.Series): Mean daily return for each asset.
            - cov_matrix (pd.DataFrame): Sample covariance matrix of daily returns between assets.
            - shrunk_cov_matrix (pd.DataFrame): Shrunk covariance matrix with improved numerical stability.
    """
    mean_returns = daily_returns.mean()
    cov_matrix = daily_returns.cov()
    shrunk_cov_matrix = shrink_covariance(daily_returns)
    return mean_returns, cov_matrix, shrunk_cov_matrix


def shrink_covariance(
    daily_returns: pd.DataFrame, shrinkage_intensity: float = None
) -> pd.DataFrame:
    """
    Apply simple shrinkage to covariance matrix for improved numerical stability.

    Shrinkage reduces estimation error by pulling the sample covariance toward
    a structured target (identity matrix). This prevents optimization failures
    by making the matrix better conditioned.

    Parameters:
        daily_returns: DataFrame of daily returns for each asset
        shrinkage_intensity: Shrinkage intensity [0,1]. If None, auto-estimated.

    Returns:
        Shrunk covariance matrix with improved numerical properties
    """
    if daily_returns.empty or len(daily_returns) < 2:
        return daily_returns.cov()

    # Sample covariance matrix
    sample_cov = daily_returns.cov()
    n_assets = len(sample_cov)
    n_obs = len(daily_returns)

    # Target: identity matrix scaled by average variance
    avg_variance = np.trace(sample_cov) / n_assets
    target = avg_variance * np.eye(n_assets)

    # Auto-estimate shrinkage intensity
    if shrinkage_intensity is None:
        shrinkage_intensity = min(0.3, max(0.1, n_assets / n_obs))

    # Apply shrinkage: λ * target + (1-λ) * sample
    shrunk_matrix = (
        shrinkage_intensity * target + (1 - shrinkage_intensity) * sample_cov.values
    )

    return pd.DataFrame(
        shrunk_matrix, index=sample_cov.index, columns=sample_cov.columns
    )


def save_figure(regime_name: str, prefix: str) -> str:
    """
    Save the current matplotlib figure to the scenario-specific charts folder.

    The function normalizes the scenario name, creates the folder if it doesn't exist,
    and saves the current matplotlib figure with a consistent naming scheme:
    charts/{scenario}/{prefix}_{scenario}.{ext}

    Args:
        regime_name (str): Scenario name (e.g., 'historical', 'fiat_debasement', ...)
        prefix (str): File prefix (e.g., 'monte_carlo_simulation', 'correlation_matrix')
        ext (str): File extension (e.g., 'png', 'csv')

    Returns:
        str: URL-style path to the saved figure.
    """
    scenario = str(regime_name).replace(" ", "_").lower()
    folder = f"simulation/charts/{scenario}"
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{scenario}.png"
    full_path = os.path.join(folder, filename)
    plt.savefig(full_path, dpi=300, bbox_inches="tight")
    # Return URL path fr FastAPI static mount (strip simulation/ prefix)
    url_path = f"/charts/{scenario}/{filename}"
    return url_path


def get_regime_display_suffix(regime_name: str) -> str:
    """Returns a formatted suffix for regime name display, excluding 'Custom'."""
    return f" - {regime_name}" if (regime_name and regime_name != "Custom") else ""
