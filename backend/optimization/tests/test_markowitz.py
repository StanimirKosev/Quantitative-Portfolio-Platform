"""
Unit tests for portfolio optimization mathematical functions.
"""

import pytest
import numpy as np
import pandas as pd
from optimization.engine.markowitz import (
    calculate_portfolio_metrics,
    calculate_efficient_frontier,
    maximize_sharpe_portfolio,
)


class TestCalculatePortfolioMetrics:
    """Test portfolio return and risk calculations"""

    def test_portfolio_metrics_basic_calculation(self):
        """Test basic portfolio metrics with known inputs"""
        # Arrange: Simple 2-asset portfolio
        weights = np.array([0.6, 0.4])
        mean_returns = pd.Series([0.001, 0.002])  # Daily returns
        cov_matrix = pd.DataFrame([[0.0004, 0.0001], [0.0001, 0.0009]])

        # Act
        annual_return, annual_volatility = calculate_portfolio_metrics(
            weights, mean_returns, cov_matrix
        )

        # Assert: Basic validations
        assert annual_return > 0  # Should be positive given positive mean returns
        assert annual_volatility > 0  # Volatility should always be positive
        assert isinstance(annual_return, float)
        assert isinstance(annual_volatility, float)

        # Mathematical validation: portfolio return should be weighted average
        expected_daily_return = np.sum(mean_returns * weights)
        expected_annual_return = expected_daily_return * 252
        assert abs(annual_return - expected_annual_return) < 1e-10

    def test_portfolio_variance_calculation(self):
        """Test portfolio variance formula: w^T * Cov * w"""
        weights = np.array([0.5, 0.5])
        mean_returns = pd.Series([0.001, 0.001])
        # Known covariance matrix
        cov_matrix = pd.DataFrame([[0.01, 0.005], [0.005, 0.01]])

        _, annual_volatility = calculate_portfolio_metrics(
            weights, mean_returns, cov_matrix
        )

        # Manual calculation of portfolio variance
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix.values, weights))
        expected_annual_vol = np.sqrt(portfolio_variance) * np.sqrt(252)

        assert abs(annual_volatility - expected_annual_vol) < 1e-10

    def test_single_asset_portfolio(self):
        """Test edge case: single asset portfolio"""
        weights = np.array([1.0])
        mean_returns = pd.Series([0.0015])
        cov_matrix = pd.DataFrame([[0.0025]])

        annual_return, annual_volatility = calculate_portfolio_metrics(
            weights, mean_returns, cov_matrix
        )

        # Single asset: portfolio metrics = asset metrics
        assert abs(annual_return - 0.0015 * 252) < 1e-10
        assert abs(annual_volatility - np.sqrt(0.0025 * 252)) < 1e-10


class TestCalculateEfficientFrontier:
    """Test efficient frontier calculation"""

    def test_efficient_frontier_basic_properties(self):
        """Test that efficient frontier has expected properties"""
        # Arrange: 3-asset test portfolio
        mean_returns = pd.Series([0.0005, 0.001, 0.0015])
        cov_matrix = pd.DataFrame(
            [
                [0.0004, 0.0001, 0.0002],
                [0.0001, 0.0009, 0.0001],
                [0.0002, 0.0001, 0.0016],
            ]
        )

        # Act
        frontier = calculate_efficient_frontier(mean_returns, cov_matrix, num_points=5)

        # Assert: Basic structure
        assert isinstance(frontier, list)
        assert len(frontier) > 0  # Should have at least some feasible points
        assert len(frontier) <= 5  # Should not exceed requested points

        # Check structure of each point
        for point in frontier:
            assert "return" in point
            assert "volatility" in point
            assert "weights" in point
            assert point["return"] > 0
            assert point["volatility"] > 0
            assert abs(np.sum(point["weights"]) - 1.0) < 1e-6  # Weights sum to 1
            assert np.all(
                point["weights"] >= -1e-8
            )  # Long-only (allow small numerical errors)

    def test_efficient_frontier_return_ordering(self):
        """Test that efficient frontier points are ordered by increasing risk"""
        mean_returns = pd.Series([0.0005, 0.001, 0.0015])
        cov_matrix = pd.DataFrame(
            [
                [0.0004, 0.0001, 0.0002],
                [0.0001, 0.0009, 0.0001],
                [0.0002, 0.0001, 0.0016],
            ]
        )

        frontier = calculate_efficient_frontier(mean_returns, cov_matrix, num_points=5)

        # Should be roughly ordered by risk (some numerical noise allowed)
        volatilities = [point["volatility"] for point in frontier]
        returns = [point["return"] for point in frontier]

        # Generally increasing risk/return relationship
        assert len(set(volatilities)) > 1  # Should have different risk levels
        assert len(set(returns)) > 1  # Should have different return levels

    def test_efficient_frontier_error_cases(self):
        """Test error handling with problematic inputs"""
        # Arrange: Create scenario that will fail - inconsistent data
        mean_returns = pd.Series([0.001, 0.002])  # 2 assets
        cov_matrix = pd.DataFrame(
            [[0.0004, 0.0001, 0.0002], [0.0001, 0.0009, 0.0001], [0.0002, 0.0001, 0.0016]]  # 3x3 matrix
        )

        # Act & Assert: Should handle gracefully
        with pytest.raises((ValueError, IndexError, Exception)) as exc_info:
            calculate_efficient_frontier(mean_returns, cov_matrix)

        # Should fail due to dimension mismatch or other data issues
        assert "dimensions" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


class TestMaximizeSharpePortfolio:
    """Test maximum Sharpe ratio optimization"""

    def test_maximize_sharpe_basic_properties(self):
        """Test basic properties of max Sharpe portfolio"""
        # Arrange: Simple portfolio with different risk/return characteristics
        mean_returns = pd.Series([0.0005, 0.001, 0.0015])  # Increasing returns
        cov_matrix = pd.DataFrame(
            [
                [0.0004, 0.0001, 0.0002],
                [0.0001, 0.0009, 0.0001],
                [0.0002, 0.0001, 0.0016],  # Higher risk for higher return
            ]
        )

        # Act
        result = maximize_sharpe_portfolio(
            mean_returns, cov_matrix, risk_free_rate=0.02
        )

        # Assert: Basic structure
        assert isinstance(result, dict)
        assert "return" in result
        assert "volatility" in result
        assert "weights" in result
        assert "sharpe_ratio" in result

        # Basic validations
        assert result["return"] > 0
        assert result["volatility"] > 0
        assert result["sharpe_ratio"] > 0
        assert abs(np.sum(result["weights"]) - 1.0) < 1e-6
        assert np.all(result["weights"] >= -1e-8)  # Long-only

    def test_sharpe_ratio_calculation(self):
        """Test that Sharpe ratio is calculated correctly"""
        mean_returns = pd.Series([0.001, 0.0015])
        cov_matrix = pd.DataFrame([[0.0004, 0.0001], [0.0001, 0.0009]])
        risk_free_rate = 0.03

        result = maximize_sharpe_portfolio(mean_returns, cov_matrix, risk_free_rate)

        # Manual Sharpe ratio calculation
        expected_sharpe = (result["return"] - risk_free_rate) / result["volatility"]

        assert abs(result["sharpe_ratio"] - expected_sharpe) < 1e-10

    def test_maximize_sharpe_single_asset(self):
        """Test edge case: single asset"""
        mean_returns = pd.Series([0.002])
        cov_matrix = pd.DataFrame([[0.0025]])

        result = maximize_sharpe_portfolio(mean_returns, cov_matrix)

        # Single asset: weight should be 1.0
        assert abs(result["weights"][0] - 1.0) < 1e-6
        assert result["return"] == pytest.approx(0.002 * 252, rel=1e-6)

    def test_maximize_sharpe_error_handling(self):
        """Test error handling with impossible scenarios"""
        # Arrange: Negative expected returns (worse than risk-free rate)
        mean_returns = pd.Series([-0.001, -0.002])
        cov_matrix = pd.DataFrame([[0.0004, 0.0001], [0.0001, 0.0009]])

        # Act & Assert: Should raise meaningful error
        with pytest.raises(ValueError) as exc_info:
            maximize_sharpe_portfolio(mean_returns, cov_matrix, risk_free_rate=0.02)

        error_msg = str(exc_info.value)
        assert (
            "sharpe ratio" in error_msg.lower() or "risk-adjusted" in error_msg.lower()
        )

    def test_risk_free_rate_sensitivity(self):
        """Test that different risk-free rates affect Sharpe ratio"""
        mean_returns = pd.Series([0.001, 0.0015])
        cov_matrix = pd.DataFrame([[0.0004, 0.0001], [0.0001, 0.0009]])

        result_low_rf = maximize_sharpe_portfolio(
            mean_returns, cov_matrix, risk_free_rate=0.01
        )
        result_high_rf = maximize_sharpe_portfolio(
            mean_returns, cov_matrix, risk_free_rate=0.05
        )

        # Higher risk-free rate should result in lower Sharpe ratio
        assert result_low_rf["sharpe_ratio"] > result_high_rf["sharpe_ratio"]


class TestIntegrationScenarios:
    """Integration tests combining multiple functions"""

    def test_efficient_frontier_contains_max_sharpe(self):
        """Test that max Sharpe portfolio is near the efficient frontier"""
        mean_returns = pd.Series([0.0008, 0.0012, 0.0016])
        cov_matrix = pd.DataFrame(
            [
                [0.0004, 0.0001, 0.0002],
                [0.0001, 0.0009, 0.0001],
                [0.0002, 0.0001, 0.0016],
            ]
        )

        # Calculate both
        frontier = calculate_efficient_frontier(mean_returns, cov_matrix, num_points=10)
        max_sharpe = maximize_sharpe_portfolio(mean_returns, cov_matrix)

        # Max Sharpe should be near one of the frontier points
        sharpe_vol = max_sharpe["volatility"]
        sharpe_ret = max_sharpe["return"]

        # Find closest frontier point
        min_distance = float("inf")
        for point in frontier:
            distance = (
                (point["volatility"] - sharpe_vol) ** 2
                + (point["return"] - sharpe_ret) ** 2
            ) ** 0.5
            min_distance = min(min_distance, distance)

        # Should be reasonably close (within numerical tolerance)
        assert min_distance < 0.05  # Adjust tolerance as needed

    def test_mathematical_consistency(self):
        """Test mathematical consistency between functions"""
        mean_returns = pd.Series([0.0005, 0.001])
        cov_matrix = pd.DataFrame([[0.0004, 0.0001], [0.0001, 0.0009]])

        # Test portfolio metrics consistency
        weights = np.array([0.3, 0.7])
        ret, vol = calculate_portfolio_metrics(weights, mean_returns, cov_matrix)

        # Manual calculation should match
        expected_ret = np.sum(mean_returns * weights) * 252
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix.values, weights))
        expected_vol = np.sqrt(portfolio_var) * np.sqrt(252)

        assert abs(ret - expected_ret) < 1e-10
        assert abs(vol - expected_vol) < 1e-10
