import { Check, LoaderCircle } from "lucide-react";
import { Progress } from "./ui/progress";
import { type FC, type ReactNode } from "react";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";
import { createPortal } from "react-dom";

interface Props {
  children: ReactNode;
}

const PortfolioAnalysisLoader: FC<Props> = ({ children }) => {
  const simulationsLoading =
    useIsFetching({ queryKey: ["simulate", "default"] }) +
    useIsMutating({ mutationKey: ["simulate", "custom"] });

  const optimizationsLoading =
    // Include default portfolio fetch with optimization
    useIsFetching({ queryKey: ["optimize", "default"] }) +
    useIsFetching({ queryKey: ["portfolio", "default"] }) +
    useIsMutating({ mutationKey: ["optimize", "custom"] });

  const loadingSteps = [
    {
      key: "optimize",
      label: "Calculating efficient frontier",
      isLoading: optimizationsLoading > 0,
      isComplete: optimizationsLoading === 0,
    },
    {
      key: "simulate",
      label: "Running Monte Carlo simulation",
      isLoading: simulationsLoading > 0,
      isComplete: simulationsLoading === 0,
    },
  ];

  const completedCount = loadingSteps.filter((s) => s.isComplete).length;
  const progressValue = (completedCount / loadingSteps.length) * 100;

  const shouldShowModal = progressValue < 100;

  return (
    <>
      {children}
      {shouldShowModal
        ? createPortal(
            <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-in fade-in-0 duration-300">
              <div className="bg-card p-6 sm:p-8 rounded-xl border shadow-xl max-w-md w-full mx-4 animate-in fade-in-0 zoom-in-95 duration-300">
                <h3 className="text-lg font-semibold mb-6 text-center">
                  Analyzing Portfolio
                </h3>

                <div className="space-y-4" role="status" aria-live="polite">
                  {loadingSteps.map((step, index) => (
                    <div
                      key={step.key}
                      className="flex items-center gap-3 transition-all duration-300 ease-in-out"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="relative">
                        {step.isComplete ? (
                          <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center animate-in zoom-in-75 duration-200">
                            <Check className="w-3 h-3 text-white" />
                          </div>
                        ) : (
                          <LoaderCircle className="animate-spin w-6 h-6 text-primary" />
                        )}
                      </div>

                      <span
                        className={`text-sm transition-colors duration-200 ${
                          step.isComplete
                            ? "text-green-600 font-medium"
                            : "text-primary font-medium"
                        }`}
                      >
                        {step.label}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="mt-6">
                  <Progress
                    value={progressValue}
                    className="transition-all duration-700 ease-out"
                    aria-label={`Progress: ${Math.round(progressValue)}%`}
                  />
                  <p className="text-xs text-muted-foreground text-center mt-2">
                    {Math.round(progressValue)}% complete
                  </p>
                </div>
              </div>
            </div>,
            document.body
          )
        : null}
    </>
  );
};

export default PortfolioAnalysisLoader;
