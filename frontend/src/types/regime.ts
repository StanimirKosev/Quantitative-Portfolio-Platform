export type RegimeKey =
  | "historical"
  | "fiat_debasement"
  | "geopolitical_crisis";

export interface Regime {
  key: RegimeKey;
  name: string;
  description: string;
}
