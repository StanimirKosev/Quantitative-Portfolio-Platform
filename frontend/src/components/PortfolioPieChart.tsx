import { useQuery } from "@tanstack/react-query";
import type { PortfolioResponse } from "../types/portfolio";
import { CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";
import { Legend, Pie, PieChart } from "recharts";
import { useRegimeStore } from "../store/regimeStore";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { API_BASE_URL } from "../lib/api";

const COLORS = [
  "#C8511F",
  "#5A9D15",
  "#2E6BA5",
  "#5A6A6A",
  "#9D2228",
  "#B3710C",
  "#5C3074",
  "#0F7485",
];

const pieChartStyles = {
  container: "flex flex-col items-center justify-center w-full lg:w-2/5 min-h-[250px] sm:min-h-[300px]",
  title: "text-lg sm:text-xl lg:text-2xl mb-2",
  chartContainer: "mx-auto aspect-square w-full max-w-[280px] sm:max-w-[350px] lg:max-w-[380px] p-2 sm:p-4",
  description: "mt-2 sm:mt-6 text-center w-full text-xs sm:text-sm",
};

const PortfolioPieChart = () => {
  const { selectedRegime } = useRegimeStore();
  const { customPortfolio, isCustomStateActive } = useCustomPortfolioStore();

  const { data: defaultPortfolio } = useQuery<PortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/api/portfolio/default`).then((res) => res.json()),
    enabled: !isCustomStateActive(),
  });

  const dataSources = customPortfolio || defaultPortfolio;

  const assets = dataSources?.portfolio_assets.map((asset, idx) => ({
    ...asset,
    ticker_pct: `${asset.ticker}: ${asset.weight_pct}%`,
    fill: COLORS[idx % COLORS.length],
  }));

  return (
    <div className={pieChartStyles.container}>
      <CardHeader className="items-center pb-0">
        <CardTitle className={pieChartStyles.title}>Portfolio Composition</CardTitle>
      </CardHeader>
      <ChartContainer
        config={{}}
        className={pieChartStyles.chartContainer}
      >
        <PieChart key={selectedRegime}>
          <ChartTooltip
            cursor={false}
            content={<ChartTooltipContent hideLabel />}
            formatter={(_, __, props) => {
              const { ticker, weight_pct, description } = props.payload;
              return [
                description
                  ? `${ticker}: ${weight_pct}% - ${description}`
                  : `${ticker}: ${weight_pct}%`,
              ];
            }}
          />
          <Pie
            data={assets}
            dataKey="weight_pct"
            nameKey="ticker_pct"
            innerRadius={80}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            wrapperStyle={{ 
              fontSize: window.innerWidth < 640 ? "0.8rem" : "1.05rem", 
              padding: "12px 0" 
            }}
          />
        </PieChart>
      </ChartContainer>
      <CardDescription
        className={pieChartStyles.description}
        style={{
          position: "absolute",
          left: "50%",
          top: window.innerWidth < 640 ? 10 : 30,
          transform: "translateX(-50%)",
        }}
      >
        Analysis period: {dataSources?.start_date} - {dataSources?.end_date}
      </CardDescription>
    </div>
  );
};

export default PortfolioPieChart;
