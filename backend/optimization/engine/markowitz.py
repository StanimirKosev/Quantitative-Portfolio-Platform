import numpy as np
import cvxpy as cp
import pandas as pd
from typing import Tuple, List, Dict, Union
from core.logging_config import log_info, log_error


def calculate_portfolio_metrics(
    weights: Union[np.ndarray, list], mean_returns: pd.Series, cov_matrix: pd.DataFrame
) -> Tuple[float, float]:
    """
    Calculate annualized portfolio return and risk from daily data.

    Parameters:
        weights (array-like): Portfolio weights for each asset (must sum to 1.0)
        mean_returns (array-like): Mean daily returns for each asset
        cov_matrix (array-like): Daily covariance matrix between assets

    Returns:
        tuple: (annualized_return, annualized_volatility)
            - annualized_return: Expected yearly return as decimal (0.12 = 12%)
            - annualized_volatility: Yearly standard deviation as decimal (0.15 = 15%)
    """
    weights = np.array(weights)

    # Portfolio daily return: weighted average of asset returns
    portfolio_daily_return = np.sum(mean_returns * weights)

    # Annualize: 252 trading days per year
    annualized_return = portfolio_daily_return * 252

    # Portfolio daily variance: w^T * Cov * w (matrix multiplication)
    portfolio_daily_variance = np.dot(weights.T, np.dot(cov_matrix, weights))

    # Portfolio daily volatility: square root of variance
    portfolio_daily_volatility = np.sqrt(portfolio_daily_variance)

    # Annualize volatility: multiply by sqrt(252) because volatility scales with sqrt(time)
    annualized_volatility = portfolio_daily_volatility * np.sqrt(252)

    return annualized_return, annualized_volatility


def calculate_efficient_frontier(
    mean_returns: pd.Series, cov_matrix: pd.DataFrame, num_points: int = 25
) -> List[Dict[str, Union[float, np.ndarray]]]:
    """
    Calculate efficient frontier with multiple optimal portfolios across risk-return spectrum.

    For each target return level, finds the minimum variance portfolio that achieves that return.
    Creates the classic efficient frontier curve for portfolio optimization visualization.

    Parameters:
        mean_returns (pd.Series): Mean daily returns for each asset
        cov_matrix (pd.DataFrame): Daily covariance matrix between assets
        num_points (int): Number of portfolios along efficient frontier (default: 25)

    Returns:
        List[Dict]: List of portfolio dictionaries, each containing:
            - 'return': Annualized expected return (decimal, e.g. 0.12 = 12%)
            - 'volatility': Annualized volatility/risk (decimal, e.g. 0.15 = 15%)
            - 'weights': Optimal portfolio weights (numpy array summing to 1.0)

    Raises:
        ValueError: If no feasible portfolios can be found or input data is invalid
    """
    min_return = mean_returns.min()
    max_return = mean_returns.max()
    target_returns = np.linspace(min_return, max_return, num_points)

    efficient_frontier = []
    failed_points = 0

    # Create optimization variables for portfolio weights (one per asset)
    weights = cp.Variable(len(mean_returns))

    log_info(
        "Starting efficient frontier calculation",
        num_assets=len(mean_returns),
        num_points=num_points,
        return_range=f"{min_return:.4f} to {max_return:.4f}"
    )

    for target_return in target_returns:

        constraints = [
            cp.sum(weights) == 1,  # Budget constraint: must invest 100% of capital
            weights >= 0,  # Long-only: no short selling (negative positions)
            mean_returns.values @ weights
            == target_return,  # Return constraint: achieve specific return
        ]

        objective = cp.Minimize(cp.quad_form(weights, cov_matrix.values))
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.OSQP, max_iter=5000, time_limit=10)

        if problem.status not in ["optimal", "optimal_inaccurate"]:
            failed_points += 1
            continue

        optimal_weights = weights.value

        portfolio_return, portfolio_volatility = calculate_portfolio_metrics(
            optimal_weights, mean_returns, cov_matrix
        )

        efficient_frontier.append(
            {
                "return": portfolio_return,
                "volatility": portfolio_volatility,
                "weights": optimal_weights.copy(),
            }
        )

    # Enhanced error handling with detailed feedback
    if not efficient_frontier:
        error_msg = "No feasible portfolios found for efficient frontier. "
        if failed_points > 0:
            error_msg += f"Failed to solve {failed_points} out of {num_points} optimization points. "

        error_msg += (
            "This usually means your portfolio cannot be optimized with the given assets and date range. "
            "Try using different assets or selecting a shorter time period with more stable data."
        )
        log_error(
            "Efficient frontier calculation failed",
            failed_points=failed_points,
            total_points=num_points,
            num_assets=len(mean_returns)
        )
        raise ValueError(error_msg)

    log_info(
        "Efficient frontier calculated successfully",
        successful_points=len(efficient_frontier),
        total_points=num_points,
        failed_points=failed_points,
        success_rate=f"{len(efficient_frontier)/num_points*100:.1f}%"
    )

    return efficient_frontier


def maximize_sharpe_portfolio(
    mean_returns: pd.Series, cov_matrix: pd.DataFrame, risk_free_rate: float = 0.02
) -> Union[Dict[str, Union[float, np.ndarray]], None]:
    """
    Find portfolio with maximum Sharpe ratio using convex optimization.

    Instead of optimizing the non-convex ratio directly, transforms the problem:
    - Fix excess return = 1, minimize variance
    - Use auxiliary variable κ to handle budget constraint
    - Normalize final weights: w_optimal = w_solution / κ_solution

    Parameters:
        mean_returns: Daily expected returns for each asset
        cov_matrix: Daily covariance matrix between assets
        risk_free_rate: Annual risk-free rate, typically 10-year Treasury yield (default: 2%)

    Returns:
        dict: Portfolio with 'return', 'volatility', 'weights', 'sharpe_ratio'
        None: If optimization fails
    """

    log_info(
        "Starting maximum Sharpe ratio optimization",
        num_assets=len(mean_returns),
        risk_free_rate=f"{risk_free_rate*100:.1f}%"
    )

    daily_risk_free_rate = risk_free_rate / 252

    # Optimization variables
    kappa = cp.Variable()  # auxiliary variable for normalization trick
    weights = cp.Variable(len(mean_returns))

    constraints = [
        mean_returns.values @ weights - daily_risk_free_rate
        == 1,  # fix excess return = 1
        cp.sum(weights) == kappa,  # budget constraint with auxiliary variable
        weights >= 0,  # long-only (no short selling)
    ]

    # Minimize portfolio variance
    objective = cp.Minimize(cp.quad_form(weights, cov_matrix.values))
    problem = cp.Problem(objective, constraints)

    # Solve with timeout and clear error handling
    problem.solve(solver=cp.OSQP, max_iter=5000, time_limit=30)

    if problem.status != "optimal":
        log_error(
            "Maximum Sharpe ratio optimization failed",
            solver_status=problem.status,
            num_assets=len(mean_returns),
            risk_free_rate=f"{risk_free_rate*100:.1f}%"
        )
        if problem.status == "infeasible":
            raise ValueError(
                "Cannot find portfolio with maximum Sharpe ratio. "
                "This usually means your assets have very poor risk-adjusted returns. "
                "Try including better-performing assets."
            )
        elif problem.status == "unbounded":
            raise ValueError(
                "Portfolio optimization is unbounded. "
                "This indicates numerical issues with your covariance matrix. "
                "Check for assets with zero or negative variance."
            )
        else:
            raise ValueError(
                f"Portfolio optimization failed ({problem.status}). "
                "Try with different assets or check your data quality."
            )

    # Normalize weights to sum to 1.0
    optimal_weights = weights.value / kappa.value

    portfolio_return, portfolio_volatility = calculate_portfolio_metrics(
        optimal_weights, mean_returns, cov_matrix
    )

    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

    log_info(
        "Maximum Sharpe ratio optimization completed successfully",
        portfolio_return=f"{portfolio_return*100:.2f}%",
        portfolio_volatility=f"{portfolio_volatility*100:.2f}%",
        sharpe_ratio=f"{sharpe_ratio:.3f}",
        max_weight=f"{np.max(optimal_weights)*100:.1f}%"
    )

    return {
        "return": portfolio_return,
        "volatility": portfolio_volatility,
        "weights": optimal_weights,
        "sharpe_ratio": sharpe_ratio,
    }
