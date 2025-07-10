import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from monte_carlo import calculate_simulation_statistics, calculate_risk_metrics
import seaborn as sns
from utils import save_figure


def plot_simulation_results(portfolio_paths, regime_name):
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
    • Median: €{perf_stats['median_final']:,.0f} ({perf_stats['median_return_pct']:+.1f}%)
    • Mean: €{perf_stats['mean_final']:,.0f} ({perf_stats['mean_return_pct']:+.1f}%)
    • Best Case: €{perf_stats['best_final']:,.0f} ({perf_stats['best_return_pct']:+.1f}%)
    • Worst Case: €{perf_stats['worst_final']:,.0f} ({perf_stats['worst_return_pct']:+.1f}%)
    • Initial: €{perf_stats['initial_value']:,.0f}

    Risk Metrics:
    • 95% VaR: €{risk_metrics['var_95']:,.0f} ({risk_metrics['var_95_pct']:+.1f}%)
    • 99% VaR: €{risk_metrics['var_99']:,.0f} ({risk_metrics['var_99_pct']:+.1f}%)
    • 95% CVaR: €{risk_metrics['cvar_95']:,.0f} ({risk_metrics['cvar_95_pct']:+.1f}%)
    • 99% CVaR: €{risk_metrics['cvar_99']:,.0f} ({risk_metrics['cvar_99_pct']:+.1f}%)"""

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
    plt.ylabel("Portfolio Value (€)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.margins(x=0)  # Remove horizontal padding to fit the data snugly

    # Format y-axis as currency
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"€{x:,.0f}"))

    plt.tight_layout()

    save_figure(regime_name, "monte_carlo_simulation", "png")
    plt.show()


def plot_correlation_heatmap(corr_matrix_analysis, regime_name):
    """
    Plot a heatmap of the correlation matrix using seaborn.

    Parameters:
        corr_matrix_analysis (dict): Output of get_cov_matrix_analysis(), containing correlation matrix and related stats.
        regime_name (str): Scenario name (e.g., 'historical', 'fiat_debasement', 'geopolitical_crisis').
        title (str, optional): Title for the plot.
    """
    corr_matrix = corr_matrix_analysis["correlation_matrix"]
    condition_number = corr_matrix_analysis["condition_number"]

    # Determine conditioning status (arbitrary threshold: < 100 is 'Well', else 'Poorly')
    if condition_number < 0:
        cond_status = "Invalid (Negative Eigenvalues)"
    elif condition_number < 100:
        cond_status = "Well Conditioned"
    else:
        cond_status = "Poorly Conditioned"

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        cbar_kws={"shrink": 0.8},
        linewidths=0.5,
        linecolor="white",
    )
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.title(
        f"Portfolio Correlation Matrix - {regime_name.title()}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    stats_text = (
        f"Conditioning Number: {condition_number:.2f}\n" f"Status: {cond_status}\n"
    )
    plt.tight_layout()

    plt.subplots_adjust(bottom=0.18)  # Make space for text below the plot
    plt.figtext(0.01, 0.01, stats_text, ha="left", va="bottom", fontsize=10)

    save_figure(regime_name, "correlation_matrix", "png")
    plt.show()


def plot_eigenvalues(corr_matrix_analysis, regime_name):
    """
    Plot a bar chart of eigenvalues (sorted), highlighting dominant factors (>1.0),
    and display a single interpretation box with:
    - Number of dominant factors
    - Total explained variance by dominant factors
    - Top 2 contributing assets for each dominant principal component

    Parameters:
        corr_matrix_analysis (dict): Output of get_cov_matrix_analysis(), containing eigenvalues, explained variance, dominant_pc_top_assets, and explained_variance_by_dominant_pct.
        regime_name (str): Scenario name (e.g., 'historical', 'fiat_debasement', 'geopolitical_crisis').
    """
    eigenvalues = np.array(corr_matrix_analysis["eigenvalues"])
    dominant_pc_top_assets = corr_matrix_analysis["dominant_pc_top_assets"]
    explained_variance_by_dominant_pct = corr_matrix_analysis[
        "explained_variance_by_dominant_pct"
    ]

    # Color scheme: dominant factors (>1.0) in red, others in light blue
    colors = ["#b22222" if val > 1.0 else "#87aade" for val in eigenvalues]

    plt.figure(figsize=(8, 6))
    plt.bar(
        range(1, len(eigenvalues) + 1),
        eigenvalues,
        color=colors,
        edgecolor="black",
        linewidth=0.5,
    )

    # Add horizontal line at y=1.0 to show dominance threshold
    plt.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, linewidth=1)

    plt.xlabel("Principal Component", fontsize=12)
    plt.ylabel("Eigenvalue", fontsize=12)
    plt.title(
        f"Portfolio Covariance Eigenvalue Spectrum - {regime_name.title()}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Clean up axes
    plt.xticks(range(1, len(eigenvalues) + 1))
    plt.grid(axis="y", alpha=0.3)

    # Set y-axis to start at 0 for better visual proportion
    plt.ylim(0, max(eigenvalues) * 1.1)

    interp_text = (
        f"Dominant Factors: {len(dominant_pc_top_assets)}\n"
        f"Explained Variance: {explained_variance_by_dominant_pct:.1f}%\n"
        f"(Eigenvalues > 1.0 are dominant factors)\n"
        f"Top contributing assets:\n" + "\n".join(dominant_pc_top_assets)
    )

    plt.gca().text(
        0.98,
        0.98,
        interp_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9
        ),
    )

    plt.tight_layout()
    save_figure(regime_name, "eigenvalue_analysis", "png")
    plt.show()
