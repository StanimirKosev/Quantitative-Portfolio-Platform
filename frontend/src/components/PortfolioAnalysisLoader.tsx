import { Check } from "lucide-react";
import { Progress } from "./ui/progress";
import { type FC, type ReactNode } from "react";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";

interface Props {
  children: ReactNode;
}

const styles = {
  container: "relative",
  overlay:
    "absolute inset-0 flex items-center justify-center z-50 animate-in fade-in-0 duration-300 backdrop-blur-sm",
  modal:
    "bg-card p-4 sm:p-6 md:p-8 rounded-2xl border shadow-2xl max-w-sm sm:max-w-md w-full mx-3 sm:mx-4 animate-in fade-in-0 zoom-in-95 duration-300 slide-in-from-bottom-8 sm:slide-in-from-bottom-0",
  title:
    "text-base sm:text-lg font-semibold mb-4 sm:mb-6 text-center leading-tight",
  stepsContainer: "space-y-3 sm:space-y-4",
  stepItem:
    "flex items-center gap-3 transition-all duration-300 ease-in-out animate-in slide-in-from-left-4",
  iconContainer: "relative flex-shrink-0",
  completedIcon:
    "w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-green-500 flex items-center justify-center animate-in zoom-in-75 duration-200 ring-2 ring-green-500/20",
  checkIcon: "w-2.5 h-2.5 sm:w-3 sm:h-3 text-white",
  loadingIconContainer: "relative w-5 h-5 sm:w-6 sm:h-6",
  loadingIcon:
    "w-full h-full rounded-full border-2 border-t-primary border-l-primary border-b-transparent border-r-transparent animate-spin",
  loadingRing:
    "absolute inset-0 rounded-full border border-primary/10 animate-pulse",
  stepLabelCompleted:
    "text-xs sm:text-sm transition-colors duration-200 leading-relaxed text-green-600 font-medium",
  stepLabelLoading:
    "text-xs sm:text-sm transition-colors duration-200 leading-relaxed text-primary font-medium",
  progressContainer: "mt-4 sm:mt-6",
  progressBar: "transition-all duration-700 ease-out h-2 sm:h-2.5",
  progressText: "text-xs text-muted-foreground text-center mt-2 font-medium",
};

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
    <div className={styles.container}>
      {children}
      {shouldShowModal ? (
        <div
          className={styles.overlay}
          style={{ backgroundColor: "hsl(var(--background) / 0.9)" }}
        >
          <div className={styles.modal}>
            <h3 className={styles.title}>Analyzing Portfolio</h3>

            <div
              className={styles.stepsContainer}
              role="status"
              aria-live="polite"
            >
              {loadingSteps.map((step, index) => (
                <div
                  key={step.key}
                  className={styles.stepItem}
                  style={{
                    animationDelay: `${index * 150}ms`,
                    animationFillMode: "both",
                  }}
                >
                  <div className={styles.iconContainer}>
                    {step.isComplete ? (
                      <div className={styles.completedIcon}>
                        <Check className={styles.checkIcon} />
                      </div>
                    ) : (
                      <div className={styles.loadingIconContainer}>
                        <div className={styles.loadingIcon} />
                        <div className={styles.loadingRing} />
                      </div>
                    )}
                  </div>

                  <span
                    className={
                      step.isComplete
                        ? styles.stepLabelCompleted
                        : styles.stepLabelLoading
                    }
                  >
                    {step.label}
                  </span>
                </div>
              ))}
            </div>

            <div className={styles.progressContainer}>
              <Progress
                value={progressValue}
                className={styles.progressBar}
                aria-label={`Progress: ${Math.round(progressValue)}%`}
              />
              <p className={styles.progressText}>
                {Math.round(progressValue)}% complete
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default PortfolioAnalysisLoader;
