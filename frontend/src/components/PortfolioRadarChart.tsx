import { useQuery } from "@tanstack/react-query";
import type { RegimeParametersResponse } from "../types/regime";
import { useRegimeStore } from "../store/regimeStore";
import { CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Legend, PolarAngleAxis, PolarGrid, Radar, RadarChart } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "./ui/chart";

const chartConfig = {
  mean_factor: {
    label: "Mean Factor",
    color: "#4A90E2",
  },
  vol_factor: {
    label: "Volatility Factor",
    color: "#FF6B35",
  },
  correlation_move_pct: {
    label: "Correlation Move",
    color: "#7ED321",
  },
} satisfies ChartConfig;

const PortfolioRadarChart = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const { selectedRegime } = useRegimeStore();

  const { data } = useQuery<RegimeParametersResponse>({
    queryKey: [selectedRegime, "parameters"],
    queryFn: () =>
      fetch(`${apiUrl}/api/regimes/${selectedRegime}/parameters`)
        .then((res) => res.json())
        .then((data) => data),
    enabled: !!selectedRegime,
  });

  return (
    <div className="flex flex-col items-center justify-center w-2/5">
      <CardHeader className="items-center pb-0">
        <CardTitle className="text-2xl mb-2">Factor Radar</CardTitle>
      </CardHeader>
      <ChartContainer
        config={{}}
        className="mx-auto aspect-square w-full max-w-[380px] p-4 -mt-1"
      >
        <RadarChart data={data?.parameters} className="-mt-4">
          <ChartTooltip
            cursor={false}
            content={<ChartTooltipContent indicator="line" />}
          />
          <PolarAngleAxis dataKey="ticker" />
          <PolarGrid radialLines={false} />
          {Object.entries(chartConfig).map(([dataKey, { label, color }]) => (
            <Radar
              key={dataKey}
              name={label}
              dataKey={dataKey}
              stroke={color}
              fill={color}
              fillOpacity={0.1}
            />
          ))}
          <Legend
            verticalAlign="bottom"
            height={36}
            content={() => (
              <CardDescription
                style={{ textAlign: "center", padding: "25px 0" }}
              >
                {data?.description}
              </CardDescription>
            )}
          />
        </RadarChart>
      </ChartContainer>
    </div>
  );
};

export default PortfolioRadarChart;
