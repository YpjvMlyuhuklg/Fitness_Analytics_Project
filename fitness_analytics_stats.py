# =====================================================================================
# PyPulse: A Python-Driven Analytics System for Health and Fitness Tracking
# fitness_analytics_stats.py - Statistical & Analytical Computations
#
# ROLE OF THIS FILE:
#   This file is responsible for Phase 5 of the project workflow:
#   Statistical and Analytical Computations. It takes the cleaned DataFrame
#   produced by cleaning.py and returns a single dictionary of every computed
#   result, which the Tkinter GUI (main app) can then display.
#
# HOW TO USE (from the main Tkinter app or any other file):
#   from fitness_analytics_stats import compute_all_statistics, print_statistics_report
#
#   df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
#   df["date"] = pd.to_datetime(df["date"])
#   stats = compute_all_statistics(df)
#
# OVERLAP NOTICE -- READ BEFORE INTEGRATING:
#   Several computations in this file duplicate work already done by our other
#   group members. This is intentional: this file is SELF-CONTAINED so it can
#   be tested independently. When integrating to the final Tkinter app,
#   decide whether to:
#     (A) call compute_all_statistics() and discard the overlapping standalone
#         scripts, OR
#     (B) import specific results from the standalone scripts and skip the
#         overlapping sections here.
#     (C) run both, but keep in mind that the overlapping computations will
#         execute twice.
#   Either approach is fine, just don't run both in the same app session,
#   or the same computation will execute twice.
#
#   Specific overlaps are marked with # [OVERLAP] comments below.
#
# EXPECTED COLUMNS (output of cleaning.py):
#   participant_id, date (datetime), gender, activity_type,
#   duration_minutes, calories_burned, daily_steps,
#   avg_heart_rate, sleep_hours
# =====================================================================================


# Import necessary libraries
import pandas as pd
import numpy as np

# Numeric columns that statistical functions are applied to
NUMERIC_COLS = [
    "duration_minutes",
    "calories_burned",
    "daily_steps",
    "avg_heart_rate",
    "sleep_hours",
]

# Human-readable labels used in the printed report and GUI displays
COL_LABELS = {
    "duration_minutes"  :   "Duration (min)",
    "calories_burned"   :   "Calories Burned (kcal)",
    "daily_steps"       :   "Daily Steps",
    "avg_heart_rate"    :   "Avg Heart Rate (bpm)",
    "sleep_hours"       :   "Sleep Hours",
}


# ==========================================================
# MAIN FUNCTION - returns a dict with every computed result
# ==========================================================

def compute_all_statistics(df: pd.DataFrame) -> dict:
    """
    Run all statistical and analytical computations on the cleaned DataFrame.

    Parameters
    ----------
    df : Cleaned pandas DataFrame. The 'date' column must already be
         converted to datetime (pd.to_datetime) before calling this.

    Returns
    -------
    dict with the following keys:
        descriptive         - per-column mean/median/mode/std/min/max
        percentages         - key session percentages (high intensity, etc.)
        activity_summary    - grouped totals & averages by activity type
        gender_summary      - grouped totals & averages by gender
        gender_activity     - cross-tab of gender x activity type
        participant_summary - grouped totals & averages by participant
        monthly_trend       - month-by-month averages and totals
        weekly_trend        - week-by-week averages and totals
        correlation_matrix  - Pearson correlations between numeric columns
        activity_frequency  - session count and % share per activity type
        rankings            - top-10 sessions for each numeric metric
    """

    # Initialize the stats dictionary that will hold all computed results
    stats = {}

    # -------------------------------------------------------------------------
    # 1. DESCRIPTIVE STATISTICS
    #    Computes mean, median, mode, std, min, max for every numeric column.
    #
    #    [OVERLAP] fitness_analytics_totals_trends_corr.py already prints
    #    avg_calories, avg_steps, avg_duration, avg_sleep, and avg_heart_rate
    #    (the means) under its "TOTALS & AVERAGES" section. This block goes
    #    further by also computing median, mode, std, min, and max, so it is
    #    not a full duplicate, but the means will match exactly.
    # -------------------------------------------------------------------------
    descriptive = {}
    for col in NUMERIC_COLS:
        s = df[col].dropna()
        descriptive[col] = {
            "mean"      :   round(float(s.mean()),   2),
            "median"    :   round(float(s.median()), 2),
            "mode"      :   round(float(s.mode().iloc[0]), 2) if not s.mode().empty else None,
            "std"       :   round(float(s.std()),    2),
            "min"       :   round(float(s.min()),    2),
            "max"       :   round(float(s.max()),    2),
        }
    stats["descriptive"] = descriptive

    # -------------------------------------------------------------------------
    # 2. KEY SESSION PERCENTAGES
    #    Calculates what share of sessions meet specific health thresholds.
    #
    #    [OVERLAP] fitness_analytics_totals_trends_corr.py computes the same
    #    five percentages (pct_high_intensity, pct_low_sleep, pct_high_calorie,
    #    pct_high_steps, pct_long_duration) under its "TOTALS & AVERAGES"
    #    section. The values here will be identical.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    total = len(df)
    stats["percentages"] = {
        "high_intensity_pct": round(len(df[df["avg_heart_rate"] >= 130])  / total * 100, 2),
        "low_sleep_pct":      round(len(df[df["sleep_hours"] < 6])        / total * 100, 2),
        "high_calorie_pct":   round(len(df[df["calories_burned"] >= 300]) / total * 100, 2),
        "high_steps_pct":     round(len(df[df["daily_steps"] >= 10000])   / total * 100, 2),
        "long_session_pct":   round(len(df[df["duration_minutes"] >= 60]) / total * 100, 2),
    }

    # -------------------------------------------------------------------------
    # 3. ACTIVITY TYPE SUMMARY
    #    Groups sessions by activity type and aggregates key metrics.
    #
    #    [OVERLAP] fitness_analytics_filter_sort_group.py produces 'by_activity'
    #    (Group B) with the same groupby logic: sessions, total_calories,
    #    avg_calories, avg_duration, avg_steps, and pct_of_all_sessions.
    #    This block adds avg_heart_rate and avg_sleep on top of that, so it
    #    is a superset of what that file computes.
    #    Integration group member: this block can replace by_activity from
    #    filter_sort_group if you prefer one source.
    # -------------------------------------------------------------------------
    stats["activity_summary"] = (
        df.groupby("activity_type")
        .agg(
            sessions       = ("activity_type",    "count"),
            total_calories = ("calories_burned",  "sum"),
            avg_calories   = ("calories_burned",  "mean"),
            avg_duration   = ("duration_minutes", "mean"),
            avg_steps      = ("daily_steps",      "mean"),
            avg_heart_rate = ("avg_heart_rate",   "mean"),
            avg_sleep      = ("sleep_hours",      "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_calories", ascending=False)
    )

    # -------------------------------------------------------------------------
    # 4. GENDER SUMMARY
    #    Groups sessions by gender and aggregates key metrics.
    #
    #    [OVERLAP] fitness_analytics_filter_sort_group.py produces 'by_gender'
    #    (Group C) with the same groupby: sessions, total_calories,
    #    avg_calories, avg_steps, avg_sleep_hours. The values will match.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    stats["gender_summary"] = (
        df.groupby("gender")
        .agg(
            sessions       = ("activity_type",   "count"),
            total_calories = ("calories_burned", "sum"),
            avg_calories   = ("calories_burned", "mean"),
            avg_steps      = ("daily_steps",     "mean"),
            avg_sleep      = ("sleep_hours",     "mean"),
            avg_heart_rate = ("avg_heart_rate",  "mean"),
        )
        .round(2)
        .reset_index()
    )

    # -------------------------------------------------------------------------
    # 5. GENDER x ACTIVITY CROSS-TAB
    #    Groups by both gender and activity type together.
    #
    #    [OVERLAP] fitness_analytics_filter_sort_group.py produces
    #    'by_gender_activity' (Group D) with identical logic: groupby
    #    ["gender", "activity_type"], aggregating sessions and avg_calories.
    #    The values here will be identical.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    stats["gender_activity"] = (
        df.groupby(["gender", "activity_type"])
        .agg(
            sessions     = ("activity_type",   "count"),
            avg_calories = ("calories_burned", "mean"),
        )
        .round(2)
        .reset_index()
    )

    # -------------------------------------------------------------------------
    # 6. PARTICIPANT SUMMARY
    #    Groups sessions by participant and aggregates totals and averages.
    #
    #    [OVERLAP] fitness_analytics_filter_sort_group.py produces
    #    'by_participant' (Group A) with the same groupby: total_sessions,
    #    total_calories, avg_calories, total_steps, avg_steps, avg_sleep_hours.
    #    The values here will be identical.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    stats["participant_summary"] = (
        df.groupby("participant_id")
        .agg(
            total_sessions = ("activity_type",    "count"),
            total_calories = ("calories_burned",  "sum"),
            avg_calories   = ("calories_burned",  "mean"),
            total_steps    = ("daily_steps",      "sum"),
            avg_steps      = ("daily_steps",      "mean"),
            avg_sleep      = ("sleep_hours",      "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_calories", ascending=False)
    )

    # -------------------------------------------------------------------------
    # 7. MONTHLY TREND
    #    Groups sessions by calendar month and computes averages and totals.
    #
    #    [OVERLAP] fitness_analytics_totals_trends_corr.py produces
    #    'monthly_trend' with the same groupby("month") and the same metrics:
    #    sessions, total_calories, avg_calories, total_steps, avg_steps,
    #    avg_sleep_hours, avg_heart_rate, avg_duration, and
    #    calories_trend_pct_change. The values here will be identical.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    df_m = df.copy()
    df_m["month"] = df_m["date"].dt.to_period("M").astype(str)
    monthly = (
        df_m.groupby("month")
        .agg(
            sessions       = ("activity_type",   "count"),
            total_calories = ("calories_burned",  "sum"),
            avg_calories   = ("calories_burned",  "mean"),
            total_steps    = ("daily_steps",      "sum"),
            avg_steps      = ("daily_steps",      "mean"),
            avg_sleep      = ("sleep_hours",      "mean"),
            avg_heart_rate = ("avg_heart_rate",   "mean"),
            avg_duration   = ("duration_minutes", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("month")
    )
    monthly["calories_pct_change"] = (
        monthly["avg_calories"].pct_change() * 100
    ).round(2)
    stats["monthly_trend"] = monthly

    # -------------------------------------------------------------------------
    # 8. WEEKLY TREND
    #    Groups sessions by calendar week and computes averages and totals.
    #
    #    [OVERLAP] fitness_analytics_totals_trends_corr.py produces
    #    'weekly_trend' with the same groupby("week") logic and the same
    #    metrics. The values here will be identical.
    #    Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    df_w = df.copy()
    df_w["week"] = df_w["date"].dt.to_period("W").apply(
        lambda r: str(r.start_time.date())
    )
    weekly = (
        df_w.groupby("week")
        .agg(
            sessions       = ("activity_type",    "count"),
            total_calories = ("calories_burned",  "sum"),
            avg_calories   = ("calories_burned",  "mean"),
            total_steps    = ("daily_steps",      "sum"),
            avg_steps      = ("daily_steps",      "mean"),
            avg_sleep      = ("sleep_hours",      "mean"),
            avg_heart_rate = ("avg_heart_rate",   "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("week")
    )
    weekly["calories_pct_change"] = (
        weekly["total_calories"].pct_change() * 100
    ).round(2)
    stats["weekly_trend"] = weekly

    # -------------------------------------------------------------------------
    # 9. CORRELATION MATRIX
    #    Pearson correlation coefficients between all five numeric columns.
    #
    #    [NO OVERLAP] fitness_analytics_totals_trends_corr.py does NOT compute
    #    a full correlation matrix. This block is unique to this file.
    #    The paper specifically calls out three correlations:
    #      - duration_minutes vs. calories_burned  (expected: strong positive)
    #      - sleep_hours vs. avg_heart_rate        (expected: negative)
    #      - daily_steps vs. calories_burned       (expected: positive)
    #    All three (3) are readable from this matrix.
    # -------------------------------------------------------------------------
    stats["correlation_matrix"] = df[NUMERIC_COLS].corr().round(3)

    # -------------------------------------------------------------------------
    # 10. ACTIVITY FREQUENCY DISTRIBUTION
    #     Count and percentage share of sessions per activity type.
    #
    #     [OVERLAP] fitness_analytics_filter_sort_group.py computes
    #     pct_of_all_sessions inside 'by_activity' (Group B). This block
    #     isolates just the frequency counts and percentages as a standalone
    #     table, which is more convenient for the pie chart in
    #     fitness_analytics_viz.py. The values will match.
    # -------------------------------------------------------------------------
    counts = df["activity_type"].value_counts().reset_index()
    counts.columns = ["activity_type", "count"]
    counts["pct"] = (counts["count"] / total * 100).round(2)
    stats["activity_frequency"] = counts

    # -------------------------------------------------------------------------
    # 11. RANKINGS (top 10 per numeric metric)
    #     Sorts the full dataset by each numeric column and returns the top 10.
    #
    #     [OVERLAP] fitness_analytics_totals_trends_corr.py computes top-10
    #     rankings for duration, calories, steps, heart rate, and sleep
    #     (Rank A through Rank E) using the same sort logic. The rows
    #     returned here will be identical to those in that file.
    #     Integration group member: use one or the other, not both.
    # -------------------------------------------------------------------------
    rankings = {}
    for col in NUMERIC_COLS:
        top = (
            df.copy()
            .sort_values(col, ascending=False)
            .head(10)[["participant_id", "date", "gender", "activity_type", col]]
            .reset_index(drop=True)
        )
        top.index += 1       # rank starts at 1
        top.index.name = "rank"
        rankings[col] = top
    stats["rankings"] = rankings

    return stats


# =============================================================================
# PRINT REPORT (Not everything above is printed, this is only for testing)
# Can be used for console testing or piped into a Tkinter ScrolledText widget.
# =============================================================================

def print_statistics_report(stats: dict) -> None:
    """Pretty-print the full statistics report to the console."""
    SEP  = "=" * 75
    SEP2 = "-" * 75

    print(f"\n{SEP}")
    print("  PYPULSE -- STATISTICAL & ANALYTICAL REPORT")
    print(SEP)

    # Descriptive statistics
    print("\n[1] DESCRIPTIVE STATISTICS")
    print(SEP2)
    for col, s in stats["descriptive"].items():
        print(f"\n  {COL_LABELS[col]}")
        print(f"    Mean    : {s['mean']}")
        print(f"    Median  : {s['median']}")
        print(f"    Mode    : {s['mode']}")
        print(f"    Std Dev : {s['std']}")
        print(f"    Min     : {s['min']}")
        print(f"    Max     : {s['max']}")

    # Key percentages
    print(f"\n[2] KEY SESSION PERCENTAGES")
    print(SEP2)
    p = stats["percentages"]
    print(f"  High intensity (HR >= 130 bpm) : {p['high_intensity_pct']}%")
    print(f"  Low sleep      (< 6 hrs)       : {p['low_sleep_pct']}%")
    print(f"  High calorie   (>= 300 kcal)   : {p['high_calorie_pct']}%")
    print(f"  High steps     (>= 10,000)     : {p['high_steps_pct']}%")
    print(f"  Long session   (>= 60 min)     : {p['long_session_pct']}%")

    # Activity summary
    print(f"\n[3] ACTIVITY TYPE SUMMARY")
    print(SEP2)
    print(stats["activity_summary"].to_string(index=False))

    # Gender summary
    print(f"\n[4] GENDER SUMMARY")
    print(SEP2)
    print(stats["gender_summary"].to_string(index=False))

    # Monthly trend
    print(f"\n[5] MONTHLY TREND")
    print(SEP2)
    print(stats["monthly_trend"].to_string(index=False))

    # Correlation matrix
    print(f"\n[6] CORRELATION MATRIX")
    print(SEP2)
    print(stats["correlation_matrix"].to_string())

    # Activity frequency
    print(f"\n[7] ACTIVITY FREQUENCY DISTRIBUTION")
    print(SEP2)
    print(stats["activity_frequency"].to_string(index=False))

    # Rankings
    print(f"\n[8] TOP 10 RANKINGS")
    print(SEP2)
    for col, df_rank in stats["rankings"].items():
        print(f"\n  Ranked by: {COL_LABELS[col]}")
        print(df_rank.to_string())

    print(f"\n{SEP}\n")


# ============================================================
# LOCAL TEST -- remove or comment out before final submission
# ============================================================

if __name__ == "__main__":
    df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])

    stats = compute_all_statistics(df)
    print_statistics_report(stats)