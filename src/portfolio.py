def get_portfolio():
    tickers = ["BTC-EUR", "5MVW.DE", "SPYL.DE", "WMIN.DE", "IS3N.DE", "4GLD.DE"]
    weights = [0.6, 0.13, 0.105, 0.07, 0.06, 0.035]

    if len(tickers) != len(weights):
        raise ValueError("Tickers and weights must have the same length")

    # Check that weights sum to 1.0 within a small tolerance to avoid floating-point errors
    if abs(sum(weights) - 1.0) > 0.0001:
        raise ValueError("Weights must sum to 1.0")

    return (tickers, weights)


FIAT_DEBASEMENT_REGIME = {
    "BTC-EUR": {"mean_factor": 1.3, "vol_factor": 1.1},  # BTC outperforms, stabilizes
    "4GLD.DE": {"mean_factor": 1.15, "vol_factor": 1.05},  # Gold up, less than BTC
    "5MVW.DE": {"mean_factor": 1.05, "vol_factor": 1.1},  # Energy mild outperformance
    "SPYL.DE": {"mean_factor": 1.1, "vol_factor": 1.0},  # S&P up, vol unchanged
    "WMIN.DE": {"mean_factor": 1.2, "vol_factor": 1.2},  # Miners up, more volatile
    "IS3N.DE": {"mean_factor": 1.1, "vol_factor": 1.15},  # EM modest outperformance
}

GEOPOLITICAL_CRISIS_REGIME = {
    "BTC-EUR": {"mean_factor": 0.85, "vol_factor": 1.7},  # Down, choppy, possible hedge
    "4GLD.DE": {"mean_factor": 1.10, "vol_factor": 1.2},  # Gold up, a bit choppier
    "5MVW.DE": {"mean_factor": 1.15, "vol_factor": 1.25},  # Energy up, choppier
    "SPYL.DE": {"mean_factor": 0.8, "vol_factor": 1.3},  # S&P down, choppier
    "WMIN.DE": {"mean_factor": 1.05, "vol_factor": 1.4},  # Miners up, riskier
    "IS3N.DE": {"mean_factor": 0.7, "vol_factor": 1.5},  # EM down, much choppier
}
