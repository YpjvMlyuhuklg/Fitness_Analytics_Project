import pandas as pd
import numpy as np

GENDER_MAP = {
    "M": "Male", "m": "Male", "MALE": "Male", "male": "Male", "Male": "Male",
    "F": "Female", "f": "Female", "FEMALE": "Female", "female": "Female", "Female": "Female",
}

NUMERIC_COLS = ["calories_burned", "duration_minutes", "daily_steps", "avg_heart_rate", "sleep_hours"]


def _to_numeric(df):
    df = df.replace(r"^\s*$", np.nan, regex=True)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def parse_fitness_date(value):
    if pd.isna(value):
        return pd.NaT
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none"):
        return pd.NaT
    parts = s.split("/")
    if len(parts) == 3:
        try:
            a, b = int(parts[0]), int(parts[1])
        except ValueError:
            return pd.to_datetime(s, errors="coerce")
        if a > 12:
            return pd.to_datetime(s, dayfirst=True, errors="coerce")
        if b > 12:
            return pd.to_datetime(s, dayfirst=False, errors="coerce")
        result = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if result is not pd.NaT and result.month <= 3:
            return result
        return pd.to_datetime(s, dayfirst=False, errors="coerce")
    return pd.to_datetime(s, errors="coerce")


_parse_date = parse_fitness_date


def clean_fitness_data(input_file, output_file):
    print("Loading data...")
    df = pd.read_csv(input_file)
    original_rows = len(df)

    df = df.drop_duplicates()

    print("Cleaning dates...")
    df["date"] = df["date"].map(parse_fitness_date)
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

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

    df = df.sort_values(["participant_id", "date"])
    df.to_csv(output_file, index=False)

    print("-" * 30)
    print("Cleaning complete")
    print(f"Original rows: {original_rows}")
    print(f"Cleaned rows:  {len(df)}")
    print(f"Saved to:      {output_file}")
    print("-" * 30)


if __name__ == "__main__":
    import sys
    raw = sys.argv[1] if len(sys.argv) > 1 else "Group4_FitnessAnalytics_raw.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "Group4_FitnessAnalytics_cleaned.csv"
    clean_fitness_data(raw, out)
