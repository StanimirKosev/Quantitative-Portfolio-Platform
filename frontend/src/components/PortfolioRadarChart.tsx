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
import { API_BASE_URL } from "../lib/api";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";

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

const radarChartStyles = {
  container:
    "flex flex-col items-center justify-center w-full lg:w-2/5 min-h-[250px] sm:min-h-[300px]",
  title: "text-lg sm:text-xl lg:text-2xl mb-2",
  chartContainer:
    "mx-auto aspect-square w-full max-w-[280px] sm:max-w-[350px] lg:max-w-[380px] p-2 sm:p-4 -mt-1",
  description: "text-xs sm:text-sm",
};

const PortfolioRadarChart = () => {
  const { selectedRegime } = useRegimeStore();
  const { customPortfolio, isCustomStateActive } = useCustomPortfolioStore();

  const { data: defaultPortfolioRegimeFactors } =
    useQuery<RegimeParametersResponse>({
      queryKey: [selectedRegime, "parameters"],
      queryFn: () =>
        fetch(`${API_BASE_URL}/api/regimes/${selectedRegime}/parameters`).then(
          (res) => res.json()
        ),
      enabled: !!selectedRegime && !isCustomStateActive(),
    });

  const dataSources =
    customPortfolio?.portfolio_factors ||
    defaultPortfolioRegimeFactors?.parameters;

  return (
    <div className={radarChartStyles.container}>
      <CardHeader className="items-center pb-0 pt-0">
        <CardTitle className={radarChartStyles.title}>Factor Radar</CardTitle>
      </CardHeader>
      <ChartContainer config={{}} className={radarChartStyles.chartContainer}>
        <RadarChart data={dataSources} className="-mt-4">
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
                className={radarChartStyles.description}
                style={{
                  textAlign: "center",
                  padding: window.innerWidth < 640 ? "15px 0" : "25px 0",
                }}
              >
                {!isCustomStateActive()
                  ? defaultPortfolioRegimeFactors?.description
                  : null}
              </CardDescription>
            )}
          />
        </RadarChart>
      </ChartContainer>
    </div>
  );
};

export default PortfolioRadarChart;
