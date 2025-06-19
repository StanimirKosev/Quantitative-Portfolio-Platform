import numpy as np


def generate_sample(mean_returns, cov_matrix, weights, size=10000):
    """
    Generate random portfolio return samples using a multivariate normal distribution.

    Parameters:
        mean_returns (array-like): Mean daily returns for each asset.
        cov_matrix (2D array-like): Covariance matrix of asset returns.
        weights (array-like): Portfolio weights for each asset.
        size (int): Number of random samples to generate (default: 10000).

    Returns:
        np.ndarray: Array of simulated portfolio returns, shape (size,).
    """
    np.random.seed(42)
    samples = np.random.multivariate_normal(mean_returns, cov_matrix, size)
    portfolio_returns = np.dot(samples, weights)

    return portfolio_returns
