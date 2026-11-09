import plotly.express as px

def create_top_neighborhoods_bar(df):
    """Show the top 15 most reviewed neighborhoods and their average prices."""
    summary = df.groupby(["neighbourhood_group", "neighbourhood"]).agg(
        total_reviews=("number_of_reviews", "sum"),
        avg_price=("price", "mean")
    ).reset_index()
    
    # Select and sort the top 15 neighborhoods by total reviews
    top_15 = summary.nlargest(15, "total_reviews").sort_values("total_reviews", ascending=True)

    fig = px.bar(
        top_15,
        x="total_reviews",
        y="neighbourhood",
        color="neighbourhood_group",
        orientation="h",
        text_auto=".2s",
        labels={
            "total_reviews": "Total Reviews",
            "neighbourhood": "Neighborhood",
            "neighbourhood_group": "Borough",
            "avg_price": "Average Price ($)"
        },
        hover_data={"avg_price": ":.2f"}
    )
    
    fig.update_layout(
        title=dict(text="Top 15 Neighborhoods by Guest Engagement (Reviews)", font=dict(size=20)),
        height=600,
        margin=dict(t=60, l=20, r=40, b=40)
    )
    return fig