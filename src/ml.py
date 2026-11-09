import numpy as np
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURES = ["price", "minimum_nights", "number_of_reviews", "availability_365"]
LOG_FEATURES = ["price", "minimum_nights", "number_of_reviews"]


def run_kmeans(df, n_clusters):
    """Fit K-Means on filtered listings and return their cluster assignments."""
    features = df[FEATURES].copy()
    features[LOG_FEATURES] = np.log1p(features[LOG_FEATURES])

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    result = df.copy()
    result["cluster"] = model.fit_predict(scaled_features) + 1
    return result


def summarize_clusters(clustered_df):
    """Describe clusters using listing counts and medians in original units."""
    return (
        clustered_df.groupby("cluster")
        .agg(
            Listings=("id", "size"),
            **{
                "Median price ($)": ("price", "median"),
                "Median minimum nights": ("minimum_nights", "median"),
                "Median reviews": ("number_of_reviews", "median"),
                "Median availability (days)": ("availability_365", "median"),
            },
        )
        .rename_axis("Cluster")
    )


def run_price_regression(df):
    """Evaluate price predictions on listings held out from training."""
    categorical = ["neighbourhood_group", "room_type"]
    numerical = ["minimum_nights"]
    features = df[categorical + numerical]
    target = df["price"]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    preprocessing = ColumnTransformer(
        [
            ("categories", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("numbers", StandardScaler(), numerical),
        ]
    )
    model = TransformedTargetRegressor(
        regressor=make_pipeline(preprocessing, LinearRegression()),
        func=np.log1p,
        inverse_func=np.expm1,
    )
    model.fit(x_train, y_train)
    # Nightly prices cannot be negative; evaluate the final displayed predictions.
    predictions = np.maximum(model.predict(x_test), 0)

    baseline = DummyRegressor(strategy="median")
    baseline.fit(x_train, y_train)
    baseline_predictions = baseline.predict(x_test)

    results = x_test.copy()
    results["actual_price"] = y_test
    results["predicted_price"] = predictions
    return {
        "test_results": results,
        "train_count": len(x_train),
        "test_count": len(x_test),
        "model_mae": mean_absolute_error(y_test, predictions),
        "baseline_mae": mean_absolute_error(y_test, baseline_predictions),
    }
