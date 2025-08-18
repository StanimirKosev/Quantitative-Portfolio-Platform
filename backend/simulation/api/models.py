from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel

RegimeFactors = Dict[str, Union[Dict[str, Optional[float]], float]]


class PortfolioRequestPayload(BaseModel):
    tickers: List[str]
    weights: List[float]
    regime: Optional[str] = "historical"
    regime_factors: Optional[RegimeFactors] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SimulationChartsResponse(BaseModel):
    simulation_chart_path: str
    correlation_matrix_chart_path: str
    risk_factors_chart_path: str


class PortfolioAsset(BaseModel):
    ticker: str
    weight_pct: float
    description: str = ""


class PortfolioDefaultResponse(BaseModel):
    portfolio_assets: List[PortfolioAsset]
    start_date: str
    end_date: str


class RegimeParameterItem(BaseModel):
    ticker: str
    mean_factor: float
    vol_factor: float
    correlation_move_pct: float


class RegimeParametersResponse(BaseModel):
    regime: str
    description: Optional[str] = None
    parameters: List[RegimeParameterItem]


class RegimeListItem(BaseModel):
    key: str
    name: str


class RegimesResponse(BaseModel):
    regimes: List[RegimeListItem]


class ValidationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None


class LogPayload(BaseModel):
    event: str
    level: Literal["info", "error", "fatal"]
    timestamp: str
    route: Optional[str] = None
    context: Optional[Dict] = None
