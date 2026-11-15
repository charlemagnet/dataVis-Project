import math

import plotly.express as px

BOROUGH_COLORS = {
    "Bronx": "#8B5CF6",
    "Brooklyn": "#CC6677",
    "Manhattan": "#3B82F6",
    "Queens": "#10B981",
    "Staten Island": "#F59E0B",
}

DEMAND_METRICS = {
    "Reviews per month": "reviews_per_month",
    "Availability (days per year)": "availability_365",
    "Total reviews per listing": "number_of_reviews",
}


def summarize_neighborhoods(df, demand_column, min_listings=10):
    """One row per neighbourhood with median price, a demand metric and listing count."""
    summary = (
        df.groupby(["neighbourhood_group", "neighbourhood"])
        .agg(
            median_price=("price", "median"),
            demand=(demand_column, "mean"),
            listings=("id", "count"),
        )
        .reset_index()
    )
    return summary[summary["listings"] >= min_listings].copy()


def create_price_demand_bubble(df, demand_label="Reviews per month", min_listings=10, label_top=6):
    """Bubble chart: neighbourhood median price vs a demand metric, sized by listing count,
    split into four quadrants at the median of each axis."""
    demand_column = DEMAND_METRICS[demand_label]
    summary = summarize_neighborhoods(df, demand_column, min_listings)
    if summary.empty:
        return None, summary

    x_mid = summary["median_price"].median()
    y_mid = summary["demand"].median()

    fig = px.scatter(
        summary,
        x="median_price",
        y="demand",
        size="listings",
        color="neighbourhood_group",
        color_discrete_map=BOROUGH_COLORS,
        category_orders={"neighbourhood_group": list(BOROUGH_COLORS)},
        hover_name="neighbourhood",
        hover_data={
            "neighbourhood_group": True,
            "median_price": ":$,.0f",
            "demand": ":.2f",
            "listings": ":,",
        },
        labels={
            "median_price": "Median nightly price ($)",
            "demand": f"Average {demand_label.lower()}",
            "listings": "Listings",
            "neighbourhood_group": "Borough",
        },
        log_x=True,
        size_max=45,
        opacity=0.75,
    )
    fig.update_traces(marker=dict(line=dict(color="white", width=1.5)))

    # Quadrant dividers at the median of each axis
    fig.add_vline(x=x_mid, line=dict(color="#94A3B8", dash="dash", width=1))
    fig.add_hline(y=y_mid, line=dict(color="#94A3B8", dash="dash", width=1))

    quadrant_labels = [
        (0.01, 0.99, "left", "top", "Affordable & high demand"),
        (0.99, 0.99, "right", "top", "Premium & high demand"),
        (0.01, 0.01, "left", "bottom", "Affordable & low demand"),
        (0.99, 0.01, "right", "bottom", "Premium & low demand"),
    ]
    for x, y, xanchor, yanchor, text in quadrant_labels:
        fig.add_annotation(
            x=x, y=y, xref="paper", yref="paper",
            xanchor=xanchor, yanchor=yanchor,
            text=text, showarrow=False,
            font=dict(size=12, color="#64748B"),
        )

    # Direct labels for the largest neighbourhoods only
    for i, (_, row) in enumerate(summary.nlargest(label_top, "listings").iterrows()):
        fig.add_annotation(
            # log_x axis: annotation positions are given in log10 space
            x=math.log10(row["median_price"]), y=row["demand"],
            xref="x", yref="y",
            text=row["neighbourhood"],
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#94A3B8",
            ax=0, ay=-30 if i % 2 == 0 else 30,
            font=dict(size=11),
        )

    price_ticks = [25, 50, 75, 100, 150, 200, 300, 500, 1000, 2000]
    fig.update_xaxes(tickvals=price_ticks, ticktext=[f"${t:,}" for t in price_ticks])

    fig.update_layout(
        title=dict(text=f"Neighbourhood Price vs {demand_label}", font=dict(size=20)),
        height=650,
        legend_title_text="Borough",
        margin=dict(t=60, l=40, r=20, b=40),
    )
    return fig, summary
