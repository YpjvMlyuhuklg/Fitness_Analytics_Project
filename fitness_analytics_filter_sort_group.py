import pandas as pd

INPUT_FILE = "Group4_FitnessAnalytics_cleaned.csv"
OUTPUT_FILE = "Group4_FitnessAnalytics_processed.csv"

pd.set_option("display.width", 120)

# Load data
df = pd.read_csv(INPUT_FILE)

print("DATA LOADED")
print(f"Total rows: {len(df)}")
print(f"Total participants: {df['participant_id'].nunique()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

# 1. FILTERING
print("\n1. FILTERING")

# Filter A: High-intensity sessions (average heart rate >= 130 bpm)
high_intensity = df[df["avg_heart_rate"] >= 130]
print(f"\nHigh-intensity sessions (avg HR >= 130): {len(high_intensity)} rows")
print(high_intensity[["participant_id", "date", "activity_type", "avg_heart_rate"]].head(10).to_string(index=False))

# Filter B: Long-duration sessions (60+ minutes)
long_sessions = df[df["duration_minutes"] >= 60]
print(f"\nLong sessions (duration >= 60 min): {len(long_sessions)} rows")
print(long_sessions[["participant_id", "date", "activity_type", "duration_minutes"]].head(10).to_string(index=False))

# Filter C: Low sleep combined with high calorie burn
low_sleep_high_burn = df[(df["sleep_hours"] < 6) & (df["calories_burned"] > df["calories_burned"].median())]
print(f"\nLow sleep (<6h) + above-median calories burned: {len(low_sleep_high_burn)} rows")
print(low_sleep_high_burn[["participant_id", "date", "sleep_hours", "calories_burned"]].head(10).to_string(index=False))

# 2. SORTING
print("\n2. SORTING")

# Sort A: Top 10 sessions by calories burned (descending)
top_calories = df.sort_values("calories_burned", ascending=False).head(10)
print("\nTop 10 sessions by calories burned:")
print(top_calories[["participant_id", "date", "activity_type", "calories_burned"]].to_string(index=False))

# Sort B: Top 10 sessions by daily steps (descending)
top_steps = df.sort_values("daily_steps", ascending=False).head(10)
print("\nTop 10 sessions by daily steps:")
print(top_steps[["participant_id", "date", "activity_type", "daily_steps"]].to_string(index=False))

# Sort C: 10 sessions with the lowest sleep hours (ascending)
lowest_sleep = df.sort_values("sleep_hours", ascending=True).head(10)
print("\n10 sessions with lowest sleep hours:")
print(lowest_sleep[["participant_id", "date", "sleep_hours", "activity_type"]].to_string(index=False))

# Sort D: Whole dataset sorted by participant then date (used for export later)
df_sorted = df.sort_values(["participant_id", "date"])

# 3. GROUPING
print("\n3. GROUPING")

# Group A: By participant - totals and averages
by_participant = df.groupby("participant_id").agg(
    total_sessions=("activity_type", "count"),
    total_calories=("calories_burned", "sum"),
    avg_calories=("calories_burned", "mean"),
    total_steps=("daily_steps", "sum"),
    avg_steps=("daily_steps", "mean"),
    avg_sleep_hours=("sleep_hours", "mean"),
).round(2).reset_index().sort_values("total_calories", ascending=False)

print("\nGrouped by participant (sorted by total calories, top 10):")
print(by_participant.head(10).to_string(index=False))

# Group B: By activity type - totals and averages
by_activity = df.groupby("activity_type").agg(
    sessions=("activity_type", "count"),
    total_calories=("calories_burned", "sum"),
    avg_calories=("calories_burned", "mean"),
    avg_duration=("duration_minutes", "mean"),
    avg_steps=("daily_steps", "mean"),
).round(2).reset_index()

by_activity["pct_of_all_sessions"] = (by_activity["sessions"] / len(df) * 100).round(2)
by_activity = by_activity.sort_values("total_calories", ascending=False)

print("\nGrouped by activity type:")
print(by_activity.to_string(index=False))

# Group C: By gender - totals and averages
by_gender = df.groupby("gender").agg(
    sessions=("activity_type", "count"),
    total_calories=("calories_burned", "sum"),
    avg_calories=("calories_burned", "mean"),
    avg_steps=("daily_steps", "mean"),
    avg_sleep_hours=("sleep_hours", "mean"),
).round(2).reset_index()

print("\nGrouped by gender:")
print(by_gender.to_string(index=False))

# Group D: By gender + activity type combined
by_gender_activity = df.groupby(["gender", "activity_type"]).agg(
    sessions=("activity_type", "count"),
    avg_calories=("calories_burned", "mean"),
).round(2).reset_index()

print("\nGrouped by gender and activity type:")
print(by_gender_activity.to_string(index=False))

# Export processed file
print("\nEXPORTING PROCESSED FILE")

df_sorted.to_csv(OUTPUT_FILE, index=False)
print(f"Processed dataset saved to: {OUTPUT_FILE}")
print(f"Rows exported: {len(df_sorted)}")
