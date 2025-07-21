export interface PortfolioAsset {
  ticker: string;
  weight_pct: number;
  description: string;
}

export interface PortfolioResponse {
  portfolio_assets: PortfolioAsset[];
  start_date: string;
  end_date: string;
}

export interface SimulateChartsResponse {
  simulation_chart_path: string;
  correlation_matrix_chart_path: string;
  risk_factors_chart_path: string;
}

export interface ValidationResponse {
  success: boolean;
  message?: string;
  errors?: string[];
}
