from pathlib import Path
import pandas as pd

# 1. Load original dataset
df = pd.read_csv("data/raw/AB_NYC_2019.csv")

print("Missing values BEFORE cleaning:")
print(df.isnull().sum())

# 2. Handle missing names
df["name"] = df["name"].fillna("Unknown Listing")
df["host_name"] = df["host_name"].fillna("Unknown Host")

# 3. Handle missing monthly reviews
df["reviews_per_month"] = df["reviews_per_month"].fillna(0)

# 4. Convert review dates to datetime
df["last_review"] = pd.to_datetime(
    df["last_review"],
    errors="coerce"
)

# 5. Create a new feature
df["has_review"] = df["number_of_reviews"] > 0

# 6. Remove invalid prices
df = df[df["price"] > 0].copy()

# 7. Detect price outliers using IQR
Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)

IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

outliers = df[df["price"] > upper_bound]

print("\nDetected price outliers:", len(outliers))

# 8. Show results
print("\nMissing values AFTER cleaning:")
print(df.isnull().sum())

print("\nFinal dataset shape:", df.shape)

# 9. Save cleaned dataset
output_path = Path("data/processed/airbnb_cleaned.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print("\nCleaned dataset saved successfully!")