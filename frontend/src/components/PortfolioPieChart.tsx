import { useQuery } from "@tanstack/react-query";
import type { DefaultPortfolioResponse } from "../types/portfolio";
import { CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";
import { Legend, Pie, PieChart } from "recharts";
import { useRegimeStore } from "../store/regimeStore";

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

const PortfolioPieChart = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const { selectedRegime } = useRegimeStore();

  const { data } = useQuery<DefaultPortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${apiUrl}/api/portfolio/default`)
        .then((res) => res.json())
        .then((data) => data),
  });

  const assets = data?.default_portfolio_assets?.map((asset, idx) => ({
    ...asset,
    ticker_pct: `${asset.ticker}: ${asset.weight_pct}%`,
    fill: COLORS[idx % COLORS.length],
  }));

  return (
    <div className="flex flex-col items-center justify-center w-2/5">
      <CardHeader className="items-center pb-0">
        <CardTitle className="text-2xl mb-2">Portfolio Composition</CardTitle>
      </CardHeader>
      <ChartContainer
        config={{}}
        className="mx-auto aspect-square w-full max-w-[380px] p-4"
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
            wrapperStyle={{ fontSize: "1.05rem", padding: "12px 0" }}
          />
        </PieChart>
      </ChartContainer>
      <CardDescription
        className="mt-6 text-center w-full"
        style={{
          position: "absolute",
          left: "50%",
          top: 30,
          transform: "translateX(-50%)",
        }}
      >
        Analysis period: {data?.start_date} - {data?.end_date}
      </CardDescription>
    </div>
  );
};

export default PortfolioPieChart;
