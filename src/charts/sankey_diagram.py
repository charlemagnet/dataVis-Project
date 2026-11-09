
import pandas as pd
import plotly.graph_objects as go


def create_sankey_chart(df):

    data = df.copy()

    # 1. Create price categories
    price_labels = [
        "$1-100", "$101-200", "$201-350", "$351+"
    ]

    data["price_group"] = pd.cut(
        data["price"],
        bins=[0, 100, 200, 350, float("inf")],
        labels=price_labels
    )

    # 2. Create availability categories
    availability_labels = [
        "0 days",
        "1-90 days",
        "91-180 days",
        "181-365 days"
    ]

    data["availability_group"] = pd.cut(
        data["availability_365"],
        bins=[-1, 0, 90, 180, 365],
        labels=availability_labels
    )

    # 3. Define nodes
    room_labels = sorted(data["room_type"].unique())

    labels = (
        room_labels
        + price_labels
        + availability_labels
    )

    node_ids = {
        label: i for i, label in enumerate(labels)
    }

    # 4. Define meaningful colors
    room_colors = {
    "Entire home/apt": "#3B82F6",
    "Private room": "#10B981",
    "Shared room": "#F59E0B"
    }

    room_link_colors = {
        "Entire home/apt": "rgba(59,130,246,0.30)",
        "Private room": "rgba(16,185,129,0.30)",
        "Shared room": "rgba(245,158,11,0.45)"
    }

    neutral_node_color = "#64748B"
    neutral_link_color = "rgba(148,163,184,0.28)"

    # Only room type nodes have distinct colors
    node_colors = (
        [room_colors.get(room, neutral_node_color)
        for room in room_labels]
        + [neutral_node_color] * len(price_labels)
        + [neutral_node_color] * len(availability_labels)
    )

    # 5. Calculate connections
    sources = []
    targets = []
    values = []

    transitions = [
        ("room_type", "price_group"),
        ("price_group", "availability_group")
    ]

    for source_col, target_col in transitions:

        grouped = (
            data.groupby(
                [source_col, target_col],
                observed=True
            )
            .size()
            .reset_index(name="count")
        )

        for _, row in grouped.iterrows():

            source_label = str(row[source_col])
            target_label = str(row[target_col])

            sources.append(node_ids[source_label])
            targets.append(node_ids[target_label])
            values.append(int(row["count"]))

    # 6. Create Sankey diagram
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",

            node=dict(
                pad=30,
                thickness=30,
                label=labels,
                color=node_colors,

                line=dict(
                    color="rgba(255,255,255,0.5)",
                    width=0.8
                ),

                hovertemplate=(
                    "%{label}<br>"
                    "%{value:,} listings"
                    "<extra></extra>"
                )
            ),

            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=neutral_link_color,

                hovertemplate=(
                    "%{source.label} → %{target.label}"
                    "<br>%{value:,} listings"
                    "<extra></extra>"
                )
            )
        )
    )

    # 7. Layout configuration
    fig.update_layout(
        title=dict(
            text="Room Type → Price → Availability",
            font=dict(size=20)
        ),

        font=dict(size=14),

        height=760,

        margin=dict(
            l=30,
            r=35,
            t=70,
            b=30
        ),

        hoverlabel=dict(
            font_size=14
        )
    )

    return fig
