import type {
  EfficientFrontierPoint,
  MaxSharpePoint,
} from "../types/optimization";

const FrontierTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: EfficientFrontierPoint | MaxSharpePoint }>;
}) => {
  if (!(active && payload && payload.length)) return null;

  const data = payload[0].payload;
  const isMaxSharpe = "sharpe_ratio" in data;

  return (
    <div className="bg-gray-800 text-white p-3 rounded-lg border border-gray-600 shadow-lg">
      {isMaxSharpe && (
        <div className="text-orange-400 font-bold mb-2">
          🎯 OPTIMAL PORTFOLIO
        </div>
      )}
      <div>Expected Return: {data.return_pct}%</div>
      <div>Risk (Volatility): {data.volatility_pct}%</div>
      {isMaxSharpe && <div>Sharpe Ratio: {data.sharpe_ratio} (Maximum)</div>}
      {data.weights_pct && (
        <div className="mt-2">
          <div className="font-semibold">Portfolio Weights:</div>
          {data.weights_pct.map((weight: number, idx: number) => (
            <div key={idx} className="text-sm">
              {data?.tickers[idx]}: {weight}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FrontierTooltip;
