import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import plotly.io as pio
pio.renderers.default = "iframe"


def plot_snapshot_metrics_by_field(data, metrics=["Graduates", "Tuition", "Median income"], height=500, width=800, staticPlot=True):
    latest_year = data["Year"].max()
    latest_data = data[data["Year"] == latest_year].copy()

    fields_order = latest_data.sort_values(by="Graduates", ascending=True)["Field of study"]

    # Prepare one trace per metric
    traces = []
    for metric in metrics:
        trace = go.Bar(
            y=latest_data.set_index("Field of study").loc[fields_order][metric],
            x=fields_order,
            orientation="v",
            name=metric,
            visible=(metric == metrics[0]),
            hovertemplate=f"{metric}: %{{y:,.0f}}<extra></extra>",
        )
        traces.append(trace)

    # Create buttons for the dropdown
    buttons = []
    for i, metric in enumerate(metrics):
        visibility = [j == i for j in range(len(metrics))]
        buttons.append(dict(
            label=metric,
            method="update",
            args=[{"visible": visibility}, {"title": f"{metric} by Field of Study ({latest_year})"}]
        ))

    # Build the figure
    fig = go.Figure(data=traces)
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            showactive=True,
            x=1.05,
            xanchor="left",
            y=1,
            buttons=buttons,
        )],
        title=f"{metrics[0]} by Field of Study ({latest_year})",
        xaxis_title=metrics[0],
        yaxis_title="Field of Study",
        height=height,
        width=width,
        margin=dict(t=60)
    )

    fig.show(config={'staticPlot': staticPlot})


def plot_roi_by_field(data, height=500, width=800, staticPlot=True):
    latest_year = data["Year"].max()
    data_3y = data[data["Year"] >= latest_year - 2]

    # Compute 3-year averages
    avg_data = data_3y.groupby("Field of study").agg({
        "ROI": "mean",
        "ESI": "mean"
    }).reset_index()

    # Sort by ROI descending
    avg_data = avg_data.sort_values("ROI", ascending=True)

    # Plot with Plotly Express
    fig = px.bar(
        avg_data,
        x="ROI",
        y="Field of study",
        orientation="h",
        hover_data={
            "ROI": ":.2f",
            "ESI": ":.3f"
        },
        title=f"Average ROI by Field of Study ({latest_year-2}–{latest_year})"
    )

    fig.update_layout(
        xaxis_title="Return on Investment (ROI)",
        yaxis_title="Field of Study",
        height=height,
        width=width,
        margin=dict(t=60)
    )

    fig.show(config={'staticPlot': staticPlot})


def plot_income_vs_tuition_bubble(data, height=600, width=800, staticPlot=True):
    latest_year = data["Year"].max()
    recent_years = data["Year"] >= (latest_year - 2)
    data_3y = data[recent_years]

    # Average key metrics per field
    avg_data = data_3y.groupby("Field of study").agg({
        "Tuition (4Y)": "mean",
        "Median income": "mean",
        "Graduate Share (%)": "mean"
    }).reset_index()

    # Sort for better layer stacking
    avg_data = avg_data.sort_values("Graduate Share (%)", ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=avg_data["Tuition (4Y)"],
        y=avg_data["Median income"],
        mode="markers+text",
        text=avg_data["Field of study"],
        textposition="middle center",
        customdata=avg_data[["Graduate Share (%)"]],  # Pass true values
        marker=dict(
            size=avg_data["Graduate Share (%)"] * 2.5,
            color="skyblue",
            line=dict(width=1, color="gray"),
            opacity=0.7
        ),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Tuition (4Y): $%{x:,.0f}<br>" +
            "Median Income: $%{y:,.0f}<br>" +
            "Graduate Share: %{customdata[0]:.1f}%<extra></extra>"
        )
    ))

    fig.update_layout(
        title=f"Degree Cost vs. Median Income by Field of Study ({latest_year-2}–{latest_year})",
        xaxis_title="Tuition (4Y $)",
        yaxis_title="Median Income ($)",
        height=height,
        width=width,
        margin=dict(t=60)
    )

    fig.show(config={'staticPlot': staticPlot})


def plot_saturation_circle_packing(data, height=600, width=600, staticPlot=True):
    latest_year = data["Year"].max()
    data_3y = data[data["Year"] >= latest_year - 2]

    # Average values across 3 years
    avg_data = data_3y.groupby("Field of study").agg({
        "Graduates (5Y)": "mean",
        "Employed (25%)": "mean"
    }).reset_index()

    # Compute Employed estimate and Saturation Index
    avg_data["Employed"] = avg_data["Employed (25%)"] * 4
    avg_data["Saturation per 1K Employed"] = (
        avg_data["Graduates (5Y)"] / avg_data["Employed"]
    ) * 1000

    # Determine threshold (median-based)
    threshold = avg_data["Saturation per 1K Employed"].median()
    avg_data["Color"] = np.where(
        avg_data["Saturation per 1K Employed"] > threshold,
        "tomato", "mediumseagreen"
    )

    # Arrange bubbles in circular layout
    angles = np.linspace(0, 2 * np.pi, len(avg_data), endpoint=False)
    avg_data["x"] = np.cos(angles)
    avg_data["y"] = np.sin(angles)
    avg_data["size"] = np.sqrt(avg_data["Saturation per 1K Employed"]) * 25

    # Build figure
    fig = go.Figure()
    
    cmin = avg_data["Saturation per 1K Employed"].min()
    cmax = avg_data["Saturation per 1K Employed"].max()

    for _, row in avg_data.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["x"]],
            y=[row["y"]],
            mode="markers+text",
            marker=dict(
                size=row["size"],
                color=row["Saturation per 1K Employed"],
                colorscale="Reds",  # or "RdYlBu", "Picnic"
                cmin=cmin,     # optional: set min for consistent scale
                cmax=cmax,     # optional: set max for consistent scale
                showscale=False,
                colorbar=dict(title="Saturation per 1K Employed"),
                line=dict(width=1, color="black"),
                opacity=0.8
            ),
            text=[row["Field of study"]],
            textposition="middle center",
            hovertemplate=(
                f"<b>{row['Field of study']}</b><br>"
                f"Saturation: {row['Saturation per 1K Employed']:.1f} grads per 1K employed<extra></extra>"
            ),
            showlegend=False
        ))

    fig.update_layout(
        title="Saturation per 1K Employed (3-Year Average)",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=height,
        width=width,
        margin=dict(t=60)
    )

    fig.show(config={'staticPlot': staticPlot})    

    


def plot_employment_vs_saturation():
    pass


def plot_trend_metrics_by_field():
    pass


def plot_roi_over_time():
    pass


def plot_correlation_heatmap():
    pass


def generate_summary_flag_table():
    pass

