import plotly.express as px

def create_violin_plot(df):
    """Display the density of price distributions across boroughs and room types."""
    # Filter out extreme outliers (e.g., top 5%) to maintain visual clarity
    upper_limit = df["price"].quantile(0.95)
    plot_df = df[df["price"] <= upper_limit]

    fig = px.violin(
        plot_df,
        x="neighbourhood_group",
        y="price",
        color="room_type",
        box=True, # Include statistical box plots inside the violins
        points=False, # Disable individual points to improve rendering performance
        category_orders={"room_type": ["Entire home/apt", "Private room", "Shared room"]},
        color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
        labels={
            "neighbourhood_group": "Borough",
            "price": "Nightly Price ($)",
            "room_type": "Room Type"
        }
    )
    
    fig.update_layout(
        title=dict(text="Price Distribution by Borough and Room Type (Excluding Top 5%)", font=dict(size=20)),
        height=600,
        margin=dict(t=60, l=40, r=20, b=40)
    )
    return fig