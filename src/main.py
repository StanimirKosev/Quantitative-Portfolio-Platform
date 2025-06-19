from portfolio import get_portfolio
from utils import fetch_close_prices, transform_to_daily_returns_percent

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

daily_returns = transform_to_daily_returns_percent(close_values)

print(daily_returns)




