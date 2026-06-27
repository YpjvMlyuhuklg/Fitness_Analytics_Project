import pandas as pd
from fitness_analytics_stats import STEP_BENCHMARK

INPUT_FILE = "Group4_FitnessAnalytics_cleaned.csv"
OUTPUT_FILE = "Group4_FitnessAnalytics_stats.csv"

pd.set_option("display.width", 120)

# Load data
df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.to_period("M").astype(str)
df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time.date())

print("DATA LOADED")
print(f"Total sessions: {len(df)}")
print(f"Total participants: {df['participant_id'].nunique()}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")

# 1. TOTALS & AVERAGES
print("\n1. TOTALS & AVERAGES")

total_sessions = len(df)
total_calories = df["calories_burned"].sum()
total_steps = df["daily_steps"].sum()
total_duration = df["duration_minutes"].sum()

avg_calories = df["calories_burned"].mean()
avg_steps = df["daily_steps"].mean()
avg_duration = df["duration_minutes"].mean()
avg_sleep = df["sleep_hours"].mean()
avg_heart_rate = df["avg_heart_rate"].mean()

print(f"Total sessions logged:        {total_sessions}")
print(f"Total calories burned:        {total_calories:,}")
print(f"Total steps recorded:         {total_steps:,}")
print(f"Total duration (minutes):     {total_duration:,}")
print(f"Average calories per session: {avg_calories:.2f}")
print(f"Average steps per session:    {avg_steps:.2f}")
print(f"Average duration per session: {avg_duration:.2f} min")
print(f"Average sleep hours:          {avg_sleep:.2f}")
print(f"Average heart rate:           {avg_heart_rate:.2f} bpm")

# Percentage of sessions that are "high intensity" (avg HR >= 130)
high_intensity_count = len(df[df["avg_heart_rate"] >= 130])
pct_high_intensity = high_intensity_count / total_sessions * 100
print(f"\n% of sessions that are high intensity (HR >= 130): {pct_high_intensity:.2f}%")

# Percentage of sessions with low sleep (<6h)
low_sleep_count = len(df[df["sleep_hours"] < 6])
pct_low_sleep = low_sleep_count / total_sessions * 100
print(f"% of sessions with low sleep (<6h):                 {pct_low_sleep:.2f}%")

# Percentage of sessions with calories burned >= 300
high_calorie_count = len(df[df["calories_burned"] >= 300])
pct_high_calorie = high_calorie_count / total_sessions * 100
print(f"% of sessions with calories burned >= 300:          {pct_high_calorie:.2f}%")

# Percentage of sessions meeting the step benchmark
high_steps_count = len(df[df["daily_steps"] >= STEP_BENCHMARK])
pct_high_steps = high_steps_count / total_sessions * 100
print(f"% of sessions with steps recorded >= {STEP_BENCHMARK:,}:        {pct_high_steps:.2f}%")

# Percentage of sessions with duration >= 60 minutes
long_duration_count = len(df[df["duration_minutes"] >= 60])
pct_long_duration = long_duration_count / total_sessions * 100
print(f"% of sessions with duration >= 60 minutes:          {pct_long_duration:.2f}%")

# 2. RANKINGS
print("\n2. RANKINGS")

# Rank A: Top 10 sessions by duration_minutes
rank_duration = df.copy()
rank_duration["rank"] = rank_duration["duration_minutes"].rank(ascending=False, method="min").astype(int)
rank_duration = rank_duration.sort_values("rank").head(10)
print("\nTop 10 sessions ranked by duration_minutes:")
print(rank_duration[["rank", "participant_id", "gender", "activity_type", "duration_minutes"]].to_string(index=False))

# Rank B: Top 10 sessions by calories_burned
rank_calories = df.copy()
rank_calories["rank"] = rank_calories["calories_burned"].rank(ascending=False, method="min").astype(int)
rank_calories = rank_calories.sort_values("rank").head(10)
print("\nTop 10 sessions ranked by calories_burned:")
print(rank_calories[["rank", "participant_id", "gender", "activity_type", "calories_burned"]].to_string(index=False))

# Rank C: Top 10 sessions by daily_steps
rank_steps = df.copy()
rank_steps["rank"] = rank_steps["daily_steps"].rank(ascending=False, method="min").astype(int)
rank_steps = rank_steps.sort_values("rank").head(10)
print("\nTop 10 sessions ranked by daily_steps:")
print(rank_steps[["rank", "participant_id", "gender", "activity_type", "daily_steps"]].to_string(index=False))

# Rank D: Top 10 sessions by avg_heart_rate
rank_heart_rate = df.copy()
rank_heart_rate["rank"] = rank_heart_rate["avg_heart_rate"].rank(ascending=False, method="min").astype(int)
rank_heart_rate = rank_heart_rate.sort_values("rank").head(10)
print("\nTop 10 sessions ranked by avg_heart_rate:")
print(rank_heart_rate[["rank", "participant_id", "gender", "activity_type", "avg_heart_rate"]].to_string(index=False))

# Rank E: Top 10 sessions by sleep_hours
rank_sleep = df.copy()
rank_sleep["rank"] = rank_sleep["sleep_hours"].rank(ascending=False, method="min").astype(int)
rank_sleep = rank_sleep.sort_values("rank").head(10)
print("\nTop 10 sessions ranked by sleep_hours:")
print(rank_sleep[["rank", "participant_id", "gender", "activity_type", "sleep_hours"]].to_string(index=False))

# 3. TRENDS
print("\n3. TRENDS")

# Monthly trend of key metrics
monthly_trend = df.groupby("month").agg(
    sessions=("activity_type", "count"),
    total_calories=("calories_burned", "sum"),
    avg_calories=("calories_burned", "mean"),
    total_duration=("duration_minutes", "sum"),
    avg_duration=("duration_minutes", "mean"),
    total_steps=("daily_steps", "sum"),
    avg_steps=("daily_steps", "mean"),
    avg_sleep_hours=("sleep_hours", "mean"),
    avg_heart_rate=("avg_heart_rate", "mean"),
).round(2).reset_index().sort_values("month")

monthly_trend["calories_trend_pct_change"] = (monthly_trend["avg_calories"].pct_change() * 100).round(2)

print("\nMonthly trend:")
print(monthly_trend.to_string(index=False))

# Weekly trend of total sessions and calories
weekly_trend = df.groupby("week").agg(
    sessions=("activity_type", "count"),
    total_calories=("calories_burned", "sum"),
    avg_calories=("calories_burned", "mean"),
    total_duration=("duration_minutes", "sum"),
    avg_duration=("duration_minutes", "mean"),
    total_steps=("daily_steps", "sum"),
    avg_steps=("daily_steps", "mean"),
    avg_sleep_hours=("sleep_hours", "mean"),
    avg_heart_rate=("avg_heart_rate", "mean"),
).reset_index().sort_values("week")

weekly_trend["calories_trend_pct_change"] = (weekly_trend["total_calories"].pct_change() * 100).round(2)

print("\nWeekly trend (first 10 weeks):")
print(weekly_trend.head(10).to_string(index=False))

# Export processed file
print("\nEXPORTING PROCESSED FILE")

df_export = df.drop(columns=["month", "week"]).sort_values(["participant_id", "date"])
df_export.to_csv(OUTPUT_FILE, index=False)
print(f"Processed dataset saved to: {OUTPUT_FILE}")
print(f"Rows exported: {len(df_export)}")
