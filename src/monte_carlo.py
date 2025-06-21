import numpy as np


def simulate_daily_returns(mean_returns, cov_matrix, weights, size=252):
    """
    Simulate portfolio daily return samples using a multivariate normal distribution.

    Parameters:
        mean_returns (array-like): Mean daily returns for each asset.
        cov_matrix (2D array-like): Covariance matrix of asset returns.
        weights (array-like): Portfolio weights for each asset.
        size (int): Number of random samples to generate (default: 252).

    Returns:
        np.ndarray: Array of simulated portfolio daily returns, shape (size,).
    """
    samples = np.random.multivariate_normal(mean_returns, cov_matrix, size)
    portfolio_returns = np.dot(samples, weights)

    return portfolio_returns


def simulate_portfolio_paths(
    mean_returns,
    cov_matrix,
    weights,
    initial_value=10000,
    num_simulations=1000,
):
    """
    Simulate multiple portfolio value paths over time using Monte Carlo simulation.

    Parameters:
        mean_returns (array-like): Mean daily returns for each asset.
        cov_matrix (2D array-like): Covariance matrix of asset returns.
        weights (array-like): Portfolio weights for each asset.
        initial_value (float): Starting portfolio value (default: 10000).
        num_simulations (int): Number of simulation paths to generate (default: 1000).

    Returns:
        list: List of portfolio value paths, where each path is a list of daily values.
              Each simulation path starts with initial_value and shows portfolio value
              evolution over 252 trading days.
    """

    portfolio_paths = []
    for _ in range(num_simulations):
        simulated_daily_returns = simulate_daily_returns(
            mean_returns, cov_matrix, weights
        )

        portfolio_path = [initial_value]
        for day in range(len(simulated_daily_returns)):
            new_value = portfolio_path[-1] * (1 + simulated_daily_returns[day] / 100)
            portfolio_path.append(new_value)

        portfolio_paths.append(portfolio_path)

    return portfolio_paths
