import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from monte_carlo import (
    analyze_portfolio_correlation,
    analyze_portfolio_risk_factors,
    calculate_simulation_statistics,
    calculate_risk_metrics,
)
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


def plot_correlation_heatmap(cov_matrix, regime_name):
    """
    Plot a heatmap of the portfolio's correlation matrix using seaborn, with conditioning diagnostics.

    Parameters:
        cov_matrix (pd.DataFrame): Covariance matrix of asset returns (assets as both rows and columns).
        regime_name (str): Scenario name (e.g., 'historical', 'fiat_debasement', 'geopolitical_crisis') for plot title and file naming.

    The function computes the correlation matrix and its condition number, then visualizes the matrix as a heatmap with annotations. An info panel below the plot summarizes the matrix's conditioning status.
    """
    analysis = analyze_portfolio_correlation(cov_matrix)
    corr_matrix = analysis["correlation_matrix"]
    condition_number = analysis["condition_number"]

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


def plot_portfolio_pca_analysis(cov_matrix, regime_name):
    """
    Visualize principal component analysis (PCA) results for a portfolio as a risk factor bar chart.

    This function plots the eigenvalues of the portfolio's covariance (or correlation) matrix as a bar chart, highlighting dominant risk factors (principal components with eigenvalue > 1.0) in a distinct color. For each dominant factor, it annotates the bar with the top contributing assets (those with >10% loading or at least the top 2), stacking their names and percentage contributions proportionally within the bar. An information panel summarizes the number of dominant factors, total explained variance, and other key statistics.

    Parameters:
        corr_matrix_analysis (dict): Output of analyze_portfolio_risk_factors(), containing:
            - 'eigenvalues': array-like, eigenvalues of the matrix
            - 'dominant_factor_loadings' (or 'dominant_factor_loadings'): dict mapping PC index to list of top asset contributors
            - 'explained_variance_dominant' (or 'explained_variance_dominant'): float, total explained variance by dominant PCs
        regime_name (str): Scenario name (e.g., 'historical', 'fiat_debasement', 'geopolitical_crisis') for plot title and file naming.

    Features:
        - Bars colored by dominance (eigenvalue > 1.0)
        - Asset labels stacked within each dominant bar, proportional to their contribution
        - Info panel with summary statistics
        - Saves the figure with a scenario-specific filename
    """
    analysis = analyze_portfolio_risk_factors(cov_matrix)
    eigenvalues = np.array(analysis["eigenvalues"])
    dominant_factor_loadings = analysis["dominant_factor_loadings"]
    explained_variance_dominant = analysis["explained_variance_dominant"]

    DOMINANT_COLOR = "#c41e3a"
    MINOR_COLOR = "#6fa8dc"
    colors = [DOMINANT_COLOR if val > 1.0 else MINOR_COLOR for val in eigenvalues]

    plt.figure(figsize=(8, 6))

    # Draw a horizontal line at y=1.0 to indicate the dominance threshold
    plt.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, linewidth=1)

    plt.xlabel("Principal Component", fontsize=12)
    plt.ylabel("Eigenvalue (λ)", fontsize=12)
    plt.title(
        f"Portfolio Risk Factor Analysis - {regime_name.title()}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    plt.xticks(range(1, len(eigenvalues) + 1))
    plt.grid(axis="y", alpha=0.3)

    # Set y-axis to start at 0 for better visual proportion
    plt.ylim(0, max(eigenvalues) * 1.1)

    info_panel_text = (
        f"Risk Factor Summary:\n"
        f"• Dominant Factors: {len(dominant_factor_loadings)} (eigenvalue > 1.0)\n"
        f"• Explained Variance: {explained_variance_dominant:.1f}%\n"
        f"• Asset Loadings: Major contributors (>10%)\n"
        f"• Total Components: {len(eigenvalues)}"
    )

    plt.gca().text(
        0.5,
        0.98,
        info_panel_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        horizontalalignment="left",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9
        ),
    )

    bars = plt.bar(
        range(1, len(eigenvalues) + 1),
        eigenvalues,
        color=colors,
        edgecolor="black",
        linewidth=0.5,
    )

    # Annotate each dominant PC bar with its top contributing assets
    for pc_number, pc_assets in dominant_factor_loadings.items():
        bar = bars[pc_number - 1]
        y_start = 0

        for asset in pc_assets:
            asset_height = eigenvalues[pc_number - 1] * (asset["pct"] / 100)
            y_pos = y_start + asset_height / 2
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                f"{asset['asset']} {asset['pct']:.0f}%",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    alpha=0.9,
                    edgecolor="gray",
                ),
            )
            y_start += asset_height  # Stack asset labels within the bar

    plt.tight_layout()
    save_figure(regime_name, "risk_factor_analysis", "png")
    plt.show()
