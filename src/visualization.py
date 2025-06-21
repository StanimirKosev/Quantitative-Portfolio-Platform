import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np


def plot_simulation_results(portfolio_paths):
    """Visualizes the results of a Monte Carlo portfolio simulation.

    This function generates a comprehensive plot displaying the outcomes of
    multiple portfolio simulation paths. It shows all individual paths with
    transparency, highlights the 90% confidence interval, and displays
    key summary statistics in a text box on the plot.

    Args:
        portfolio_paths (list or np.ndarray): A 2D sequence where each
            inner sequence represents a single simulation path of portfolio
            values over time.
    """
    portfolio_paths = np.array(portfolio_paths)

    # Create a simple plot
    plt.figure(figsize=(10, 6))

    # Plot all simulation paths
    x_values = range(len(portfolio_paths[0]))
    for i in range(len(portfolio_paths)):
        plt.plot(x_values, portfolio_paths[i], linewidth=0.5)

    # Calculate confidence intervals (5th and 95th percentiles)
    lower_bound = np.percentile(portfolio_paths, 5, axis=0)
    upper_bound = np.percentile(portfolio_paths, 95, axis=0)

    # Plot confidence interval
    plt.fill_between(
        x_values,
        lower_bound,
        upper_bound,
        color="gray",
        alpha=0.5,
        label="90% Confidence Interval",
    )

    # Calculate final statistics
    final_values = portfolio_paths[:, -1]  # Last day values
    mean_final = np.mean(final_values)
    worst_case = np.min(final_values)
    best_case = np.max(final_values)
    initial_value = portfolio_paths[0, 0]

    # Calculate percentage returns
    mean_return_pct = ((mean_final / initial_value) - 1) * 100
    worst_return_pct = ((worst_case / initial_value) - 1) * 100
    best_return_pct = ((best_case / initial_value) - 1) * 100

    # Add statistics text box
    stats_text = f"""Final Portfolio Statistics:
    Mean: ${mean_final:,.0f} ({mean_return_pct:+.1f}%)
    Best Case: ${best_case:,.0f} ({best_return_pct:+.1f}%)
    Worst Case: ${worst_case:,.0f} ({worst_return_pct:+.1f}%)
    Initial: ${initial_value:,.0f}"""

    plt.text(
        0.02,
        0.98,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.title(
        "Monte Carlo Portfolio Simulation\n1000 Possible Futures for $10,000 Investment",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("Trading Days")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.margins(x=0)  # Remove horizontal padding to fit the data snugly

    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))

    plt.tight_layout()

    plt.savefig("charts/monte_carlo_simulation.png", dpi=300, bbox_inches="tight")
    print("Chart saved to charts/monte_carlo_simulation.png")

    plt.show()
