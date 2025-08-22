import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SimulateChartsResponse } from "../types/portfolio";
import type { CustomPortfolioFormData } from "../lib/portfolioUtils";
import type { PortfolioOptimizationResponse } from "../types/optimization";

interface CustomPortfolioState {
  // State
  customPortfolio: CustomPortfolioFormData | undefined;
  customPortfolioCharts: SimulateChartsResponse | undefined;
  customPortfolioOptimization: PortfolioOptimizationResponse | undefined;

  // Actions
  setCustomPortfolio: (payload: CustomPortfolioFormData) => void;
  setCustomPortfolioCharts: (payload: SimulateChartsResponse) => void;
  setCustomPortfolioOptimization: (
    payload: PortfolioOptimizationResponse
  ) => void;
  clearCustomState: () => void;

  // Getters
  isCustomStateActive: () => boolean;
}

const initialState = {
  customPortfolio: undefined,
  customPortfolioCharts: undefined,
  customPortfolioOptimization: undefined,
};

export const useCustomPortfolioStore = create<CustomPortfolioState>()(
  persist(
    (set, get) => ({
      // State
      ...initialState,

      // Actions
      setCustomPortfolio: (payload) => set({ customPortfolio: payload }),
      setCustomPortfolioCharts: (payload) =>
        set({ customPortfolioCharts: payload }),
      setCustomPortfolioOptimization: (payload) =>
        set({ customPortfolioOptimization: payload }),

      clearCustomState: () => set(initialState),

      // Getters
      isCustomStateActive: () => {
        const state = get();
        return Object.keys(initialState).every(
          (key) => !!state[key as keyof typeof state]
        );
      },
    }),
    {
      name: "custom-portfolio-storage",
    }
  )
);
