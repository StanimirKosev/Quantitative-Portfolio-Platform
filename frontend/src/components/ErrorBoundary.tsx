import type { ReactNode, ErrorInfo } from "react";
import { Component } from "react";
import ErrorPage from "./ErrorPage";
import type { LogPayload } from "../types/logging";
import { API_BASE_URL } from "../lib/api";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Error caught by boundary:", error);
    console.error("Component stack:", errorInfo.componentStack);

    // Log crash to backend
    this.logErrorToBackend(error, errorInfo);
  }

  private async logErrorToBackend(error: Error, errorInfo: ErrorInfo) {
    try {
      const logPayload: LogPayload = {
        event: "component_crash",
        level: "fatal",
        timestamp: new Date().toISOString(),
        route: window.location.pathname,
        context: {
          error_message: error.message,
          error_name: error.name,
          error_stack: error.stack,
          component_stack: errorInfo.componentStack,
          user_agent: navigator.userAgent,
        },
      };

      await fetch(`${API_BASE_URL}/api/logs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(logPayload),
      });
    } catch (logError) {
      console.error("Failed to log error to backend:", logError);
    }
  }

  render() {
    if (this.state.hasError) {
      return <ErrorPage error={this.state.error} />;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
