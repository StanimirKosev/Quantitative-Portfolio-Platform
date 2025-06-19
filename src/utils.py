import yfinance as yf

def fetch_close_prices(tickers, start="2022-01-01", end="2024-12-31"):
    """
    Fetch closing prices for given tickers and date range using yfinance.
    Returns a DataFrame of closing prices, or None if data is unavailable.
    """
    data = None

    try:
        data = yf.download(tickers, start=start, end=end)
    except Exception as e:
        print(f"Error downloading data: {e}")
    
    if data is None or data.empty or 'Close' not in data:
        return None
   
    return data['Close']