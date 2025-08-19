from pydantic import BaseModel


class SimulationChartsResponse(BaseModel):
    simulation_chart_path: str
    correlation_matrix_chart_path: str
    risk_factors_chart_path: str
