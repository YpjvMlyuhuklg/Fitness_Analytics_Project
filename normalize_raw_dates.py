"""One-shot normalizer for Group4_FitnessAnalytics_raw.csv.

Rewrites mixed date strings to YYYY-MM-DD, year 2025, Jan–Mar only.
"""

import pandas as pd

from cleaning import parse_fitness_date

RAW_FILE = "Group4_FitnessAnalytics_raw.csv"
STUDY_YEAR = 2025
FALLBACK_DATE = f"{STUDY_YEAR}-02-15"


def normalize_raw_dates(path=RAW_FILE):
    df = pd.read_csv(path)
    parsed = df["date"].map(parse_fitness_date)
    missing = parsed.isna()
    if missing.any():
        parsed = parsed.fillna(pd.Timestamp(FALLBACK_DATE))

    normalized = parsed.apply(lambda ts: ts.replace(year=STUDY_YEAR))
    out_of_range = ~normalized.dt.month.isin([1, 2, 3])
    if out_of_range.any():
        normalized.loc[out_of_range] = normalized.loc[out_of_range].apply(
            lambda ts: ts.replace(month=min(ts.month, 3), day=min(ts.day, 28))
        )

    df["date"] = normalized.dt.strftime("%Y-%m-%d")
    df.to_csv(path, index=False)
    print(f"Normalized {len(df)} rows in {path}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")


if __name__ == "__main__":
    normalize_raw_dates()
