import type {
  PortfolioRequestPayload,
  PortfolioResponse,
} from "../types/portfolio";
import type {
  RegimeParameter,
  RegimeParametersResponse,
} from "../types/regime";
import { API_BASE_URL } from "./api";

// Types
export type CustomPortfolioFormData = PortfolioResponse & {
  portfolio_factors: RegimeParametersResponse["parameters"];
};

// Constants
export const DEFAULT_ASSET_VALUES = {
  ticker: "",
  weight_pct: 0,
} as const;

export const DEFAULT_REGIME_FACTOR_VALUES = {
  ticker: "",
  mean_factor: 1.0,
  vol_factor: 1.0,
  correlation_move_pct: 0,
} as const;

export const DECIMAL_PRECISION = {
  WEIGHT: 1,
  FACTOR: 2,
} as const;

// Type guards and validation
const isIntermediateTypingState = (
  val: string,
  maxDecimals: number
): boolean => {
  const regexPattern = `^-?\\d*\\.?\\d{0,${maxDecimals}}$`;
  const isValidFormat = new RegExp(regexPattern).test(val);

  return (
    isValidFormat &&
    (val === "-" ||
      val.endsWith(".") ||
      val === "-0" ||
      val.startsWith("-0.") ||
      val.startsWith("0."))
  );
};

// Number field handling utilities
const parseAndRoundNumber = (
  value: string,
  decimalPlaces: number
): number | null => {
  const parsed = parseFloat(value);
  if (isNaN(parsed)) return null;

  const multiplier = Math.pow(10, decimalPlaces);
  return Math.round(parsed * multiplier) / multiplier;
};

/**
 * Processes number input value and returns the appropriate value for form state
 * Handles intermediate typing states and proper number parsing/rounding
 */
export const processNumberInput = (
  inputValue: string,
  decimalPlaces: number
): string | number | null => {
  // Allow intermediate typing states (-, -0, numbers ending with .)
  if (isIntermediateTypingState(inputValue, decimalPlaces)) {
    return inputValue;
  }

  // Handle empty string
  if (inputValue === "") {
    return null;
  }

  // Parse and round the number
  const parsed = parseAndRoundNumber(inputValue, decimalPlaces);
  return parsed;
};

// Form data transformation utilities
export const transformFormDataToApiPayload = (
  formData: CustomPortfolioFormData
): PortfolioRequestPayload => {
  return {
    tickers: formData.portfolio_assets.map((asset) => asset.ticker || ""),
    weights: formData.portfolio_assets.map(
      (asset) => Number(asset.weight_pct) / 100 || 0
    ),
    regime_factors: {
      ...Object.fromEntries(
        formData.portfolio_factors.map(
          ({ ticker, mean_factor, vol_factor }) => [
            ticker,
            {
              mean_factor: mean_factor == null ? null : Number(mean_factor),
              vol_factor: vol_factor == null ? null : Number(vol_factor),
            },
          ]
        )
      ),
      correlation_move_pct:
        formData.portfolio_factors[0]?.correlation_move_pct == null
          ? null
          : Number(formData.portfolio_factors[0].correlation_move_pct),
    },
    start_date: formData.start_date,
    end_date: formData.end_date,
  };
};

// API utilities
export const doCustomPortfolioRequest = async <T>(
  formData: CustomPortfolioFormData,
  endpoint: string
): Promise<T> => {
  const payload = transformFormDataToApiPayload(formData);

  const response = await fetch(`${API_BASE_URL}/api/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`HTTP ${response.status}: ${errorData.detail}`);
  }

  return response.json();
};

// Portfolio validation utilities
export const calculateTotalWeight = (
  assets: Array<{ weight_pct: number | string | null }>
): number => {
  return assets.reduce(
    (sum, asset) => sum + (Number(asset.weight_pct) || 0),
    0
  );
};

// Helper for getting factor values safely
export const getRegimeFactorValue = (
  portfolioFactors: RegimeParameter[],
  index: number,
  field: keyof RegimeParameter
): string => {
  const value = portfolioFactors?.[index]?.[field];
  return value == null ? "" : String(value);
};
