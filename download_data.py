import kagglehub
import shutil
from pathlib import Path

# Download dataset to KaggleHub cache
path = kagglehub.dataset_download(
    "dgomonov/new-york-city-airbnb-open-data"
)

# Copy CSV to project
source = Path(path) / "AB_NYC_2019.csv"
destination = Path("data/raw/AB_NYC_2019.csv")

destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, destination)

print("Dataset saved to:", destination)