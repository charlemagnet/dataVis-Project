import plotly.express as px
import pandas as pd

def create_treemap(df):
    """Show the hierarchical distribution of listings and average prices by neighborhood."""
    # Group data to calculate listing counts and average prices
    summary = df.groupby(["neighbourhood_group", "neighbourhood"]).agg(
        listing_count=("id", "count"),
        avg_price=("price", "mean")
    ).reset_index()
    
    # Filter out neighborhoods with very few listings to prevent visual clutter
    summary = summary[summary["listing_count"] > 5]

    fig = px.treemap(
        summary,
        path=[px.Constant("New York City"), "neighbourhood_group", "neighbourhood"],
        values="listing_count",
        color="avg_price",
        color_continuous_scale="Viridis",
        labels={"avg_price": "Average Price ($)"},
        hover_data={"listing_count": True, "avg_price": ":.2f"}
    )
    
    fig.update_layout(
        title=dict(text="Listing Distribution and Average Prices by Neighborhood", font=dict(size=20)),
        margin=dict(t=50, l=10, r=10, b=10),
        height=650
    )
    return fig