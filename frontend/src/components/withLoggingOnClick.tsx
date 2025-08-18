import type { FC } from "react";
import type { LogPayload, LogResponse } from "../types/logging";
import { API_BASE_URL } from "../lib/api";
import { useMutation } from "@tanstack/react-query";
import { Button } from "./ui/button";

interface withLoggingOnClick {
  onClick: () => void;
  logData: Pick<LogPayload, "event" | "route" | "context">;
}

/**
 * Higher Order Component that adds automatic user interaction logging to any component.
 * Wraps components to send structured logs to backend on click events.
 * 
 * @param Component - React component to wrap with logging functionality
 * @param params - Fixed logging parameters (level: "info" | "error" | "fatal")
 * @returns Enhanced component that logs clicks with event, route, and context data
 */
const withLoggingOnClick = <P extends object>(
  Component: FC<P>,
  params: Pick<LogPayload, "level">
): FC<P & withLoggingOnClick> => {
  return ({ logData, ...props }) => {
    const sendLogToBackend = async (payload: LogPayload) => {
      const response = await fetch(`${API_BASE_URL}/api/logs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP ${response.status}: ${errorData.detail}`);
      }

      return response.json();
    };

    const { mutate: log } = useMutation<LogResponse, Error, LogPayload>({
      mutationFn: sendLogToBackend,
    });

    const onClick = () => {
      log({
        ...logData,
        ...params,
        timestamp: new Date().toISOString(),
      });

      props.onClick();
    };

    return <Component {...(props as P)} onClick={onClick} />;
  };
};

export const ButtonWithLoggingOnClick = withLoggingOnClick(Button, {
  level: "info",
});
