import {
  XAxis,
  YAxis,
  CartesianGrid,
  Scatter,
  ResponsiveContainer,
  ScatterChart,
  Tooltip,
} from "recharts";
import { CarouselItem } from "./ui/carousel";
import { Card, CardContent } from "./ui/card";
import { useQuery } from "@tanstack/react-query";
import type { PortfolioOptimizationResponse } from "../types/optimization";
import { useRegimeStore } from "../store/regimeStore";
import { API_BASE_URL } from "../lib/api";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import FrontierTooltip from "./FrontierTooltip";

const CHART_COLORS = {
  BLUE: "#2E6BA5",
  ORANGE: "#C8511F",
} as const;

const EfficientFrontierSlide = () => {
  const { selectedRegime } = useRegimeStore();
  const { customPortfolioOptimization, isCustomStateActive } =
    useCustomPortfolioStore();

  const { data: defaultPortfolioOptimization } =
    useQuery<PortfolioOptimizationResponse>({
      queryKey: ["optimize", "default", selectedRegime],
      queryFn: async () => {
        const res = await fetch(
          `${API_BASE_URL}/api/optimize/${selectedRegime}`,
          {
            method: "POST",
          }
        );
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(`HTTP ${res.status}: ${errorData.detail}`);
        }
        return res.json();
      },
      enabled: !!selectedRegime && !isCustomStateActive(),
    });

  const dataSource =
    customPortfolioOptimization || defaultPortfolioOptimization;

  return (
    <CarouselItem className="px-12 sm:px-16">
      <Card className="flex flex-col h-full bg-black">
        <CardContent className="flex flex-col flex-1 p-2 sm:p-4 gap-2 justify-center items-center">
          <div className="text-center py-6">
            <h3 className="text-white text-xl font-semibold">
              Efficient Frontier - Risk vs Return
            </h3>
            <p className="text-gray-400 text-sm">
              Each point represents an optimal portfolio for its risk level
            </p>
          </div>

          <div className="w-full h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{
                  right: 40,
                  bottom: 25,
                  left: 40,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  type="number"
                  dataKey="volatility_pct"
                  name="Risk (Volatility %)"
                  stroke="#9CA3AF"
                  label={{
                    value: "Risk (Volatility %)",
                    position: "insideBottom",
                    offset: -20,
                    style: { textAnchor: "middle", fill: "#9CA3AF" },
                  }}
                />
                <YAxis
                  type="number"
                  dataKey="return_pct"
                  name="Expected Return (%)"
                  stroke="#9CA3AF"
                  label={{
                    value: "Expected Return (%)",
                    angle: -90,
                    position: "insideLeft",
                    style: { textAnchor: "middle", fill: "#9CA3AF" },
                  }}
                />
                <Tooltip
                  content={<FrontierTooltip />}
                  cursor={{
                    strokeDasharray: "5 5",
                    stroke: "#6B7280",
                    strokeWidth: 1,
                  }}
                />

                <Scatter
                  name="Efficient Frontier"
                  data={dataSource?.frontier_points}
                  fill={CHART_COLORS.BLUE}
                  line={{ stroke: CHART_COLORS.BLUE, strokeWidth: 2.5 }}
                  shape={(props: { cx?: number; cy?: number }) => {
                    const { cx, cy } = props;
                    return (
                      <circle cx={cx} cy={cy} r={6} fill={CHART_COLORS.BLUE} />
                    );
                  }}
                />

                <Scatter
                  name="Maximum Sharpe Ratio"
                  data={[dataSource?.max_sharpe_point]}
                  fill={CHART_COLORS.ORANGE}
                  shape={(props: { cx?: number; cy?: number }) => {
                    const { cx, cy } = props;
                    return (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={8}
                        fill={CHART_COLORS.ORANGE}
                      />
                    );
                  }}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          <div className="flex justify-center gap-6 text-base py-2">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: CHART_COLORS.BLUE }}
              ></div>
              <span
                className="font-semibold"
                style={{ color: CHART_COLORS.BLUE }}
              >
                Efficient Frontier
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: CHART_COLORS.ORANGE }}
              ></div>
              <span
                className="font-semibold"
                style={{ color: CHART_COLORS.ORANGE }}
              >
                Maximum Sharpe Ratio
              </span>
            </div>
          </div>

          <div className="text-gray-400 text-xs sm:text-sm text-center">
            Risk-free rate: {dataSource?.risk_free_rate_pct}%
          </div>
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default EfficientFrontierSlide;
