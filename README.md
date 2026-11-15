# 🏠 NYC Airbnb – Exploratory Data Visualization Dashboard

An interactive **Streamlit** dashboard for exploring the **New York City Airbnb Open Data (2019)** dataset.
It combines **9 interactive Plotly visualizations** and **2 machine learning models** to study how
location, room type, host type and demand relate to nightly prices across NYC.

> **CEN445 – Introduction to Data Visualization · Assignment 2026–27**

---

## 📑 Table of Contents

1. [Dataset](#-dataset)
2. [Data Preprocessing](#-data-preprocessing)
3. [Dashboard Features](#-dashboard-features)
4. [Visualizations](#-visualizations)
5. [Machine Learning](#-machine-learning)
6. [Key Insights](#-key-insights)
7. [Project Structure](#-project-structure)
8. [Setup & Running](#-setup--running)
9. [Team Members & Contributions](#-team-members--contributions)

---

## 📊 Dataset

| | |
|---|---|
| **Name** | New York City Airbnb Open Data (2019) |
| **Source** | Kaggle – [dgomonov/new-york-city-airbnb-open-data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data) |
| **File** | `data/raw/AB_NYC_2019.csv` (included in this repository) |
| **Size** | 48,895 rows × 16 columns (raw) → 48,884 rows × 17 columns (cleaned) |
| **Coverage** | 5 boroughs, 221 neighbourhoods, 37,455 hosts |

The dataset describes Airbnb listings in New York City and contains a mix of data types:

| Type | Columns |
|---|---|
| **Numerical** | `price`, `minimum_nights`, `number_of_reviews`, `reviews_per_month`, `calculated_host_listings_count`, `availability_365` |
| **Categorical** | `neighbourhood_group` (borough), `neighbourhood`, `room_type` |
| **Geographical** | `latitude`, `longitude` |
| **Date** | `last_review` |
| **Text / IDs** | `id`, `name`, `host_id`, `host_name` |
| **Engineered** | `has_review` (boolean, created during preprocessing) |

The raw file can be re-downloaded with `python download_data.py` (uses `kagglehub`).

---

## 🧹 Data Preprocessing

Preprocessing is done in [`src/preprocessing.py`](src/preprocessing.py) and the result is saved to
`data/processed/airbnb_cleaned.csv`. Initial exploration (shape, data types, missing values, summary
statistics, duplicates) is in [`explore_data.py`](explore_data.py).

| Issue | Handling |
|---|---|
| Missing `name` (16) / `host_name` (21) | Filled with `"Unknown Listing"` / `"Unknown Host"` |
| Missing `reviews_per_month` (10,052) | Filled with `0` – these listings have no reviews |
| Missing `last_review` (10,052) | Kept as missing; converted to datetime |
| Invalid prices (`price = 0`, 11 rows) | Removed |
| Price outliers | Detected with the **IQR method** (upper bound ≈ $334, 2,972 listings). They are kept in the data and controlled interactively with the *Maximum Nightly Price* slider; the violin plot additionally excludes the top 5% for readability |
| New feature | `has_review` = `number_of_reviews > 0` |

---

## 🖥️ Dashboard Features

- **Sidebar navigation** to switch between the overview, 9 visualizations and 2 ML pages.
- **Global filters** (applied to every page):
  - *Neighbourhood Group* – multiselect
  - *Room Type* – multiselect
  - *Maximum Nightly Price ($)* – slider
- **Page-level controls**: dropdowns (room-type focus, highlighted listing, demand metric), sliders
  (number of clusters, minimum listings per neighbourhood) and a radio button (correlation method).
- **Chart interactivity** (Plotly): hover tooltips, zoom, pan, legend toggling/highlighting, axis
  brushing and drag-to-reorder (parallel coordinates), drill-down (treemap), map zoom.
- **Overview page** with KPIs (total listings, median price, average reviews) and a preview of the filtered data.

---

## 📈 Visualizations

| # | Visualization | Type | Insight / Analytical perspective | Interactivity |
|---|---|---|---|---|
| 1 | **Sankey Diagram** | Advanced | Flow of listings from room type → price range → yearly availability | Room-type dropdown, hover on flows, detailed counts table |
| 2 | **Geographical Map** | Advanced | Where listings are located and how prices vary across the city | Zoom, pan, hover tooltips, colour by price |
| 3 | **Parallel Coordinates** | Advanced | Multi-dimensional comparison of price, minimum nights, reviews and availability | Axis brushing, drag-to-reorder axes, listing highlight dropdown |
| 4 | **Treemap** | Advanced | Hierarchical share of listings (NYC → borough → neighbourhood) coloured by average price | Click to drill down, hover |
| 5 | **Violin Plot** | Advanced | Price distribution density per borough and room type | Hover statistics, legend toggling |
| 6 | **Top Neighbourhoods (Bar Chart)** | Basic | 15 neighbourhoods with the highest guest engagement (total reviews) | Hover (average price), legend toggling |
| 7 | **Host Portfolio Analysis** | Advanced (heatmap + 100% stacked bar) | How single-listing, small (2–5) and professional (6+) hosts differ in median price per borough and in their room-type mix | Hover (price + listing count), legend toggling, KPI cards, summary table |
| 8 | **Neighbourhood Price vs Demand** | Advanced (bubble chart with quadrants) | Positions each neighbourhood by median price vs a demand indicator, sized by listing count, split into four quadrants (affordable/premium × high/low demand) | Demand-metric dropdown, minimum-listings slider, hover, zoom, log price axis |
| 9 | **Correlation Heatmap** | Basic | Strength and direction of relationships between the numeric features | Spearman / Pearson radio button, hover values |

All charts include titles, axis labels and legends, and share a consistent colour scheme
(e.g. the same colours for room types across charts; a sequential scale for magnitudes and a diverging
scale for correlations).

---

## 🤖 Machine Learning

Implemented in [`src/ml.py`](src/ml.py) with scikit-learn. Both models are retrained on the
currently filtered data.

### 1. K-Means Clustering
- **Features:** `price`, `minimum_nights`, `number_of_reviews`, `availability_365`
- Price, minimum nights and reviews are `log1p`-transformed; all features are standardised.
- The user selects the number of clusters (2–6) with a slider.
- Output: cluster profile table (medians in original units) and a price vs availability scatter plot coloured by cluster.

### 2. Price Regression (Linear Regression)
- **Features:** borough, room type (one-hot encoded) and minimum nights (standardised)
- **Target:** nightly price (trained on `log1p(price)`, predictions transformed back)
- 80% / 20% train–test split; evaluated with **Mean Absolute Error (MAE)** against a median-price baseline.
- With the default filters (price ≤ $500) the model reaches an MAE of **≈ $45** vs **≈ $64** for the baseline.
- Output: actual vs predicted scatter plot with a perfect-prediction reference line.

---

## 💡 Key Insights

- **Manhattan (44%) and Brooklyn (41%)** account for ~85% of all listings; Manhattan is clearly the most
  expensive borough (median **$150/night** vs $90 in Brooklyn and $65 in the Bronx).
- **Room type is the strongest price driver:** entire homes (median $160) cost more than twice as much
  as private rooms ($70); shared rooms are rare (2.4%) and cheapest ($45).
- **Professional hosts (6+ listings)** are priced above single-listing hosts in Manhattan, but *below*
  them in the outer boroughs – suggesting different business models (premium Manhattan apartments vs
  budget private rooms).
- **About 36% of listings have 0 available days** in the next year, i.e. they are either fully booked or inactive.
- **Number of reviews and reviews per month are strongly correlated**, while price shows almost no
  correlation with demand indicators – expensive listings are not necessarily less popular.
- Several **affordable Queens neighbourhoods** have the highest review activity per listing, while many
  Manhattan neighbourhoods combine premium prices with average demand.
- Simple features (borough, room type, minimum nights) already reduce price prediction error by ~30%
  compared to always predicting the median price.

---

## 📁 Project Structure

```
dataVis-Project/
├── app.py                         # Main Streamlit application
├── requirements.txt               # Python dependencies
├── download_data.py               # Downloads the raw dataset from Kaggle
├── explore_data.py                # Initial data exploration
├── data/
│   ├── raw/AB_NYC_2019.csv        # Original dataset
│   └── processed/airbnb_cleaned.csv
└── src/
    ├── preprocessing.py           # Data cleaning & outlier detection
    ├── ml.py                      # K-Means clustering & price regression
    └── charts/
        ├── sankey_diagram.py
        ├── geographical_map.py
        ├── parallel_coordinates.py
        ├── treemap_chart.py
        ├── violin_chart.py
        ├── bar_chart.py
        ├── host_portfolio.py
        ├── price_demand_bubble.py
        └── correlation_heatmap.py
```

---

## ⚙️ Setup & Running

> **Python version:** use **Python 3.11 or 3.12**. The pinned versions in `requirements.txt`
> (e.g. `numpy==2.0.2`) do not provide wheels for Python 3.13+ and will fail to install.

```bash
# 1. Clone the repository
git clone https://github.com/charlemagnet/dataVis-Project.git
cd dataVis-Project

# 2. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**.

Optional – regenerate the data:

```bash
python download_data.py      # download the raw CSV from Kaggle
python src/preprocessing.py  # create data/processed/airbnb_cleaned.csv
```

---

## 👥 Team Members & Contributions

> ⚠️ **TODO:** Fill in full names / student IDs and verify the assignments below
> (pre-filled from the Git history).

| Member | Student ID | Contributions |
|---|---|---|
| **Barış Kayırtar** (GitHub: `charlemagnet`)  Dataset selection & download script, data exploration, data preprocessing (missing values, outlier detection), dashboard layout & sidebar navigation, global filters, **Sankey Diagram**, **Geographical Map**, **Parallel Coordinates**, K-Means clustering, price regression |
| **Samet Faruk Ziyan** (GitHub: `Magosaant`) **Treemap**, **Violin Plot**, **Top Neighbourhoods Bar Chart** |
| **Mehmet Uysal** (GitHub: `muysal0`) **Host Portfolio Analysis**, **Neighbourhood Price vs Demand bubble chart**, **Correlation Heatmap** |
---

## 📜 License & Data

The dataset is published on Kaggle under its original license by Dgomonov and is based on
[Inside Airbnb](http://insideairbnb.com/) data. This project was developed for educational purposes.
