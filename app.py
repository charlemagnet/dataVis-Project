
import streamlit as st
import pandas as pd
import plotly.express as px

from src.charts.sankey_diagram import create_sankey_chart
from src.charts.geographical_map import create_geographical_map
from src.charts.parallel_coordinates import create_parallel_coordinates
from src.ml import FEATURES, run_kmeans, run_price_regression, summarize_clusters

# Page configuration
st.set_page_config(
    page_title="NYC Airbnb Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv(
        "data/processed/airbnb_cleaned.csv"
    )


@st.cache_data(show_spinner="Grouping listings...")
def cluster_listings(data, n_clusters):
    return run_kmeans(data, n_clusters)


@st.cache_data(show_spinner="Training and evaluating the price model...")
def evaluate_price_model(data):
    return run_price_regression(data)

df = load_data()

# Remember the selected page
if "page" not in st.session_state:
    st.session_state.page = "overview"

def change_page(page_id):
    st.session_state.page = page_id    


# ----------------------
# SIDEBAR NAVIGATION
# ----------------------

with st.sidebar:

    st.title("🏠 NYC Airbnb")
    st.caption("Data Visualization Dashboard")

    st.divider()
    st.subheader("Navigation")

    pages = [
        ("overview", "Overview", ":material/dashboard:"),
        ("sankey", "Sankey Diagram", ":material/account_tree:"),
        ("map", "Geographical Map", ":material/map:"),
        ("parallel", "Parallel Coordinates", ":material/monitoring:"),
        ("clustering", "K-Means Clustering", ":material/hub:"),
        ("regression", "Price Regression", ":material/trending_up:")
    ]

    for page_id, label, icon in pages:

        selected = st.session_state.page == page_id

        st.button(
            label,
            key=f"nav_{page_id}",
            icon=icon,
            width="stretch",
            type="primary" if selected else "secondary",
            on_click=change_page,
            args=(page_id,)
        )

    st.divider()

    # Shared dashboard filters
    st.subheader("Filters")

    regions = st.multiselect(
        "Neighbourhood Group",
        options=sorted(df["neighbourhood_group"].unique()),
        default=sorted(df["neighbourhood_group"].unique())
    )

    room_types = st.multiselect(
        "Room Type",
        options=sorted(df["room_type"].unique()),
        default=sorted(df["room_type"].unique())
    )

    max_price = st.slider(
        "Maximum Nightly Price ($)",
        min_value=0,
        max_value=int(df["price"].max()),
        value=500,
        step=25
    )


# ----------------------
# APPLY FILTERS
# ----------------------

filtered_df = df[
    (df["neighbourhood_group"].isin(regions)) &
    (df["room_type"].isin(room_types)) &
    (df["price"] <= max_price)
].copy()


# ----------------------
# OVERVIEW PAGE
# ----------------------

if st.session_state.page == "overview":

    st.title("🏠 NYC Airbnb Dashboard")
    st.caption("Exploratory Data Analysis | 2019")

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Listings",
        f"{len(filtered_df):,}"
    )

    col2.metric(
        "Median Price",
        f"${filtered_df['price'].median():.2f}"
        if not filtered_df.empty else "N/A"
    )

    col3.metric(
        "Average Reviews",
        f"{filtered_df['number_of_reviews'].mean():.1f}"
        if not filtered_df.empty else "N/A"
    )

    st.subheader("Filtered Dataset")

    st.dataframe(
        filtered_df.head(20),
        width="stretch"
    )


# ----------------------
# SANKEY DIAGRAM PAGE
# ----------------------

elif st.session_state.page == "sankey":

    st.title("🔀 Sankey Diagram")

    st.write(
        "Explore the distribution of Airbnb listings "
        "across room types, price ranges and availability."
    )

    focus = st.selectbox(
        "Focus on Room Type",
        [
            "All room types",
            "Entire home/apt",
            "Private room",
            "Shared room"
        ]
    )

    sankey_df = filtered_df.copy()

    if focus != "All room types":
        sankey_df = sankey_df[
            sankey_df["room_type"] == focus
        ].copy()

    if sankey_df.empty:
        st.warning("No listings match the selected filters.")

    else:
        st.metric(
            "Listings in This Analysis",
            f"{len(sankey_df):,}"
        )

        fig = create_sankey_chart(sankey_df)

        st.plotly_chart(
            fig,
            width="stretch"
        )

        with st.expander("View Detailed Category Counts"):

            summary = sankey_df.copy()

            summary["price_group"] = pd.cut(
                summary["price"],
                bins=[0, 100, 200, 350, float("inf")],
                labels=[
                    "$1-100",
                    "$101-200",
                    "$201-350",
                    "$351+"
                ]
            )

            counts = (
                summary.groupby(
                    ["room_type", "price_group"],
                    observed=True
                )
                .size()
                .reset_index(name="Listings")
            )

            st.dataframe(counts, width="stretch")


# ----------------------
# FUTURE VISUALIZATIONS
# ----------------------

elif st.session_state.page == "map":

    st.title("🗺️ Geographical Map")
    st.write("Explore where listings are located and how nightly prices vary across NYC.")

    if filtered_df.empty:
        st.warning("No listings match the selected filters.")
    else:
        max_map_points = 10_000
        map_df = (
            filtered_df.sample(n=max_map_points, random_state=42)
            if len(filtered_df) > max_map_points else filtered_df
        )
        st.metric("Matching Listings", f"{len(filtered_df):,}")
        st.plotly_chart(create_geographical_map(map_df))
        if len(map_df) < len(filtered_df):
            st.caption(
                f"Showing a random sample of {len(map_df):,} out of "
                f"{len(filtered_df):,} matching listings for performance."
            )
        st.caption(
            "Each point represents a listing. Points may overlap; "
            "zoom in to explore individual listings."
        )


elif st.session_state.page == "parallel":

    st.title("📈 Parallel Coordinates")
    st.write(
        "Compare nightly price, minimum stay, reviews and availability across listings."
    )

    if filtered_df.empty:
        st.warning("No listings match the selected filters.")
    else:
        max_parallel_lines = 150
        parallel_df = (
            filtered_df.sample(n=max_parallel_lines, random_state=42)
            if len(filtered_df) > max_parallel_lines else filtered_df
        )
        st.metric("Matching Listings", f"{len(filtered_df):,}")
        listing_names = parallel_df.set_index("id")["name"].to_dict()
        selected_id = st.selectbox(
            "Highlight a listing",
            options=parallel_df["id"].tolist(),
            index=None,
            placeholder="Choose a listing from the displayed sample",
            format_func=lambda listing_id: f"{listing_names[listing_id]} (ID: {listing_id})",
        )
        if selected_id is not None:
            listing = parallel_df.loc[parallel_df["id"] == selected_id].iloc[0]
            st.caption(
                f"Highlighted in yellow: ${listing['price']:,} per night · "
                f"{listing['minimum_nights']:,} minimum nights · "
                f"{listing['number_of_reviews']:,} reviews · "
                f"{listing['availability_365']:,} available days"
            )
        st.plotly_chart(create_parallel_coordinates(parallel_df, selected_id))
        if len(parallel_df) < len(filtered_df):
            st.caption(
                f"Showing a random sample of {len(parallel_df):,} out of "
                f"{len(filtered_df):,} matching listings to reduce overlap."
            )
        st.caption(
            "Each line is a listing. Drag on an axis to select a range; "
            "drag axis labels to reorder them. Price, minimum nights and reviews "
            "use logarithmic spacing; axis labels show the original values."
        )


elif st.session_state.page == "clustering":
    st.title("K-Means Clustering")
    st.write(
        "Group similar listings using nightly price, minimum nights, "
        "number of reviews and yearly availability."
    )

    distinct_listings = len(filtered_df[FEATURES].drop_duplicates())
    if distinct_listings < 2:
        st.warning("Select filters that include at least two distinct listings.")
    else:
        max_clusters = min(6, distinct_listings)
        if max_clusters == 2:
            n_clusters = 2
            st.caption("Number of clusters: 2")
        else:
            n_clusters = st.slider("Number of clusters", 2, max_clusters, 3)
        clustered_df = cluster_listings(filtered_df, n_clusters)
        st.metric("Listings in the analysis", f"{len(clustered_df):,}")

        st.subheader("Cluster profiles")
        st.caption("Medians are shown in the original units and use all matching listings.")
        st.dataframe(summarize_clusters(clustered_df), width="stretch")

        plot_df = (
            clustered_df.sample(n=3_000, random_state=42)
            if len(clustered_df) > 3_000 else clustered_df.copy()
        )
        plot_df["Cluster"] = "Cluster " + plot_df["cluster"].astype(str)
        fig = px.scatter(
            plot_df,
            x="price",
            y="availability_365",
            color="Cluster",
            category_orders={"Cluster": [f"Cluster {i}" for i in range(1, n_clusters + 1)]},
            color_discrete_sequence=px.colors.qualitative.Safe,
            hover_data={"minimum_nights": True, "number_of_reviews": True},
            labels={
                "price": "Nightly price ($)",
                "availability_365": "Availability (days)",
                "minimum_nights": "Minimum nights",
                "number_of_reviews": "Reviews",
            },
            opacity=0.65,
        )
        fig.update_traces(marker=dict(size=7))
        fig.update_layout(height=550, legend_title_text="Cluster")
        st.subheader("Price and availability by cluster")
        st.plotly_chart(fig)
        if len(plot_df) < len(clustered_df):
            st.caption(
                f"Showing {len(plot_df):,} randomly sampled listings in the chart; "
                "the model and profiles use all matching listings."
            )
        st.caption(
            "Clusters use all four features, not just the two chart axes. "
            "Price, minimum nights and reviews are log-transformed, and all "
            "features are standardized before clustering. Cluster numbers are "
            "arbitrary and can change when filters or the cluster count change."
        )


elif st.session_state.page == "regression":
    st.title("Price Regression")
    st.write(
        "Estimate nightly price from borough, room type and minimum stay, "
        "then compare predictions with prices in a held-out test set."
    )
    if len(filtered_df) < 20:
        st.warning("Select filters that include at least 20 listings to train and test the model.")
    else:
        result = evaluate_price_model(filtered_df)
        col1, col2, col3 = st.columns(3)
        col1.metric("Training listings", f"{result['train_count']:,}")
        col2.metric("Test listings", f"{result['test_count']:,}")
        col3.metric("Model MAE", f"${result['model_mae']:,.2f}")
        st.caption(
            f"Median-price baseline MAE: ${result['baseline_mae']:,.2f}. "
            "MAE is the average absolute error on the test set; lower is better."
        )

        test_results = result["test_results"]
        plot_df = (
            test_results.sample(n=2_000, random_state=42)
            if len(test_results) > 2_000 else test_results
        )
        fig = px.scatter(
            plot_df,
            x="actual_price",
            y="predicted_price",
            hover_data=["neighbourhood_group", "room_type", "minimum_nights"],
            labels={
                "actual_price": "Actual nightly price ($)",
                "predicted_price": "Predicted nightly price ($)",
                "neighbourhood_group": "Borough",
                "room_type": "Room type",
                "minimum_nights": "Minimum nights",
            },
            opacity=0.55,
            color_discrete_sequence=["#60A5FA"],
        )
        limit = max(plot_df["actual_price"].max(), plot_df["predicted_price"].max())
        fig.add_shape(
            type="line", x0=0, y0=0, x1=limit, y1=limit,
            line=dict(color="#CBD5E1", dash="dash"),
        )
        fig.update_layout(height=550)
        st.subheader("Actual vs predicted price")
        st.plotly_chart(fig)
        if len(plot_df) < len(test_results):
            st.caption(
                f"The chart shows {len(plot_df):,} randomly sampled test listings; "
                "the error metrics use the full test set."
            )
        st.caption(
            "The dashed line represents perfect predictions. The model learns from "
            "80% of matching listings and is evaluated on the remaining 20%. "
            "It is exploratory, not a valuation or evidence of causation. "
            "Changing the sidebar filters retrains the model on the selected data. "
            "The maximum price filter also limits the prices included in training and testing."
        )
