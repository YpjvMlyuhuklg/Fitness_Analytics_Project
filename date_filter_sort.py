"""Optional CLI: filter and sort dates from the cleaned CSV.

The GUI creates Group4_FitnessAnalytics_cleaned.csv when you click
Run Clean & Deduplication. Run this script only if you want a separate
date-sorted export from the raw file without using the GUI.
"""

import pandas as pd

from cleaning import parse_fitness_date

INPUT_FILE = "Group4_FitnessAnalytics_raw.csv"
OUTPUT_FILE = "Group4_FitnessAnalytics_dates_sorted.csv"

STUDY_YEAR = 2025
STUDY_MONTHS = (1, 2, 3)


def load_with_parsed_dates(path):
    df = pd.read_csv(path)
    df["date_parsed"] = df["date"].map(parse_fitness_date)
    df = df.dropna(subset=["date_parsed"]).copy()
    df["date_parsed"] = df["date_parsed"].apply(
        lambda ts: ts.replace(year=STUDY_YEAR)
    )
    df = df[df["date_parsed"].dt.month.isin(STUDY_MONTHS)]
    df["date"] = df["date_parsed"].dt.strftime("%Y-%m-%d")
    return df.drop(columns=["date_parsed"])


def main():
    df = load_with_parsed_dates(INPUT_FILE)

    print("DATE FILTER & SORT")
    print(f"Rows in Jan–Mar {STUDY_YEAR}: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    jan_only = df[df["date"].str.startswith(f"{STUDY_YEAR}-01")]
    print(f"\nJanuary {STUDY_YEAR} sessions: {len(jan_only)}")

    high_intensity = df[df["avg_heart_rate"] >= 130]
    print(f"High-intensity (HR >= 130): {len(high_intensity)} rows")

    sorted_df = df.sort_values(["participant_id", "date"])
    print("\nFirst 10 rows (participant, then date):")
    print(
        sorted_df[["participant_id", "date", "activity_type"]]
        .head(10)
        .to_string(index=False)
    )

    sorted_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved sorted file: {OUTPUT_FILE} ({len(sorted_df)} rows)")


if __name__ == "__main__":
    main()
