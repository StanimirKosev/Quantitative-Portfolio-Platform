"""
Unit tests for Monte Carlo simulation mathematical functions.
"""

import pytest
import pandas as pd
from simulation.engine.monte_carlo import (
    calculate_risk_metrics,
    modify_portfolio_for_regime,
    analyze_portfolio_risk_factors,
    analyze_portfolio_correlation,
)


class TestCalculateRiskMetrics:
    """Test VaR, CVaR, and max drawdown calculations"""

    def test_risk_metrics_with_known_losses(self):
        """Test VaR and CVaR calculations with known portfolio paths"""
        # Arrange: Create 5 paths with known final outcomes
        portfolio_paths = [
            [10000, 9500, 8000],  # 20% loss (worst)
            [10000, 9800, 9000],  # 10% loss
            [10000, 10100, 10200],  # 2% gain (median)
            [10000, 10500, 11000],  # 10% gain
            [10000, 11000, 12000],  # 20% gain (best)
        ]

        # Act
        metrics = calculate_risk_metrics(portfolio_paths)

        # Assert: Basic validations
        assert metrics["var_90_pct"] > 0
        assert metrics["var_90"] > 0
        assert metrics["cvar_90"] >= metrics["var_90"]
        assert metrics["max_drawdown_pct"] <= 0

    def test_var_cvar_relationship(self):
        """Test fundamental risk metric relationships"""
        portfolio_paths = [
            [10000, 9000],  # 10% loss
            [10000, 9500],  # 5% loss
            [10000, 8000],  # 20% loss
            [10000, 11000],  # 10% gain
            [10000, 12000],  # 20% gain
        ]

        metrics = calculate_risk_metrics(portfolio_paths)

        # Fundamental relationships that must always hold
        assert metrics["cvar_90"] >= metrics["var_90"]
        assert metrics["cvar_99"] >= metrics["var_99"]
        assert metrics["var_99"] >= metrics["var_90"]
        assert metrics["cvar_99"] >= metrics["cvar_90"]

    def test_empty_tail_guard(self):
        """Test CVaR fallback when tail is empty (edge case protection)"""
        # Create scenario where 99% VaR has empty tail
        portfolio_paths = [
            [10000, 9900],  # 1% loss
            [10000, 9950],  # 0.5% loss
        ]

        metrics = calculate_risk_metrics(portfolio_paths)

        # With only 2 paths, 99th percentile might have empty tail
        # CVaR should fallback to VaR value (line 110-111 in function)
        assert metrics["cvar_99"] == pytest.approx(metrics["var_99"], rel=0.01)
        assert metrics["cvar_90"] >= metrics["var_90"]


class TestModifyPortfolioForRegime:
    """Test regime modification of mean returns and covariance matrix"""

    def test_mean_returns_scaling(self):
        """Test mean returns are correctly scaled by regime factors"""
        # Arrange
        mean_returns = pd.Series([0.001, 0.002], index=["BTC", "GOLD"])
        cov_matrix = pd.DataFrame(
            [[0.01, 0.002], [0.002, 0.015]],
            index=["BTC", "GOLD"],
            columns=["BTC", "GOLD"],
        )
        regime_factors = {
            "BTC": {"mean_factor": 2.0, "vol_factor": 1.0},
            "GOLD": {"mean_factor": 1.5, "vol_factor": 1.0},
            "correlation_move_pct": 0.0,
        }

        # Act
        modified_returns, _ = modify_portfolio_for_regime(
            mean_returns, cov_matrix, regime_factors
        )

        # Assert: Returns should be scaled by mean_factor
        assert modified_returns["BTC"] == pytest.approx(0.002)  # 0.001 * 2.0
        assert modified_returns["GOLD"] == pytest.approx(0.003)  # 0.002 * 1.5

    def test_volatility_scaling(self):
        """Test covariance matrix is correctly scaled by volatility factors"""
        # Arrange: Simple 2x2 matrix
        mean_returns = pd.Series([0.001, 0.002], index=["BTC", "GOLD"])
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01], [0.01, 0.09]], index=["BTC", "GOLD"], columns=["BTC", "GOLD"]
        )
        regime_factors = {
            "BTC": {"mean_factor": 1.0, "vol_factor": 2.0},
            "GOLD": {"mean_factor": 1.0, "vol_factor": 1.5},
            "correlation_move_pct": 0.0,
        }

        # Act
        _, modified_cov = modify_portfolio_for_regime(
            mean_returns, cov_matrix, regime_factors
        )

        # Assert: Diagonal elements scaled by vol_factor^2
        expected_btc_var = 0.04 * (2.0**2)  # 0.04 * 4 = 0.16
        expected_gold_var = 0.09 * (1.5**2)  # 0.09 * 2.25 = 0.2025

        assert modified_cov.loc["BTC", "BTC"] == pytest.approx(
            expected_btc_var, rel=0.01
        )
        assert modified_cov.loc["GOLD", "GOLD"] == pytest.approx(
            expected_gold_var, rel=0.01
        )

    def test_correlation_adjustment(self):
        """Test correlation matrix modification"""
        # Arrange: Matrix with known correlation
        mean_returns = pd.Series([0.001, 0.002], index=["BTC", "GOLD"])
        # Correlation of 0.5 between BTC and GOLD
        cov_matrix = pd.DataFrame(
            [[0.04, 0.02], [0.02, 0.04]], index=["BTC", "GOLD"], columns=["BTC", "GOLD"]
        )
        regime_factors = {
            "BTC": {"mean_factor": 1.0, "vol_factor": 1.0},
            "GOLD": {"mean_factor": 1.0, "vol_factor": 1.0},
            "correlation_move_pct": 0.2,  # Increase correlation by 20%
        }

        # Act
        _, modified_cov = modify_portfolio_for_regime(
            mean_returns, cov_matrix, regime_factors
        )

        # Assert: Off-diagonal elements should change due to correlation adjustment
        # Original correlation was 0.5, should become 0.5 * (1 + 0.2) = 0.6
        original_off_diag = cov_matrix.loc["BTC", "GOLD"]
        modified_off_diag = modified_cov.loc["BTC", "GOLD"]

        assert abs(modified_off_diag) > abs(original_off_diag)  # Correlation increased


class TestAnalyzePortfolioCorrelation:
    """Test covariance matrix analysis and validation"""

    def test_correlation_matrix_calculation(self):
        """Test correlation matrix is correctly computed from covariance"""
        # Arrange: Known covariance matrix
        cov_matrix = pd.DataFrame(
            [
                [
                    0.04,
                    0.02,
                ],  # BTC: std=0.2, correlation with GOLD = 0.02/(0.2*0.3) = 0.333
                [0.02, 0.09],  # GOLD: std=0.3
            ],
            index=["BTC", "GOLD"],
            columns=["BTC", "GOLD"],
        )

        # Act
        result = analyze_portfolio_correlation(cov_matrix)

        # Assert
        corr_matrix = result["correlation_matrix"]
        assert corr_matrix.loc["BTC", "BTC"] == pytest.approx(
            1.0
        )  # Self-correlation = 1
        assert corr_matrix.loc["GOLD", "GOLD"] == pytest.approx(
            1.0
        )  # Self-correlation = 1
        assert corr_matrix.loc["BTC", "GOLD"] == pytest.approx(
            0.333, abs=0.01
        )  # Cross-correlation
        assert corr_matrix.loc["GOLD", "BTC"] == pytest.approx(
            0.333, abs=0.01
        )  # Symmetric

    def test_positive_definite_validation(self):
        """Test PSD validation for valid covariance matrix"""
        # Arrange: Valid PSD matrix
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01], [0.01, 0.09]], index=["BTC", "GOLD"], columns=["BTC", "GOLD"]
        )

        # Act
        result = analyze_portfolio_correlation(cov_matrix)

        # Assert
        assert result["is_psd"] == True
        assert result["min_eigenvalue"] > 0
        assert result["condition_number"] > 1  # Should be finite and > 1

    def test_ill_conditioned_matrix(self):
        """Test detection of ill-conditioned matrices"""
        # Arrange: Nearly singular matrix (high condition number)
        cov_matrix = pd.DataFrame(
            [[1.0, 0.999], [0.999, 1.0]], index=["A", "B"], columns=["A", "B"]
        )

        # Act
        result = analyze_portfolio_correlation(cov_matrix)

        # Assert
        assert result["condition_number"] > 100  # Very high condition number
        assert result["min_eigenvalue"] > 0  # Still PSD, just ill-conditioned


class TestAnalyzePortfolioRiskFactors:
    """Test PCA risk factor analysis"""

    def test_eigenvalue_sorting(self):
        """Test eigenvalues are sorted from largest to smallest"""
        # Arrange: Simple 2x2 matrix with known eigenvalues
        cov_matrix = pd.DataFrame(
            [[2.0, 0.0], [0.0, 1.0]],  # Eigenvalues should be 2.0 and 1.0
            index=["A", "B"],
            columns=["A", "B"],
        )

        # Act
        result = analyze_portfolio_risk_factors(cov_matrix)

        # Assert
        eigenvalues = result["eigenvalues"]
        assert eigenvalues[0] > eigenvalues[1]  # Sorted descending
        assert eigenvalues[0] == pytest.approx(2.0, abs=0.01)
        assert eigenvalues[1] == pytest.approx(1.0, abs=0.01)

    def test_dominant_factors_filtering(self):
        """Test only eigenvalues > 1.0 are considered dominant"""
        # Arrange: Matrix with one dominant factor (eigenvalue > 1) and one not
        cov_matrix = pd.DataFrame(
            [
                [3.0, 0.0, 0.0],
                [0.0, 1.5, 0.0],  # Both > 1.0 = dominant
                [0.0, 0.0, 0.5],  # < 1.0 = not dominant
            ],
            index=["A", "B", "C"],
            columns=["A", "B", "C"],
        )

        # Act
        result = analyze_portfolio_risk_factors(cov_matrix)

        # Assert
        dominant_loadings = result["dominant_factor_loadings"]
        # Should only have 2 factors (eigenvalues 3.0 and 1.5)
        assert len(dominant_loadings) == 2
        assert 1 in dominant_loadings  # PC1
        assert 2 in dominant_loadings  # PC2
        assert 3 not in dominant_loadings  # PC3 (eigenvalue 0.5 < 1.0)

    def test_asset_contribution_calculation(self):
        """Test asset contribution percentages in risk factors"""
        # Arrange: Simple diagonal matrix where each asset is its own factor
        cov_matrix = pd.DataFrame(
            [[4.0, 0.0], [0.0, 1.0]],
            index=["HIGH_RISK", "LOW_RISK"],
            columns=["HIGH_RISK", "LOW_RISK"],
        )

        # Act
        result = analyze_portfolio_risk_factors(cov_matrix)

        # Assert
        dominant_loadings = result["dominant_factor_loadings"]

        # PC1 (eigenvalue 4.0) should be dominated by HIGH_RISK asset
        pc1_loadings = dominant_loadings[1]
        high_risk_contrib = next(
            item for item in pc1_loadings if item["asset"] == "HIGH_RISK"
        )
        assert high_risk_contrib["pct"] > 90  # Should dominate this factor

    def test_explained_variance_calculation(self):
        """Test explained variance percentage calculation"""
        # Arrange: Known eigenvalues
        cov_matrix = pd.DataFrame(
            [
                [3.0, 0.0],  # Eigenvalues: 3.0 and 2.0, total = 5.0
                [0.0, 2.0],  # Dominant factors explain 100% (both > 1.0)
            ],
            index=["A", "B"],
            columns=["A", "B"],
        )

        # Act
        result = analyze_portfolio_risk_factors(cov_matrix)

        # Assert
        # Both eigenvalues > 1.0, so explained variance should be 100%
        assert result["explained_variance_dominant"] == pytest.approx(100.0, abs=0.1)
