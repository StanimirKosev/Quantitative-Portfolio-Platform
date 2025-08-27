import { useEffect, useState, type FC } from "react";
import useWebSocket from "react-use-websocket";
import type { StockQuote } from "../types/livePrice";
import { Circle } from "lucide-react";
import type { PortfolioAsset } from "../types/portfolio";
import {
  formatTime,
  getStatusColor,
  getStatusMessage,
  getValueColor,
  getValueText,
} from "../lib/livePriceUtils";
import { API_BASE_URL } from "../lib/api";

interface Props {
  portfolioAssets: PortfolioAsset[] | undefined;
}

const LivePriceWidget: FC<Props> = ({ portfolioAssets }) => {
  const [livePrices, setLivePrices] = useState<
    Record<string, Pick<StockQuote, "market_hours" | "change_percent">>
  >({});
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const wsUrl =
    API_BASE_URL.replace(/^https:/, "wss:").replace(/^http:/, "ws:") +
    "/api/ws/live-prices";
  const { lastJsonMessage, sendJsonMessage, readyState } =
    useWebSocket<StockQuote | null>(wsUrl, { shouldReconnect: () => true });

  useEffect(() => {
    if (readyState !== 1) return;

    const tickers = portfolioAssets?.map((asset) => asset.ticker);
    if (tickers?.length) {
      sendJsonMessage(tickers);
    }
  }, [portfolioAssets, sendJsonMessage, readyState]);

  useEffect(() => {
    if (!lastJsonMessage?.id) return;

    setLivePrices((prev) => ({
      ...prev,
      [lastJsonMessage.id]: {
        change_percent: lastJsonMessage.change_percent ?? 0,
        market_hours: lastJsonMessage.market_hours ?? 0,
      },
    }));

    setLastUpdated((prev) =>
      !prev || lastJsonMessage.time > prev ? lastJsonMessage.time : prev
    );
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
          <span>{lastUpdated ? formatTime(lastUpdated) : null}</span>
        </>
      )}
    </div>
  );
};

export default LivePriceWidget;
