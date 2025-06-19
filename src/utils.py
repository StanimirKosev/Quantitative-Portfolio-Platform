import yfinance as yf


def fetch_close_prices(tickers, start="2022-01-01", end="2024-12-31"):
    """
    Fetches daily closing prices for specified tickers within a date range using yfinance.

    Parameters:
        tickers (list or str): List of ticker symbols or a single ticker symbol.
        start (str): Start date in 'YYYY-MM-DD' format. Default is '2022-01-01'.
        end (str): End date in 'YYYY-MM-DD' format. Default is '2024-12-31'.

    Returns:
        pd.DataFrame or None: DataFrame of closing prices (dates as index, tickers as columns),
                              or None if data is unavailable.
    """
    data = None

    try:
        data = yf.download(tickers, start=start, end=end)
    except Exception as e:
        print(f"Error downloading data: {e}")

    if data is None or data.empty or "Close" not in data:
        return None

    return data["Close"]


def transform_to_daily_returns_percent(close_prices):
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

    daily_returns = close_prices.pct_change().dropna()

    return daily_returns * 100


def calculate_mean_and_covariance(daily_returns):
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
