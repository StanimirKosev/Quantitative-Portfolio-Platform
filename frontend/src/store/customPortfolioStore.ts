import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { PortfolioResponse, PortfolioAsset } from "../types/portfolio";
import type { FormState } from "../pages/CustomPortfolioForm";

interface CustomPortfolioState {
  customPortfolio: PortfolioResponse | undefined;
  setCustomPortfolio: (formState: FormState) => void;
  clearCustomPortfolio: () => void;
}

export const useCustomPortfolioStore = create(
  immer<CustomPortfolioState>((set) => ({
    customPortfolio: undefined,
    setCustomPortfolio: (formState) =>
      set((state) => {
        state.customPortfolio = {
          portfolio_assets: formState.assets.map(
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            ({ description, ...rest }) => rest
          ) as PortfolioAsset[],
          start_date: formState.startDate,
          end_date: formState.endDate,
        };
      }),
    clearCustomPortfolio: () =>
      set((state) => {
        state.customPortfolio = undefined;
      }),
  }))
);
