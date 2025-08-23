import { useEffect, useState, type FC } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import type { StockQuote } from "../types/livePrice";
import { Circle } from "lucide-react";
import type { PortfolioAsset } from "../types/portfolio";

// Helper functions
const formatTime = (timestamp: string): string | null => {
  const parsed = parseInt(timestamp);
  if (isNaN(parsed)) return null;
  return new Date(parsed).toLocaleTimeString("en-US", {
    timeStyle: "short",
    hour12: false,
  });
};

const getValueColor = (value: number): string => {
  if (Math.abs(value) < 0.05) return "#6b7280";
  return value > 0 ? "#5A9D15" : "#9D2228";
};

const getValueText = (value: number): string => {
  if (Math.abs(value) < 0.05) return "0.0%";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
};

const getStatusColor = (readyState: ReadyState, hasData: boolean): string => {
  if (readyState === ReadyState.CLOSED) return "#9D2228";
  if (hasData) return "#5A9D15";
  return "#B3710C";
};

const getStatusMessage = (
  readyState: ReadyState,
  hasData: boolean
): string | null => {
  if (readyState === ReadyState.CLOSED)
    return "Connection failed • Retrying...";
  if (hasData) return null;
  return "Connecting to markets...";
};

interface Props {
  portfolioAssets: PortfolioAsset[] | undefined;
}

const LivePriceWidget: FC<Props> = ({ portfolioAssets }) => {
  const [livePrices, setLivePrices] = useState<
    Record<string, Pick<StockQuote, "market_hours" | "change_percent">>
  >({});
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const { lastJsonMessage, sendJsonMessage, readyState } =
    useWebSocket<StockQuote | null>("ws://localhost:8000/api/ws/live-prices");

  useEffect(() => {
    const tickers = portfolioAssets?.map((asset) => asset.ticker);
    if (tickers?.length) {
      sendJsonMessage(tickers);
    }
  }, [portfolioAssets, sendJsonMessage]);

  useEffect(() => {
    if (!lastJsonMessage?.id) return;

    setLivePrices((prev) => ({
      ...prev,
      [lastJsonMessage.id]: {
        change_percent: lastJsonMessage.change_percent ?? 0,
        market_hours: lastJsonMessage.market_hours ?? 0,
      },
    }));

    setLastUpdated(formatTime(lastJsonMessage.time));
  }, [lastJsonMessage]);

  // Calculate metrics
  const totalAssets = portfolioAssets?.length || 0;

  const totalTrading = Object.values(livePrices).filter(
    (price) => price.market_hours === 1
  ).length;

  const totalValue =
    portfolioAssets?.reduce((sum, asset) => {
      const priceData = livePrices[asset.ticker];
      if (!priceData || priceData.market_hours !== 1) return sum;

      return sum + ((priceData.change_percent ?? 0) * asset.weight_pct) / 100;
    }, 0) || 0;

  // Status calculation
  const hasLiveData = Boolean(lastUpdated && totalTrading > 0);
  const statusColor = getStatusColor(readyState, hasLiveData);
  const statusMessage = getStatusMessage(readyState, hasLiveData);

  return (
    <div className="flex items-center space-x-2 text-xs sm:text-sm text-muted-foreground">
      <Circle
        className="w-4 h-4 fill-current animate-pulse"
        style={{ color: statusColor }}
      />
      <span>LIVE</span>
      <span>•</span>
      {statusMessage ? (
        <span>{statusMessage}</span>
      ) : (
        <>
          <span
            className="text-base font-semibold"
            style={{ color: getValueColor(totalValue) }}
          >
            {getValueText(totalValue)}
          </span>
          <span>•</span>
          <span>
            {totalTrading}/{totalAssets} trading
          </span>
          <span>•</span>
          <span>{lastUpdated}</span>
        </>
      )}
    </div>
  );
};

export default LivePriceWidget;
