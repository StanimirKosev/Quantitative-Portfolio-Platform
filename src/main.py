from portfolio import get_portfolio
from utils import fetch_close_prices

tickers, weights = get_portfolio()

close_values = fetch_close_prices(tickers)

print(close_values)







