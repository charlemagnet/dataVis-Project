import pandas as pd
import plotly.express as px


def create_geographical_map(df):
    """Show listing locations colored by nightly price range."""
    data = df.copy()
    price_ranges = ["$1-100", "$101-200", "$201-350", "$351+"]
    data["price_range"] = pd.cut(
        data["price"],
        bins=[0, 100, 200, 350, float("inf")],
        labels=price_ranges,
    )

    fig = px.scatter_map(
        data,
        lat="latitude",
        lon="longitude",
        color="price_range",
        category_orders={"price_range": price_ranges},
        color_discrete_map={
            "$1-100": "#BFDBFE",
            "$101-200": "#60A5FA",
            "$201-350": "#3B82F6",
            "$351+": "#1D4ED8",
        },
        hover_data={
            "latitude": False,
            "longitude": False,
            "price_range": False,
            "price": ":$,.0f",
            "room_type": True,
            "neighbourhood_group": True,
            "neighbourhood": True,
            "number_of_reviews": True,
        },
        labels={
            "price_range": "Nightly price",
            "price": "Nightly price",
            "room_type": "Room type",
            "neighbourhood_group": "Borough",
            "neighbourhood": "Neighbourhood",
            "number_of_reviews": "Reviews",
        },
        map_style="carto-darkmatter",
        center={"lat": 40.72, "lon": -73.95},
        zoom=9,
        opacity=0.7,
    )
    fig.update_traces(marker={"size": 8})
    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            title=dict(text="Nightly price", font=dict(size=16)),
            font=dict(size=15),
            x=1.02,
            y=0.90,
            xanchor="left",
            yanchor="top",
            itemsizing="trace",
        ),
    )
    return fig
