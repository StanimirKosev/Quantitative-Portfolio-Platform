export type RegimeKey =
  | "historical"
  | "fiat_debasement"
  | "geopolitical_crisis";

export interface Regime {
  key: RegimeKey;
  name: string;
  description: string;
}

export interface RegimeParameter {
  ticker: string;
  mean_factor: number;
  vol_factor: number;
  correlation_move_pct: number;
}

export interface RegimeParametersResponse {
  regime: string;
  parameters: RegimeParameter[];
  description: string;
}
