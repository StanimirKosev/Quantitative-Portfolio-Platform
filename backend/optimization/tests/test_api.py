import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import pandas as pd
import numpy as np
from fastapi import HTTPException, WebSocketDisconnect
from fastapi.testclient import TestClient
import json
import asyncio

from core.utils import InvalidTickersException
from optimization.api.api_utils import optimize_portfolio_api
from core.api.api_utils import LivePriceStreamer
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
        assert "frontier_points" in resp.model_dump()
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
                {
                    "return_pct": 8.0,
                    "volatility_pct": 12.0,
                    "weights_pct": [60.0, 40.0],
                    "tickers": ["BTC-EUR", "SPYL.DE"],
                }
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
                {
                    "return_pct": 7.5,
                    "volatility_pct": 11.0,
                    "weights_pct": [58.0, 42.0],
                    "tickers": ["BTC-EUR", "SPYL.DE"],
                }
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


class TestLivePriceStreamer:
    """Tests for WebSocket live price streaming functionality."""

    def setup_method(self):
        self.mock_websocket = AsyncMock()

    @patch("core.api.api_utils.get_portfolio")
    def test_streamer_initialization(self, mock_get_portfolio):
        mock_get_portfolio.return_value = (["BTC-EUR", "SPYL.DE"], [0.6, 0.4])

        streamer = LivePriceStreamer(self.mock_websocket)

        assert streamer.fastapi_websocket == self.mock_websocket
        assert streamer.current_tickers == []

    @pytest.mark.asyncio
    @patch("core.api.api_utils.yf.AsyncWebSocket")
    @patch("core.api.api_utils.get_portfolio")
    async def test_start_accepts_websocket(
        self, mock_get_portfolio, mock_yf_websocket_class
    ):
        mock_get_portfolio.return_value = (["BTC-EUR"], [1.0])
        mock_yf_websocket = AsyncMock()
        mock_yf_websocket_class.return_value.__aenter__.return_value = mock_yf_websocket

        # Mock the receive_text to raise WebSocketDisconnect immediately
        self.mock_websocket.receive_text.side_effect = WebSocketDisconnect()

        streamer = LivePriceStreamer(self.mock_websocket)
        await streamer.start()

        # Verify WebSocket was accepted
        self.mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    @patch("core.api.api_utils.yf.AsyncWebSocket")
    @patch("core.api.api_utils.get_portfolio")
    async def test_start_subscribes_to_default_tickers(
        self, mock_get_portfolio, mock_yf_websocket_class
    ):
        default_tickers = ["BTC-EUR", "SPYL.DE"]
        mock_get_portfolio.return_value = (default_tickers, [0.6, 0.4])

        mock_yf_websocket = AsyncMock()
        mock_yf_websocket_class.return_value.__aenter__.return_value = mock_yf_websocket

        # Mock frontend sending tickers, then disconnect
        self.mock_websocket.receive_text.side_effect = [
            json.dumps(default_tickers),  # Initial subscription
            WebSocketDisconnect()         # Then disconnect
        ]

        streamer = LivePriceStreamer(self.mock_websocket)
        await streamer.start()

        # Verify Yahoo Finance WebSocket subscription to tickers from frontend
        mock_yf_websocket.subscribe.assert_called_with(default_tickers)

    @pytest.mark.asyncio
    @patch("core.api.api_utils.yf.AsyncWebSocket")
    @patch("core.api.api_utils.get_portfolio")
    async def test_start_handles_websocket_disconnect_gracefully(
        self, mock_get_portfolio, mock_yf_websocket_class
    ):
        mock_get_portfolio.return_value = (["BTC-EUR"], [1.0])
        mock_yf_websocket = AsyncMock()
        mock_yf_websocket_class.return_value.__aenter__.return_value = mock_yf_websocket

        # Mock WebSocket disconnect
        self.mock_websocket.receive_text.side_effect = WebSocketDisconnect()

        streamer = LivePriceStreamer(self.mock_websocket)

        # Should not raise exception
        await streamer.start()

    @pytest.mark.asyncio
    @patch("core.api.api_utils.yf.AsyncWebSocket")
    @patch("core.api.api_utils.get_portfolio")
    async def test_start_handles_subscription_updates(
        self, mock_get_portfolio, mock_yf_websocket_class
    ):
        mock_get_portfolio.return_value = (["BTC-EUR"], [1.0])
        mock_yf_websocket = AsyncMock()
        mock_yf_websocket_class.return_value.__aenter__.return_value = mock_yf_websocket

        custom_tickers = ["TSLA", "AAPL"]

        # First call returns custom tickers, second call raises disconnect
        self.mock_websocket.receive_text.side_effect = [
            json.dumps(custom_tickers),
            WebSocketDisconnect(),
        ]

        streamer = LivePriceStreamer(self.mock_websocket)
        
        # Should not raise exception when handling subscription updates
        await streamer.start()

    @pytest.mark.asyncio
    async def test_forward_to_frontend(self):
        streamer = LivePriceStreamer(self.mock_websocket)
        test_message = {"symbol": "BTC-EUR", "price": 45000.0}

        # Call the method - this creates a background task
        streamer._forward_to_frontend(test_message)

        # Give the async task a moment to complete
        await asyncio.sleep(0.1)

        # Verify the message was sent to the frontend WebSocket
        self.mock_websocket.send_text.assert_called_once_with(json.dumps(test_message))

    @pytest.mark.asyncio
    async def test_update_subscription_cancels_old_task(self):
        streamer = LivePriceStreamer(self.mock_websocket)
        streamer.current_tickers = ["BTC-EUR"]

        mock_yf_websocket = AsyncMock()
        # Use MagicMock for the task to avoid async mock issues
        mock_old_task = MagicMock()
        custom_tickers = ["TSLA", "AAPL"]

        with patch("core.api.api_utils.yf.AsyncWebSocket") as mock_yf_class:
            mock_new_websocket = AsyncMock()
            mock_yf_class.return_value = mock_new_websocket

            new_websocket, new_task = await streamer._update_subscription(
                mock_yf_websocket, mock_old_task, custom_tickers
            )

            # Verify old task was cancelled and old websocket closed
            mock_old_task.cancel.assert_called_once()
            mock_yf_websocket.close.assert_called_once()

            # Verify new websocket was created and subscribed
            mock_yf_class.assert_called_once_with(verbose=False)
            mock_new_websocket.subscribe.assert_called_once_with(custom_tickers)

            # Verify current_tickers was updated
            assert streamer.current_tickers == custom_tickers

            # Verify new websocket and task were returned
            assert new_websocket == mock_new_websocket
            assert new_task is not None

    @pytest.mark.asyncio
    @patch("core.api.api_utils.yf.AsyncWebSocket")
    @patch("core.api.api_utils.get_portfolio")
    async def test_start_handles_exceptions_gracefully(
        self, mock_get_portfolio, mock_yf_websocket_class
    ):
        mock_get_portfolio.return_value = (["BTC-EUR"], [1.0])

        # Make yfinance WebSocket raise an exception
        mock_yf_websocket_class.side_effect = Exception(
            "Yahoo Finance connection failed"
        )

        streamer = LivePriceStreamer(self.mock_websocket)

        # Should not raise exception, just log error
        await streamer.start()

        # WebSocket should still be accepted
        self.mock_websocket.accept.assert_called_once()
