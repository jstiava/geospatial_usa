import os
from pathlib import Path
from urllib.parse import urlparse
import requests
import pandas as pd
from urllib.parse import urlparse
from io import BytesIO

output_dir = "candidate_totals_by_county"
os.makedirs(output_dir, exist_ok=True)

script_dir = Path(__file__).parent
df = pd.read_csv(script_dir / "IL_election_options.csv")

for _, row in df.iterrows():
    url = row["CandidateTotalsByCountyLink"]

    if pd.isna(url) or not url:
        continue

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        excel = pd.read_excel(BytesIO(response.content))

        filename = row['election'] + ".csv"
        excel.to_csv(os.path.join(output_dir, filename), index=False)

        print(f"Saved {filename}")

    except Exception as e:
        print(f"Failed: {url}")
        print(e)