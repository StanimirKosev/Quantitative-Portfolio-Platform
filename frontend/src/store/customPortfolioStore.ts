import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SimulateChartsResponse } from "../types/portfolio";
import type { CustomPortfolioFormData } from "../lib/portfolioUtils";

interface CustomPortfolioState {
  // State
  customPortfolio: CustomPortfolioFormData | undefined;
  customPortfolioCharts: SimulateChartsResponse | undefined;

  // Actions
  setCustomPortfolio: (payload: CustomPortfolioFormData) => void;
  setCustomPortfolioCharts: (payload: SimulateChartsResponse) => void;
  clearCustomState: () => void;

  // Getters
  isCustomStateActive: () => boolean;
}

export const useCustomPortfolioStore = create<CustomPortfolioState>()(
  persist(
    (set, get) => ({
      // State
      customPortfolio: undefined,
      customPortfolioCharts: undefined,

      // Actions
      setCustomPortfolio: (payload) => set({ customPortfolio: payload }),
      setCustomPortfolioCharts: (payload) =>
        set({ customPortfolioCharts: payload }),
      clearCustomState: () =>
        set({ customPortfolio: undefined, customPortfolioCharts: undefined }),

      // Getters
      isCustomStateActive: () => {
        const state = get();
        return !!(state.customPortfolio && state.customPortfolioCharts);
      },
    }),
    {
      name: "custom-portfolio-storage",
    }
  )
);
