import { useRegimeStore } from "../store/regimeStore";
import { useQuery } from "@tanstack/react-query";
import type { Regime, RegimeKey } from "../types/regime";
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group";
import { API_BASE_URL } from "../lib/api";

const RegimeSelector = () => {
  const { selectedRegime, setSelectedRegime } = useRegimeStore();

  const { data } = useQuery<Regime[]>({
    queryKey: ["regimes"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/api/regimes`)
        .then((res) => res.json())
        .then((data) => data.regimes),
  });

  return (
    <div className="w-full flex flex-col items-center">
      <ToggleGroup
        type="single"
        value={selectedRegime}
        onValueChange={(value: RegimeKey) => {
          if (!value) return;
          setSelectedRegime(value);
        }}
        className="flex-wrap justify-center gap-2"
      >
        {data?.map((regime) => (
          <ToggleGroupItem
            key={regime.key}
            value={regime.key}
            aria-label={regime.name}
            className="px-2 py-1 sm:px-3 sm:py-1.5 min-w-[100px] sm:min-w-[120px] text-xs sm:text-sm lg:text-base font-medium whitespace-nowrap transition-all duration-150 active:scale-95 touch-manipulation hover:scale-[1.02]"
          >
            {regime.name}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    </div>
  );
};

export default RegimeSelector;
