import pandas as pd

# 1. Load Dataset
df = pd.read_csv("data/raw/AB_NYC_2019.csv")

# 2. Dataset dimensions
print("Dataset Shape:")
print(df.shape)

# 3. First 5 rows
print("\nFirst 5 Rows:")
print(df.head())

# 4. Column names and data types
print("\nDataset Information:")
df.info()

# 5. Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 6. Statistical summary
print("\nStatistical Summary:")
print(df.describe())

# 7. Duplicate rows
print("\nDuplicate Rows:")
print(df.duplicated().sum())