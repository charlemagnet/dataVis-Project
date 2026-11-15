import plotly.express as px

NUMERIC_COLUMNS = {
    "price": "Price",
    "minimum_nights": "Minimum nights",
    "number_of_reviews": "Reviews",
    "reviews_per_month": "Reviews / month",
    "calculated_host_listings_count": "Host listings",
    "availability_365": "Availability",
}


def create_correlation_heatmap(df, method="spearman"):
    """Show the correlation between the numeric listing features."""
    corr = df[list(NUMERIC_COLUMNS)].corr(method=method).rename(
        index=NUMERIC_COLUMNS, columns=NUMERIC_COLUMNS
    )

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        labels={"color": "Correlation"},
    )
    fig.update_traces(xgap=2, ygap=2)
    fig.update_layout(
        title=dict(text=f"Correlation Between Listing Features ({method.title()})", font=dict(size=20)),
        height=560,
        margin=dict(t=60, l=40, r=20, b=40),
    )
    return fig
