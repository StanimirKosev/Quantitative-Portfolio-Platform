import { create } from "zustand";
import type { RegimeKey } from "../types/regime";

interface RegimeState {
  selectedRegime: RegimeKey;
  setSelectedRegime: (regime: RegimeKey) => void;
}

export const useRegimeStore = create<RegimeState>((set) => ({
  selectedRegime: "historical",
  setSelectedRegime: (selectedRegime) => set({ selectedRegime }),
}));
