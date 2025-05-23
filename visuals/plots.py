import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from matplotlib.ticker import FuncFormatter

import plotly.io as pio
pio.renderers.default = "iframe"


def format_thousands(x, pos):
    return f'{int(x/1000)}K' if x >= 1000 else int(x)


def plot_snapshot_metrics(data, width=5, height=3.5, metrics=["Graduates", "Tuition", "Median income"]):
    latest_year = data["Year"].max()
    latest_data = data[data["Year"] == latest_year].copy()

    fig, axes = plt.subplots(1, len(metrics), figsize=(4 * len(metrics), 3.5), sharey=True)

    for i, metric in enumerate(metrics):
        ax = axes[i]
        
        # Sort data by current metric
        sorted_data = latest_data.sort_values(by=metric, ascending=True)
        fields_order = sorted_data["Field of study"]

        # Plot
        bars = ax.barh(
            y=fields_order,
            width=sorted_data[metric].values
        )

        # Format x-axis ticks as '1K'
        ax.xaxis.set_major_formatter(FuncFormatter(format_thousands))

        # Titles and labels
        ax.set_title(f"{metric} ({latest_year})")
        ax.set_xlabel(metric)
        ax.set_ylabel("Field of Study" if i == 0 else "")

    plt.tight_layout()
    plt.show()


def plot_roi_by_field(data, height=5, width=8, num_years=3):
    latest_year = data["Year"].max()
    data_3y = data[data["Year"] >= latest_year - num_years + 1]

    # Compute 3-year averages
    avg_data = data_3y.groupby("Field of study").agg({
        "ROI": "mean",
    }).reset_index()

    # Sort by ROI ascending (for horizontal barplot bottom-to-top)
    avg_data = avg_data.sort_values("ROI", ascending=False)

    # Create the plot
    plt.figure(figsize=(width, height))
    barplot = sns.barplot(
        data=avg_data,
        x="ROI",
        y="Field of study"
    )

    plt.title(f"Average ROI by Field of Study ({latest_year-num_years+1}–{latest_year})", pad=20)
    plt.xlabel("Return on Investment (ROI)")
    plt.ylabel("Field of Study")
    plt.tight_layout()
    plt.show()


def plot_employment_rate_by_field(data, height=5, width=8, num_years=3):
    latest_year = data["Year"].max()
    data_3y = data[data["Year"] >= latest_year - num_years + 1]

    # Compute 3-year averages
    avg_data = data_3y.groupby("Field of study").agg({
        "Employment rate": "mean",
    }).reset_index()

    # Sort by ROI ascending (for horizontal barplot bottom-to-top)
    avg_data = avg_data.sort_values("Employment rate", ascending=False)

    # Create the plot
    plt.figure(figsize=(width, height))
    barplot = sns.barplot(
        data=avg_data,
        x="Employment rate",
        y="Field of study"
    )

    plt.title(f"Average Employment Rate by Field of Study ({latest_year-num_years+1}–{latest_year})", pad=20)
    plt.xlabel("Employment Rate (%)")
    plt.ylabel("Field of Study")
    plt.tight_layout()
    plt.show()


def plot_income_vs_tuition_bubble(data, num_years=3, height=6, width=10, bubble_size=25):
    latest_year = data["Year"].max()
    recent_years = data["Year"] >= (latest_year - num_years + 1)
    data_3y = data[recent_years]

    # Average key metrics per field
    avg_data = data_3y.groupby("Field of study").agg({
        "Degree Cost": "mean",
        "Median income": "mean",
        "Graduate Share (%)": "mean"
    }).reset_index()

    # Sort for better layering (bigger bubbles go to the back)
    avg_data = avg_data.sort_values("Graduate Share (%)", ascending=False)

    plt.figure(figsize=(width, height))
    scatter = plt.scatter(
        x=avg_data["Degree Cost"],
        y=avg_data["Median income"],
        s=avg_data["Graduate Share (%)"] * bubble_size,  # Bubble size scaling
        color="skyblue",
        edgecolors="gray",
        alpha=0.7
    )

    # Add text labels inside bubbles
    for i, row in avg_data.iterrows():
        plt.text(
            row["Degree Cost"],
            row["Median income"],
            row["Field of study"],
            ha="center", va="center",
            fontsize=7,
            color="black"
        )

    plt.title(f"Avg Degree Cost vs. Avg Median Income by Field of Study ({latest_year - num_years + 1}–{latest_year})\n(Size = Graduate Share)", pad=20)
    plt.xlabel("Degree Cost ($)")
    plt.ylabel("Median Income ($)")
    #plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_roi_over_time(data, height=10, width=5):
    # Filter only rows with non-null ROI
    df_roi = data[data["ROI"].notnull()].copy()
    
    plt.figure(figsize=(height, width))
    sns.lineplot(data=df_roi, x="Year", y="ROI", hue="Field of study", marker="o")

    plt.title("ROI Over Time by Field of Study")
    plt.xlabel("Year")
    plt.ylabel("ROI")
    plt.legend(title="Field of study", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_single_trend_metric(data, metric, short_names=None, stacked_metrics=["Graduate Share (%)"], height=5, width=8):
    df_plot = data.copy()

    # Use short field names if provided
    if short_names:
        df_plot["Field (Short)"] = df_plot["Field of study"].map(short_names)
        field_col = "Field (Short)"
    else:
        field_col = "Field of study"

    # Setup figure
    fig, ax = plt.subplots(figsize=(width, height))

    if metric in stacked_metrics:
        # Stacked area chart
        df_stack = df_plot.pivot_table(index="Year", columns=field_col, values=metric, aggfunc="mean").fillna(0)
        df_stack.plot.area(ax=ax, cmap="tab20", legend=True)
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} Over Time (Stacked)")
    else:
        sns.lineplot(data=df_plot, x="Year", y=metric, hue=field_col, ax=ax, marker="o", legend=True)
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} Over Time")
        ax.grid(True)

    ax.set_xlabel("Year")
    plt.legend(title="Field of study", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_esi_by_field(data, height=5, width=8, num_years=3, threshold=0.90):
    latest_year = data["Year"].max()
    data_recent = data[data["Year"] >= latest_year - num_years + 1]

    # Compute average ESI over the selected years
    avg_data = data_recent.groupby("Field of study").agg({
        "ESI": "mean"
    }).reset_index()

    # Sort descending (best ESI on top)
    avg_data = avg_data.sort_values("ESI", ascending=False)

    # Plot
    plt.figure(figsize=(width, height))
    sns.barplot(
        data=avg_data,
        x="ESI",
        y="Field of study"
    )

    # Add threshold line
    plt.axvline(threshold, color="red", linestyle="--", linewidth=1.5)
    plt.text(threshold-0.5, -0.8, f"Instability Threshold ({threshold:.2f})", color="red")

    # Labels and layout
    plt.title(f"Average Employment Stability Index by Field ({latest_year - num_years + 1}–{latest_year})", pad=20)
    plt.xlabel("Employment Stability Index (ESI)")
    plt.ylabel("Field of Study")
    plt.xlim(0, 1.0)
    plt.tight_layout()
    plt.show()


def plot_grad_growth_vs_employment(data, num_years=3, width=8, height=6):
    df_plot = data.copy()

    # Filter for the latest num_years
    latest_year = df_plot["Year"].max()
    df_recent = df_plot[df_plot["Year"] >= latest_year - num_years + 1]

    # Compute 3-year averages
    avg_data = df_recent.groupby("Field of study").agg({
        "Graduate Growth Rate (%)": "mean",
        "Employment rate": "mean"
    }).reset_index()

    # Drop rows with missing values
    avg_data = avg_data.dropna(subset=["Graduate Growth Rate (%)", "Employment rate"])

    # Plot
    plt.figure(figsize=(width, height))
    sns.scatterplot(
        data=avg_data,
        x="Graduate Growth Rate (%)",
        y="Employment rate",
        hue="Field of study",
        s=100,
        alpha=0.8,
        edgecolor="gray",
        legend=False
    )

    # Add field labels to each point
    for _, row in avg_data.iterrows():
        plt.text(
            row["Graduate Growth Rate (%)"] + 0.1,
            row["Employment rate"],
            row["Field of study"],
            fontsize=9
        )

    # Format the plot
    plt.title(f"Graduate Growth vs Employment Rate ({latest_year - num_years + 1}–{latest_year})")
    plt.xlabel("Graduate Growth Rate (%)")
    plt.ylabel("Employment Rate (%)")
    #plt.axhline(0, linestyle="--", color="gray", linewidth=1)
    plt.axvline(0, linestyle="--", color="gray", linewidth=1)
    plt.tight_layout()
    plt.show()
