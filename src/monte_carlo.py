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


def calculate_risk_metrics(portfolio_paths):
    """
    Calculate professional risk metrics from Monte Carlo simulation results.

    Parameters:
        portfolio_paths (list): List of portfolio value paths.
        initial_value (float): Initial portfolio value for percentage calculations.

    Returns:
        dict: Dictionary containing risk metrics with euro amounts and percentages.
    """

    final_values = [path[-1] for path in portfolio_paths]

    # Value at Risk
    var_95 = np.percentile(final_values, 5)
    var_99 = np.percentile(final_values, 1)

    # Conditional Value at Risk
    cvar_95 = np.mean([v for v in final_values if v <= var_95])
    cvar_99 = np.mean([v for v in final_values if v <= var_99])

    initial_value = portfolio_paths[0][0]
    var_95_pct = ((var_95 / initial_value) - 1) * 100
    var_99_pct = ((var_99 / initial_value) - 1) * 100
    cvar_95_pct = ((cvar_95 / initial_value) - 1) * 100
    cvar_99_pct = ((cvar_99 / initial_value) - 1) * 100

    return {
        "var_95": var_95,
        "var_99": var_99,
        "cvar_95": cvar_95,
        "cvar_99": cvar_99,
        "var_95_pct": var_95_pct,
        "var_99_pct": var_99_pct,
        "cvar_95_pct": cvar_95_pct,
        "cvar_99_pct": cvar_99_pct,
    }


def calculate_simulation_statistics(portfolio_paths):
    """
    Calculate comprehensive statistics and metrics from Monte Carlo simulation results.

    This function extracts all the calculations currently done in the visualization
    function, making the code more modular and testable.

    Parameters:
        portfolio_paths (list): List of portfolio value paths.

    Returns:
        dict: Dictionary containing all simulation statistics including:
            - percentiles: 5th, 10th, 25th, 50th, 75th, 90th, 95th percentiles
            - path_indices: indices of median, best, and worst paths
            - final_values: final portfolio values for all paths
            - performance_stats: mean, median, best, worst final values and returns
    """
    portfolio_paths = np.array(portfolio_paths)

    # Calculate percentiles across all paths for each time step
    percentiles = np.percentile(portfolio_paths, [5, 10, 25, 50, 75, 90, 95], axis=0)

    # Get final values and find key paths
    final_values = [path[-1] for path in portfolio_paths]
    median_final = np.median(final_values)
    best_final = np.max(final_values)
    worst_final = np.min(final_values)

    # Find indices of key paths
    median_path_idx = np.argmin(
        [abs(path[-1] - median_final) for path in portfolio_paths]
    )
    best_path_idx = np.argmax(final_values)
    worst_path_idx = np.argmin(final_values)

    # Calculate performance statistics
    initial_value = portfolio_paths[0][0]
    mean_final = np.mean(final_values)

    mean_return_pct = ((mean_final / initial_value) - 1) * 100
    best_return_pct = ((best_final / initial_value) - 1) * 100
    worst_return_pct = ((worst_final / initial_value) - 1) * 100
    median_return_pct = ((median_final / initial_value) - 1) * 100

    return {
        "percentiles": percentiles,
        "path_indices": {
            "median": median_path_idx,
            "best": best_path_idx,
            "worst": worst_path_idx,
        },
        "final_values": final_values,
        "performance_stats": {
            "initial_value": initial_value,
            "mean_final": mean_final,
            "median_final": median_final,
            "best_final": best_final,
            "worst_final": worst_final,
            "mean_return_pct": mean_return_pct,
            "median_return_pct": median_return_pct,
            "best_return_pct": best_return_pct,
            "worst_return_pct": worst_return_pct,
        },
    }


def modify_returns_for_regime(mean_returns, tickers, asset_factors):
    """
    Modify mean returns based on macroeconomic regime factors.

    Args:
        mean_returns: Historical mean returns for each asset
        tickers: List of asset tickers
        asset_factors: Dictionary of factors for each asset with "name" key

    Returns:
        tuple: (modified_returns, regime_name)
    """
    if asset_factors is None:
        return

    modified_returns = mean_returns.copy()

    for i, ticker in enumerate(tickers):
        if ticker in asset_factors:
            modified_returns[i] *= asset_factors[ticker]

    return modified_returns


def get_cov_matrix_analysis(cov_matrix):
    """
    Return the principal components of a covariance matrix for portfolio risk analysis and visualization.
    Returns eigenvalues, explained variance ratios, eigenvectors, and asset names (tickers).
    """
    asset_tickers = list(cov_matrix.columns)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix.values)

    # Sort eigenvalues and eigenvectors from largest to smallest
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    total_variance = sum(eigenvalues)
    explained_variance_ratio = [eigval / total_variance for eigval in eigenvalues]

    condition_number = max(eigenvalues) / min(eigenvalues)

    # We return the eigenvalues, explained variance, eigenvectors, and asset names.
    # This lets us understand and visualize the main risk factors in the portfolio.
    # Each principal component (PC) is a 6D vector (for 6 assets), showing how much each asset contributes to that risk factor.
    # PC1 is the eigenvector with the highest risk (largest variance explained).
    return {
        "eigenvalues": eigenvalues,
        "explained_variance_ratio": explained_variance_ratio,
        "eigenvectors": eigenvectors,
        "asset_tickers": asset_tickers,
        "condition_number": condition_number,
    }
