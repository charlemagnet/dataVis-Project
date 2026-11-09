import numpy as np
import plotly.graph_objects as go


def create_parallel_coordinates(df, selected_id=None):
    """Compare listing attributes using interactive parallel axes."""
    if selected_id is not None:
        # Draw the selected listing last so it remains visible over other lines.
        data = df.assign(_selected=df["id"] == selected_id).sort_values("_selected")
        line = dict(
            color=data["_selected"].astype(int),
            colorscale=[[0, "#475569"], [1, "#FBBF24"]],
            cmin=0,
            cmax=1,
            showscale=False,
        )
    else:
        data = df
        price_min = data["price"].min()
        price_max = data["price"].max()
        line = dict(
            color=data["price"],
            colorscale=[[0, "#BFDBFE"], [1, "#1D4ED8"]],
            cmin=price_min,
            cmax=max(price_max, price_min + 1),
            showscale=True,
            colorbar=dict(
                title=dict(text="Price ($)", font=dict(size=15)),
                tickfont=dict(size=13),
                thickness=18,
            ),
        )

    def log_dimension(column, label, ticks):
        maximum = data[column].max()
        tick_values = [tick for tick in ticks if tick <= maximum]
        return dict(
            label=label,
            values=np.log1p(data[column]),
            range=[0, max(np.log1p(maximum), 0.01)],
            tickvals=np.log1p(tick_values),
            ticktext=[f"{tick:,}" for tick in tick_values],
        )

    fig = go.Figure(
        go.Parcoords(
            labelfont=dict(size=16, color="#E2E8F0"),
            tickfont=dict(size=13, color="#CBD5E1"),
            rangefont=dict(size=13, color="#CBD5E1"),
            line=line,
            dimensions=[
                log_dimension("price", "Price ($)", [0, 10, 50, 100, 200, 500, 1000, 5000, 10000]),
                log_dimension("minimum_nights", "Minimum nights", [0, 1, 7, 30, 90, 365, 1250]),
                log_dimension("number_of_reviews", "Reviews", [0, 1, 10, 50, 100, 300, 629]),
                dict(
                    label="Availability (days)",
                    values=data["availability_365"],
                    range=[0, 365],
                    tickvals=[0, 90, 180, 270, 365],
                ),
            ],
        )
    )
    fig.update_layout(height=600, margin=dict(l=65, r=90, t=80, b=40))
    return fig
