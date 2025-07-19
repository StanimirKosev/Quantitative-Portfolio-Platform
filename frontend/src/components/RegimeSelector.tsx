import { useRegimeStore } from "../store/regimeStore";
import { useQuery } from "@tanstack/react-query";
import type { Regime } from "../types/regime";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

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
      <Select value={selectedRegime} onValueChange={setSelectedRegime}>
        <SelectTrigger className="w-[240px] px-4 py-3 rounded-lg bg-muted text-base font-medium shadow">
          <SelectValue placeholder="Select regime" />
        </SelectTrigger>
        <SelectContent>
          {data?.map((regime) => (
            <SelectItem key={regime.key} value={regime.key}>
              {regime.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default RegimeSelector;
