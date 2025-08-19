from typing import List, Optional
from pydantic import BaseModel, Field

from core.api.models import PortfolioRequestPayload


class EfficientFrontierPoint(BaseModel):
    """Single point on the efficient frontier"""

    return_pct: float
    volatility_pct: float
    weights_pct: List[float]


class MaxSharpePoint(BaseModel):
    """Maximum Sharpe ratio portfolio point"""

    return_pct: float
    volatility_pct: float
    weights_pct: List[float]
    sharpe_ratio: float


class PortfolioOptimizationResponse(BaseModel):
    """Complete portfolio optimization response with efficient frontier and max Sharpe portfolio"""

    frontier_points: List[EfficientFrontierPoint]
    max_sharpe_point: MaxSharpePoint
    risk_free_rate_pct: float


class OptimizationRequestPayload(PortfolioRequestPayload):
    weights: Optional[List[float]] = Field(
        default=None, exclude=True
    )  # optional + hidden
