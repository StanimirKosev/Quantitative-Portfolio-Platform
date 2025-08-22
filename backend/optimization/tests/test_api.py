import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import pandas as pd
import numpy as np
from fastapi import HTTPException
from fastapi.testclient import TestClient
import json

from core.utils import InvalidTickersException
from optimization.api.api_utils import optimize_portfolio_api, ProgressBroadcaster
from app import app


class TestOptimizePortfolioApi:
    """Tests for the optimization orchestrator function."""

    @patch("optimization.api.api_utils.maximize_sharpe_portfolio")
    @patch("optimization.api.api_utils.calculate_efficient_frontier")
    @patch("core.api.api_utils.calculate_mean_and_covariance")
    @patch("core.api.api_utils.transform_to_daily_returns")
    @patch("core.api.api_utils.get_cached_prices")
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
    @patch("core.api.api_utils.calculate_mean_and_covariance")
    @patch("core.api.api_utils.transform_to_daily_returns")
    @patch("core.api.api_utils.get_cached_prices")
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

    @patch("core.api.api_utils.get_cached_prices")
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
                {"return_pct": 8.0, "volatility_pct": 12.0, "weights_pct": [60.0, 40.0], "tickers": ["BTC-EUR", "SPYL.DE"]}
            ],
            "max_sharpe_point": {
                "return_pct": 9.0,
                "volatility_pct": 13.0,
                "weights_pct": [55.0, 45.0],
                "sharpe_ratio": 0.7,
                "tickers": ["BTC-EUR", "SPYL.DE"],
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
                {"return_pct": 7.5, "volatility_pct": 11.0, "weights_pct": [58.0, 42.0], "tickers": ["BTC-EUR", "SPYL.DE"]}
            ],
            "max_sharpe_point": {
                "return_pct": 8.6,
                "volatility_pct": 12.1,
                "weights_pct": [60.0, 40.0],
                "sharpe_ratio": 0.72,
                "tickers": ["BTC-EUR", "SPYL.DE"],
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


class TestProgressBroadcaster:
    """Tests for WebSocket progress broadcasting functionality."""

    def setup_method(self):
        self.broadcaster = ProgressBroadcaster()

    @pytest.mark.asyncio
    async def test_connect_websocket(self):
        mock_websocket = AsyncMock()

        await self.broadcaster.connect(mock_websocket)

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in self.broadcaster.connections

    def test_disconnect_websocket(self):
        mock_websocket = MagicMock()
        self.broadcaster.connections.append(mock_websocket)

        self.broadcaster.disconnect(mock_websocket)

        assert mock_websocket not in self.broadcaster.connections

    def test_disconnect_nonexistent_websocket(self):
        mock_websocket = MagicMock()

        # Should not raise error
        self.broadcaster.disconnect(mock_websocket)
        assert len(self.broadcaster.connections) == 0

    @pytest.mark.asyncio
    async def test_broadcast_progress_no_connections(self):
        # Should not raise error when no connections
        await self.broadcaster.broadcast_progress(10, 25, "Testing progress")

    @pytest.mark.asyncio
    async def test_broadcast_progress_success(self):
        mock_websocket = AsyncMock()
        self.broadcaster.connections.append(mock_websocket)

        await self.broadcaster.broadcast_progress(15, 25, "Calculating portfolio 15/25")

        expected_data = {
            "current": 15,
            "total": 25,
            "message": "Calculating portfolio 15/25",
            "percentage": 60.0,
        }
        mock_websocket.send_text.assert_called_once_with(json.dumps(expected_data))

    @pytest.mark.asyncio
    async def test_broadcast_progress_handles_failed_connections(self):
        good_websocket = AsyncMock()
        bad_websocket = AsyncMock()
        bad_websocket.send_text.side_effect = Exception("Connection broken")

        self.broadcaster.connections.extend([good_websocket, bad_websocket])

        await self.broadcaster.broadcast_progress(5, 10, "Testing")

        # Good connection should receive message
        good_websocket.send_text.assert_called_once()
        # Bad connection should be removed
        assert bad_websocket not in self.broadcaster.connections
        assert good_websocket in self.broadcaster.connections

    @pytest.mark.asyncio
    async def test_broadcast_progress_percentage_calculation(self):
        mock_websocket = AsyncMock()
        self.broadcaster.connections.append(mock_websocket)

        await self.broadcaster.broadcast_progress(0, 20, "Starting")

        call_args = mock_websocket.send_text.call_args[0][0]
        data = json.loads(call_args)
        assert data["percentage"] == 0.0

    @pytest.mark.asyncio
    async def test_broadcast_progress_zero_total_handling(self):
        mock_websocket = AsyncMock()
        self.broadcaster.connections.append(mock_websocket)

        await self.broadcaster.broadcast_progress(1, 0, "Edge case")

        call_args = mock_websocket.send_text.call_args[0][0]
        data = json.loads(call_args)
        assert data["percentage"] == 0


class TestWebSocketIntegration:
    """Integration tests for WebSocket endpoints."""

    def setup_method(self):
        self.client = TestClient(app)

    def test_websocket_progress_endpoint_connection(self):
        with self.client.websocket_connect("/api/optimize/ws/progress") as websocket:
            # Connection should be established successfully
            # Send a test message to keep connection alive
            websocket.send_text("test")

            # WebSocket should stay connected
            assert websocket is not None
