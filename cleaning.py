import pandas as pd
import numpy as np

GENDER_MAP = {
    "M": "Male", "m": "Male", "MALE": "Male", "male": "Male", "Male": "Male",
    "F": "Female", "f": "Female", "FEMALE": "Female", "female": "Female", "Female": "Female",
}

NUMERIC_COLS = ["calories_burned", "duration_minutes", "daily_steps", "avg_heart_rate", "sleep_hours"]


def _to_numeric(df):
    """Coerce numeric columns before any median/outlier logic."""
    df = df.replace(r"^\s*$", np.nan, regex=True)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_fitness_data(input_file, output_file):
    print("Loading data...")
    df = pd.read_csv(input_file)
    original_rows = len(df)

    df = df.drop_duplicates()

    print("Cleaning dates...")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    df = df.dropna(subset=["date"])

    print("Standardizing categorical fields...")
    df["gender"] = df["gender"].astype(str).str.strip().map(GENDER_MAP)
    df["activity_type"] = df["activity_type"].astype(str).str.strip().str.title().replace("Runing", "Running")
    df["activity_type"] = df["activity_type"].replace({"Hiit": "HIIT"})

    print("Coercing numeric columns...")
    df = _to_numeric(df)

    print("Handling outliers...")
    dur_median = df.loc[df["duration_minutes"] != 450, "duration_minutes"].median()
    df.loc[df["duration_minutes"] == 450, "duration_minutes"] = dur_median

    df.loc[df["daily_steps"] < 0, "daily_steps"] = np.nan
    df.loc[df["avg_heart_rate"] > 250, "avg_heart_rate"] = np.nan

    print("Filling missing values...")
    for col in NUMERIC_COLS:
        df[col] = df[col].fillna(df[col].median())

    df.to_csv(output_file, index=False)

    print("-" * 30)
    print("Cleaning complete")
    print(f"Original rows: {original_rows}")
    print(f"Cleaned rows:  {len(df)}")
    print(f"Saved to:      {output_file}")
    print("-" * 30)


if __name__ == "__main__":
    clean_fitness_data("Group4_FitnessAnalytics_raw.csv", "Group4_FitnessAnalytics_cleaned.csv")
