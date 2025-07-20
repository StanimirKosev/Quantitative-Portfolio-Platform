import { useQuery } from "@tanstack/react-query";
import { CarouselItem } from "./ui/carousel";
import type { DefaultPortfolioResponse } from "../types/portfolio";

import { Pie, PieChart, Legend } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";

const COLORS = [
  "#5C7CFA", // Periwinkle Blue
  "#51CF66", // Mint Green
  "#FFD43B", // Soft Yellow
  "#FF6B6B", // Coral Red
  "#74C0FC", // Light Blue
  "#C084FC", // Soft Purple
  "#FFB84D", // Orange
  "#69DB7C", // Light Green
];

const PortfolioOverviewSlide = () => {
  const apiUrl = import.meta.env.VITE_API_URL;

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
    <CarouselItem>
      <Card className="flex flex-col h-full">
        <CardContent className="flex flex-row flex-1 pb-0">
          <div className="flex flex-col items-center justify-center w-2/5">
            <CardHeader className="items-center pb-0">
              <CardTitle className="text-2xl mb-2">
                Portfolio Composition
              </CardTitle>
            </CardHeader>
            <ChartContainer
              config={{}}
              className="mx-auto aspect-square w-full max-w-[380px] p-4"
            >
              <PieChart>
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
          </div>
          {/* Regime info on the right, 60% width */}
          <div className="flex flex-col items-center justify-center w-3/5">
            <div className="text-5xl font-bold mb-2">60%</div>
            <div className="text-2xl font-semibold">Regime Name</div>
            <CardDescription>
              Analysis period: {data?.start_date} - {data?.end_date}
            </CardDescription>
          </div>
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default PortfolioOverviewSlide;
