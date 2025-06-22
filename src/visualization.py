import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from monte_carlo import calculate_simulation_statistics, calculate_risk_metrics


def plot_simulation_results(portfolio_paths, regime_name=None):
    """Visualizes the results of a Monte Carlo portfolio simulation with percentile bands and key paths.

    This function generates a professional plot displaying the outcomes of multiple portfolio
    simulation paths using percentile bands instead of individual lines. It shows confidence
    intervals (50%, 80%, and 90%) as filled areas, highlights the median path as the most
    likely scenario, and displays best-case and worst-case paths in distinct colors.

    Args:
        portfolio_paths (list or np.ndarray): A 2D sequence where each inner sequence
            represents a single simulation path of portfolio values over time.
        regime_name (str, optional): Name of the macroeconomic regime for title and filename.

    Features:
        - Three percentile bands showing different confidence intervals
        - Median path highlighted as the most likely scenario
        - Best-case and worst-case paths in green and red respectively
        - Professional color scheme with blue gradient bands
        - Enhanced statistics box with median, mean, and risk metrics
    """

    stats = calculate_simulation_statistics(portfolio_paths)

    portfolio_paths = np.array(portfolio_paths)
    plt.figure(figsize=(10, 6))
    x_values = range(len(portfolio_paths[0]))

    percentiles = stats["percentiles"]

    # 5th-95th percentile band (90% confidence interval)
    plt.fill_between(
        x_values,
        percentiles[0],
        percentiles[6],
        color="lightblue",
        alpha=0.3,
        label="90% Confidence Interval",
    )

    # 10th-90th percentile band (80% confidence interval)
    plt.fill_between(
        x_values,
        percentiles[1],
        percentiles[5],
        color="skyblue",
        alpha=0.4,
        label="80% Confidence Interval",
    )

    # 25th-75th percentile band (50% confidence interval)
    plt.fill_between(
        x_values,
        percentiles[2],
        percentiles[4],
        color="steelblue",
        alpha=0.5,
        label="50% Confidence Interval",
    )

    # Plot key paths using pre-calculated indices
    path_indices = stats["path_indices"]

    plt.plot(
        x_values,
        portfolio_paths[path_indices["median"]],
        color="navy",
        linewidth=3,
        label="Median Path",
        zorder=5,
    )
    plt.plot(
        x_values,
        portfolio_paths[path_indices["best"]],
        color="darkgreen",
        linewidth=2,
        label="Best Case",
        zorder=4,
    )
    plt.plot(
        x_values,
        portfolio_paths[path_indices["worst"]],
        color="darkred",
        linewidth=2,
        label="Worst Case",
        zorder=4,
    )

    perf_stats = stats["performance_stats"]

    risk_metrics = calculate_risk_metrics(portfolio_paths)

    stats_text = f"""Portfolio Performance & Risk Metrics:
    
    Performance:
    • Median: ${perf_stats['median_final']:,.0f} ({perf_stats['median_return_pct']:+.1f}%)
    • Mean: ${perf_stats['mean_final']:,.0f} ({perf_stats['mean_return_pct']:+.1f}%)
    • Best Case: ${perf_stats['best_final']:,.0f} ({perf_stats['best_return_pct']:+.1f}%)
    • Worst Case: ${perf_stats['worst_final']:,.0f} ({perf_stats['worst_return_pct']:+.1f}%)
    • Initial: ${perf_stats['initial_value']:,.0f}

    Risk Metrics:
    • 95% VaR: ${risk_metrics['var_95']:,.0f} ({risk_metrics['var_95_pct']:+.1f}%)
    • 99% VaR: ${risk_metrics['var_99']:,.0f} ({risk_metrics['var_99_pct']:+.1f}%)
    • 95% CVaR: ${risk_metrics['cvar_95']:,.0f} ({risk_metrics['cvar_95_pct']:+.1f}%)
    • 99% CVaR: ${risk_metrics['cvar_99']:,.0f} ({risk_metrics['cvar_99_pct']:+.1f}%)"""

    plt.text(
        0.02,
        0.98,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9
        ),
    )

    plt.title(
        f"Monte Carlo Portfolio Simulation: \n{len(portfolio_paths)} Scenarios Over {x_values[-1]} Trading Days"
        + (f" - {regime_name}" if regime_name else ""),
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("Trading Days", fontsize=12)
    plt.ylabel("Portfolio Value ($)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.margins(x=0)  # Remove horizontal padding to fit the data snugly

    # Format y-axis as currency
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))

    plt.tight_layout()

    filename = "monte_carlo_simulation"
    if regime_name:
        clean_name = regime_name.replace(" ", "_").replace(":", "").replace("-", "_")
        filename = f"monte_carlo_simulation_{clean_name.lower()}"

    plt.savefig(f"charts/{filename}.png", dpi=300, bbox_inches="tight")
    plt.show()
