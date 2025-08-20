import pytest
from unittest.mock import patch
import pandas as pd
import numpy as np
from fastapi import HTTPException
from fastapi.testclient import TestClient

from core.utils import InvalidTickersException
from optimization.api.api_utils import optimize_portfolio_api
from app import app


class TestOptimizePortfolioApi:
    """Tests for the optimization orchestrator function."""

    @patch("optimization.api.api_utils.maximize_sharpe_portfolio")
    @patch("optimization.api.api_utils.calculate_efficient_frontier")
    @patch("optimization.api.api_utils.calculate_mean_and_covariance")
    @patch("optimization.api.api_utils.transform_to_daily_returns")
    @patch("optimization.api.api_utils.get_cached_prices")
    def test_historical_regime_optimization(
        self,
        mock_fetch,
        mock_transform,
        mock_calc_mean_cov,
        mock_frontier,
        mock_max_sharpe,
    ):
        # Arrange
        tickers = ["BTC-EUR", "SPYL.DE"]
        regime = "historical"

        # Price data → returns
        mock_fetch.return_value = pd.DataFrame(
            {"BTC-EUR": [100, 102, 101], "SPYL.DE": [50, 51, 50.5]}
        )
        mock_transform.return_value = pd.DataFrame(
            {"BTC-EUR": [0.01, -0.005], "SPYL.DE": [0.02, -0.01]}
        )

        # mean/cov (sample + shrunk)
        mean_returns = pd.Series([0.001, 0.0005], index=tickers)
        cov_sample = pd.DataFrame(
            [[0.01, 0.002], [0.002, 0.015]], index=tickers, columns=tickers
        )
        cov_shrunk = cov_sample * 0.9
        mock_calc_mean_cov.return_value = (mean_returns, cov_sample, cov_shrunk)

        # Frontier and max-sharpe outputs (annualized decimals)
        mock_frontier.return_value = [
            {"return": 0.08, "volatility": 0.12, "weights": np.array([0.6, 0.4])}
        ]
        mock_max_sharpe.return_value = {
            "return": 0.09,
            "volatility": 0.13,
            "weights": np.array([0.55, 0.45]),
            "sharpe_ratio": 0.6923,
            "risk_free_rate": 0.025,
        }

        # Act
        resp = optimize_portfolio_api(tickers, regime)

        # Assert numeric formatting to percent fields
        assert resp.frontier_points[0].return_pct == 8.0
        assert resp.frontier_points[0].volatility_pct == 12.0
        assert resp.frontier_points[0].weights_pct == [60.0, 40.0]

        assert resp.max_sharpe_point.return_pct == 9.0
        assert resp.max_sharpe_point.volatility_pct == 13.0
        assert resp.max_sharpe_point.weights_pct == [55.0, 45.0]
        assert resp.max_sharpe_point.sharpe_ratio == pytest.approx(
            0.69, rel=0, abs=0.01
        )

        assert resp.risk_free_rate_pct == 2.5

        mock_fetch.assert_called_once()
        mock_frontier.assert_called_once()
        mock_max_sharpe.assert_called_once()

    def test_invalid_regime_raises_http_exception(self):
        tickers = ["BTC-EUR"]
        with pytest.raises(HTTPException) as exc_info:
            optimize_portfolio_api(tickers, "invalid_regime")
        assert exc_info.value.status_code == 400
        assert "Invalid regime name" in str(exc_info.value.detail)

    @patch("optimization.api.api_utils.maximize_sharpe_portfolio")
    @patch("optimization.api.api_utils.calculate_efficient_frontier")
    @patch("optimization.api.api_utils.modify_portfolio_for_regime")
    @patch("optimization.api.api_utils.calculate_mean_and_covariance")
    @patch("optimization.api.api_utils.transform_to_daily_returns")
    @patch("optimization.api.api_utils.get_cached_prices")
    def test_custom_regime_with_factors(
        self,
        mock_fetch,
        mock_transform,
        mock_calc_mean_cov,
        mock_modify,
        mock_frontier,
        mock_max_sharpe,
    ):
        tickers = ["BTC-EUR", "SPYL.DE"]
        regime = "custom"
        custom_factors = {
            "BTC-EUR": {"mean_factor": 1.2, "vol_factor": 1.1},
            "SPYL.DE": {"mean_factor": 0.9, "vol_factor": 1.05},
            "correlation_move_pct": -0.1,
        }

        mock_fetch.return_value = pd.DataFrame(
            {"BTC-EUR": [100, 102, 101], "SPYL.DE": [50, 51, 50.5]}
        )
        mock_transform.return_value = pd.DataFrame(
            {"BTC-EUR": [0.01, -0.005], "SPYL.DE": [0.02, -0.01]}
        )

        hist_mean = pd.Series([0.001, 0.0005], index=tickers)
        cov_sample = pd.DataFrame(
            [[0.01, 0.002], [0.002, 0.015]], index=tickers, columns=tickers
        )
        cov_shrunk = cov_sample * 0.9
        mock_calc_mean_cov.return_value = (hist_mean, cov_sample, cov_shrunk)

        # After regime modification (used by optimization with shrunk covariance)
        mod_mean = pd.Series([0.0011, 0.00045], index=tickers)
        mod_cov = cov_shrunk * 1.05
        mock_modify.return_value = (mod_mean, mod_cov)

        mock_frontier.return_value = [
            {"return": 0.07, "volatility": 0.11, "weights": np.array([0.58, 0.42])}
        ]
        mock_max_sharpe.return_value = {
            "return": 0.085,
            "volatility": 0.12,
            "weights": np.array([0.6, 0.4]),
            "sharpe_ratio": 0.71,
            "risk_free_rate": 0.02,
        }

        resp = optimize_portfolio_api(tickers, regime, custom_factors)

        mock_modify.assert_called_once()
        assert "frontier_points" in resp.dict()
        assert resp.max_sharpe_point.sharpe_ratio == pytest.approx(0.71, abs=1e-9)

    @patch("optimization.api.api_utils.get_cached_prices")
    def test_data_fetch_exception_handling(self, mock_fetch):
        tickers = ["INVALID"]
        mock_fetch.side_effect = InvalidTickersException("Invalid ticker: INVALID")
        with pytest.raises(HTTPException) as exc_info:
            optimize_portfolio_api(tickers, "historical")
        assert exc_info.value.status_code == 400
        assert "Invalid ticker" in str(exc_info.value.detail)


class TestFastApiIntegration:
    """FastAPI endpoint tests for optimization router."""

    def setup_method(self):
        self.client = TestClient(app)

    @patch("optimization.api.routes.optimize_portfolio_api")
    def test_default_portfolio_optimization_endpoint(self, mock_optimize):
        mock_optimize.return_value = {
            "frontier_points": [
                {"return_pct": 8.0, "volatility_pct": 12.0, "weights_pct": [60.0, 40.0]}
            ],
            "max_sharpe_point": {
                "return_pct": 9.0,
                "volatility_pct": 13.0,
                "weights_pct": [55.0, 45.0],
                "sharpe_ratio": 0.7,
            },
            "risk_free_rate_pct": 2.5,
        }

        resp = self.client.post("/api/optimize/historical")
        assert resp.status_code == 200
        data = resp.json()
        assert "frontier_points" in data
        assert "max_sharpe_point" in data
        assert "risk_free_rate_pct" in data
        mock_optimize.assert_called_once()

    @patch("optimization.api.routes.optimize_portfolio_api")
    def test_custom_portfolio_optimization_endpoint(self, mock_optimize):
        mock_optimize.return_value = {
            "frontier_points": [
                {"return_pct": 7.5, "volatility_pct": 11.0, "weights_pct": [58.0, 42.0]}
            ],
            "max_sharpe_point": {
                "return_pct": 8.6,
                "volatility_pct": 12.1,
                "weights_pct": [60.0, 40.0],
                "sharpe_ratio": 0.72,
            },
            "risk_free_rate_pct": 2.0,
        }

        payload = {
            "tickers": ["BTC-EUR", "SPYL.DE"],
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }

        resp = self.client.post("/api/optimize/custom", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "frontier_points" in data
        assert "max_sharpe_point" in data
        mock_optimize.assert_called_once()
