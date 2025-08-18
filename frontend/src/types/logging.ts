export interface LogPayload {
  event: string;
  level: "info" | "error" | "fatal";
  timestamp: string;
  route?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  context?: Record<string, any>;
}

export interface LogResponse {
  status: string;
}
