import { ReadyState } from "react-use-websocket";

export const formatTime = (timestamp: string): string | null => {
  const parsed = parseInt(timestamp);
  if (isNaN(parsed)) return null;
  return new Date(parsed).toLocaleTimeString("en-US", {
    timeStyle: "short",
    hour12: false,
  });
};

export const getValueColor = (value: number): string => {
  if (Math.abs(value) < 0.05) return "#6b7280";
  return value > 0 ? "#5A9D15" : "#9D2228";
};

export const getValueText = (value: number): string => {
  if (Math.abs(value) < 0.05) return "0.0%";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
};

export const getStatusColor = (
  readyState: ReadyState,
  hasData: boolean
): string => {
  if (readyState === ReadyState.CLOSED) return "#9D2228";
  if (hasData) return "#5A9D15";
  return "#B3710C";
};

export const getStatusMessage = (
  readyState: ReadyState,
  hasData: boolean
): string | null => {
  if (readyState === ReadyState.CLOSED)
    return "Connection failed • Retrying...";
  if (hasData) return null;
  return "Connecting to markets...";
};
