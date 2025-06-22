def get_portfolio():
    tickers = ["BTC-EUR", "5MVW.DE", "SPYL.DE", "WMIN.DE", "IS3N.DE", "4GLD.DE"]
    weights = [0.6, 0.13, 0.105, 0.07, 0.06, 0.035]

    if len(tickers) != len(weights):
        raise ValueError("Tickers and weights must have the same length")

    # Check that weights sum to 1.0 within a small tolerance to avoid floating-point errors
    if abs(sum(weights) - 1.0) > 0.0001:
        raise ValueError("Weights must sum to 1.0")

    return (tickers, weights)


DOLLAR_DEBASEMENT_REGIME = {
    "BTC-EUR": 1.2,  # 20% higher - inflation hedge
    "4GLD.DE": 1.15,  # 15% higher - safe haven
    "5MVW.DE": 1.1,  # 10% higher - weak dollar helps
    "SPYL.DE": 0.9,  # 10% lower - higher rates hurt
    "WMIN.DE": 1.15,  # 15% higher - commodity boom
    "IS3N.DE": 1.1,  # 10% higher - weak dollar helps
}

GEOPOLITICAL_CRISIS_REGIME = {
    "BTC-EUR": 0.7,  # 30% lower - risk asset, underperforms
    "4GLD.DE": 1.3,  # 30% higher - safe haven, outperforms
    "5MVW.DE": 0.6,  # 40% lower - global stocks hurt
    "SPYL.DE": 0.5,  # 50% lower - US stocks hit hard
    "WMIN.DE": 0.8,  # 20% lower - commodity demand falls
    "IS3N.DE": 0.4,  # 60% lower - emerging markets hit hardest
}
