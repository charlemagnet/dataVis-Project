import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HOST_TYPES = ["Single listing (1)", "Small host (2-5)", "Professional host (6+)"]
ROOM_TYPES = ["Entire home/apt", "Private room", "Shared room"]
ROOM_COLORS = {
    "Entire home/apt": "#3B82F6",
    "Private room": "#10B981",
    "Shared room": "#F59E0B",
}


def add_host_type(df):
    """Label each listing by how many listings its host manages."""
    df = df.copy()
    df["host_type"] = pd.cut(
        df["calculated_host_listings_count"],
        bins=[0, 1, 5, float("inf")],
        labels=HOST_TYPES,
    )
    return df


def summarize_host_types(df):
    """Return a table with listings, hosts and median price per host type."""
    df = add_host_type(df)
    summary = (
        df.groupby("host_type", observed=True)
        .agg(
            listings=("id", "count"),
            hosts=("host_id", "nunique"),
            median_price=("price", "median"),
            avg_availability=("availability_365", "mean"),
        )
        .reindex(HOST_TYPES)
        .dropna(subset=["listings"])
        .reset_index()
    )
    summary["share_of_listings"] = summary["listings"] / summary["listings"].sum() * 100
    return summary.rename(
        columns={
            "host_type": "Host type",
            "listings": "Listings",
            "hosts": "Hosts",
            "median_price": "Median price ($)",
            "avg_availability": "Avg. availability (days)",
            "share_of_listings": "Share of listings (%)",
        }
    ).round(1)


def create_host_portfolio_chart(df):
    """Heatmap of median price (borough x host type) next to the room-type mix per host type."""
    df = add_host_type(df)
    boroughs = sorted(df["neighbourhood_group"].unique())

    # --- Left panel: median price per borough and host type ---
    price_grid = (
        df.groupby(["neighbourhood_group", "host_type"], observed=True)["price"]
        .median()
        .unstack("host_type")
        .reindex(index=boroughs, columns=HOST_TYPES)
    )
    count_grid = (
        df.groupby(["neighbourhood_group", "host_type"], observed=True)["id"]
        .count()
        .unstack("host_type")
        .reindex(index=boroughs, columns=HOST_TYPES)
        .fillna(0)
        .astype(int)
    )
    cell_text = [
        [
            f"${price:,.0f}" if pd.notna(price) else "-"
            for price in row
        ]
        for row in price_grid.values
    ]

    # --- Right panel: room-type share (%) within each host type ---
    mix = (
        df.groupby(["host_type", "room_type"], observed=True)
        .size()
        .unstack("room_type")
        .reindex(index=HOST_TYPES, columns=ROOM_TYPES)
        .fillna(0)
    )
    totals = mix.sum(axis=1).replace(0, float("nan"))
    mix_pct = mix.div(totals, axis=0) * 100

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.58, 0.42],
        horizontal_spacing=0.2,
        subplot_titles=(
            "Median nightly price by borough and host type",
            "Room-type mix within each host type",
        ),
    )

    fig.add_trace(
        go.Heatmap(
            z=price_grid.values,
            x=HOST_TYPES,
            y=boroughs,
            text=cell_text,
            texttemplate="%{text}",
            customdata=count_grid.values,
            colorscale="Blues",
            colorbar=dict(title="Median price ($)", x=0.5, len=0.9, thickness=14),
            hovertemplate=(
                "Borough: %{y}<br>Host type: %{x}<br>"
                "Median price: $%{z:,.0f}<br>Listings: %{customdata:,}<extra></extra>"
            ),
            xgap=2,
            ygap=2,
        ),
        row=1,
        col=1,
    )

    for room in ROOM_TYPES:
        fig.add_trace(
            go.Bar(
                y=HOST_TYPES,
                x=mix_pct[room].values,
                name=room,
                orientation="h",
                marker=dict(color=ROOM_COLORS[room], line=dict(color="white", width=2)),
                customdata=mix[room].astype(int).values,
                hovertemplate=(
                    f"{room}<br>Host type: %{{y}}<br>"
                    "Share: %{x:.1f}%<br>Listings: %{customdata:,}<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    fig.update_layout(
        barmode="stack",
        height=560,
        title=dict(text="Host Portfolio Analysis", font=dict(size=20)),
        legend=dict(title="Room type", orientation="h", y=-0.15, x=0.62, traceorder="normal"),
        margin=dict(t=90, l=40, r=20, b=80),
    )
    fig.update_xaxes(title_text="Host type", row=1, col=1)
    fig.update_yaxes(title_text="Borough", autorange="reversed", row=1, col=1)
    fig.update_xaxes(title_text="Share of listings (%)", range=[0, 100], row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=2)
    return fig
