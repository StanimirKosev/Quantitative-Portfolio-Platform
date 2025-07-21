import { useRegimeStore } from "../store/regimeStore";
import { useQuery } from "@tanstack/react-query";
import type { Regime } from "../types/regime";
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group";

const RegimeSelector = () => {
  const { selectedRegime, setSelectedRegime } = useRegimeStore();

  const apiUrl = import.meta.env.VITE_API_URL;

  const { data } = useQuery<Regime[]>({
    queryKey: ["regimes"],
    queryFn: () =>
      fetch(`${apiUrl}/api/regimes`)
        .then((res) => res.json())
        .then((data) => data.regimes),
  });

  return (
    <div className="w-full flex flex-col items-center py-4">
      <ToggleGroup
        type="single"
        value={selectedRegime}
        onValueChange={setSelectedRegime}
        className="flex gap-1.5"
      >
        {data?.map((regime) => (
          <ToggleGroupItem
            key={regime.key}
            value={regime.key}
            aria-label={regime.name}
            className="px-1 py-0.5 min-w-[120px] text-base font-medium whitespace-nowrap"
          >
            {regime.name}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    </div>
  );
};

export default RegimeSelector;
