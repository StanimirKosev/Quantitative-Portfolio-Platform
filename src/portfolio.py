def get_portfolio():
    tickers = ['BTC-EUR', '5MVW.DE', 'SPYL.DE', 'WMIN.DE', 'IS3ND.XD', 'XAUT-USD']
    weights = [0.6, 0.13, 0.105, 0.07, 0.06, 0.035]

    if len(tickers) != len(weights):
        raise ValueError("Tickers and weights must have the same length")

    # Check that weights sum to 1.0 within a small tolerance to avoid floating-point errors
    if abs(sum(weights) - 1.0) > 0.0001:
        raise ValueError("Weights must sum to 1.0")

    return (tickers, weights)



