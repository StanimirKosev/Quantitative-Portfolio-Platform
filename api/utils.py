import yfinance as yf
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Union

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

    # yfinance now defaults auto_adjust=True (adjusted prices). Set explicitly for clarity and to silence FutureWarning.
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)

    if data is None or data.empty or "Close" not in data:
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
        raise InvalidTickersException(
            f"Could not fetch valid price data for tickers: {', '.join(invalid_tickers)}.",
            invalid_tickers=invalid_tickers,
        )

    return close


def transform_to_daily_returns_percent(close_prices: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a DataFrame of closing prices to daily returns in percent.

    Parameters:
        close_prices (pd.DataFrame): DataFrame of asset closing prices, indexed by date.

    Returns:
        pd.DataFrame: DataFrame of daily returns (percentage change), indexed by date.
                      Returns None if input is None.
    """

    if close_prices is None:
        return None

    # Set fill_method=None to avoid FutureWarning and ensure no forward-filling of missing values.
    daily_returns = close_prices.pct_change(fill_method=None).dropna()

    return daily_returns * 100


def calculate_mean_and_covariance(
    daily_returns: pd.DataFrame,
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Calculate the mean daily returns and covariance matrix for a set of assets.

    Parameters:
        daily_returns (pd.DataFrame): DataFrame of daily returns (percentage change) for each asset,
                                      indexed by date.

    Returns:
        tuple:
            - mean_returns (pd.Series): Mean daily return for each asset.
            - cov_matrix (pd.DataFrame): Covariance matrix of daily returns between assets.
    """
    mean_returns = daily_returns.mean()
    cov_matrix = daily_returns.cov()
    return mean_returns, cov_matrix


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
    folder = f"charts/{scenario}"
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{scenario}.png"
    full_path = os.path.join(folder, filename)
    plt.savefig(full_path, dpi=300, bbox_inches="tight")
    # Normalize to URL format
    url_path = "/" + full_path.replace("\\", "/")
    return url_path


def get_regime_display_suffix(regime_name: str) -> str:
    """Returns a formatted suffix for regime name display, excluding 'Custom'."""
    return f" - {regime_name}" if (regime_name and regime_name != "Custom") else ""
