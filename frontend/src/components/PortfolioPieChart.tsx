import type { PortfolioAsset } from "../types/portfolio";
import { CardHeader, CardTitle } from "./ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";
import { Legend, Pie, PieChart } from "recharts";
import { useRegimeStore } from "../store/regimeStore";
import type { FC } from "react";

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
  container:
    "flex flex-col items-center justify-center w-full lg:w-2/5 min-h-[250px] sm:min-h-[300px]",
  title: "text-lg sm:text-xl lg:text-2xl mb-2",
  chartContainer:
    "mx-auto aspect-square w-full max-w-[280px] sm:max-w-[350px] lg:max-w-[380px] p-2 sm:p-4",
};
interface Props {
  portfolioAssets: PortfolioAsset[] | undefined;
}

const PortfolioPieChart: FC<Props> = ({ portfolioAssets }) => {
  const { selectedRegime } = useRegimeStore();

  const assets = portfolioAssets?.map((asset, idx) => ({
    ...asset,
    ticker_pct: `${asset.ticker}: ${asset.weight_pct}%`,
    fill: COLORS[idx % COLORS.length],
  }));

  return (
    <div className={pieChartStyles.container}>
      <CardHeader className="items-center pb-0 pt-0">
        <CardTitle className={pieChartStyles.title}>
          Portfolio Composition
        </CardTitle>
      </CardHeader>
      <ChartContainer config={{}} className={pieChartStyles.chartContainer}>
        <PieChart
          key={
            selectedRegime
          } /**Key - Reset animation state when regime changes */
        >
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
              padding: "12px 0",
            }}
          />
        </PieChart>
      </ChartContainer>
    </div>
  );
};

export default PortfolioPieChart;
