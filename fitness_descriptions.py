"""Dynamic chart descriptions for PyPulse."""

import calendar
import pandas as pd
from fitness_analytics_stats import (
    compute_all_statistics,
    format_activity,
    STEP_BENCHMARK,
    LOW_SLEEP_HOURS,
)


# Correlation Strength and Direction
def _correlation_label(r):
    if r == 0:
        return "no linear"
    abs_r = abs(r)
    direction = "positive" if r > 0 else "negative"
    if abs_r >= 0.7:
        strength = "strong"
    elif abs_r >= 0.4:
        strength = "moderate"
    elif abs_r >= 0.2:
        strength = "weak"
    else:
        strength = "very weak"
    return f"{strength} {direction}"


# Period String to Month Name
def _month_label(period_str):
    parts = period_str.split("-")
    if len(parts) == 2:
        return calendar.month_name[int(parts[1])]
    return period_str


# Dominant Scatter Plot Quadrant
def _scatter_concentration(df):
    step_median = df["daily_steps"].median()
    cal_median  = df["calories_burned"].median()
    quadrants = {
        "high_step_high_cal": len(df[(df["daily_steps"] >  step_median) & (df["calories_burned"] >  cal_median)]),
        "low_step_high_cal":  len(df[(df["daily_steps"] <= step_median) & (df["calories_burned"] >  cal_median)]),
        "high_step_low_cal":  len(df[(df["daily_steps"] >  step_median) & (df["calories_burned"] <= cal_median)]),
        "low_step_low_cal":   len(df[(df["daily_steps"] <= step_median) & (df["calories_burned"] <= cal_median)]),
    }
    dominant = max(quadrants, key=quadrants.get)
    labels = {
        "high_step_high_cal": "most sessions cluster in the upper-right, meaning high step counts align with high calorie burn",
        "low_step_high_cal":  "many high-calorie sessions occur at lower step counts, likely from intense but stationary activities",
        "high_step_low_cal":  "many high-step sessions show moderate calorie burn, suggesting light-intensity walking dominates",
        "low_step_low_cal":   "the majority of sessions show both lower steps and lower calorie burn",
    }
    return labels[dominant]


# Chart Description Builder
def generate_chart_descriptions(df: pd.DataFrame, stats: dict = None) -> dict:
    if stats is None:
        stats = compute_all_statistics(df)

    eff   = stats["activity_effectiveness"]
    corr  = stats["correlation_matrix"]
    step  = stats["step_benchmark"]
    freq  = stats["activity_frequency"]
    pcts  = stats["percentages"]
    desc  = stats["descriptive"]

    highest_act  = format_activity(eff["highest_avg_calories"]["activity_type"])
    lowest_act   = format_activity(eff["lowest_avg_calories"]["activity_type"])
    highest_cal  = eff["highest_avg_calories"]["avg_calories"]
    lowest_cal   = eff["lowest_avg_calories"]["avg_calories"]
    most_eff_act = format_activity(eff["most_efficient"]["activity_type"])
    most_eff_cpm = eff["most_efficient"]["calories_per_minute"]

    most_common      = format_activity(freq.iloc[0]["activity_type"])
    least_common     = format_activity(freq.iloc[-1]["activity_type"])
    most_common_pct  = freq.iloc[0]["pct"]
    least_common_pct = freq.iloc[-1]["pct"]

    monthly    = stats["monthly_trend"]
    peak_month = _month_label(monthly.loc[monthly["avg_calories"].idxmax(), "month"])
    low_month  = _month_label(monthly.loc[monthly["avg_calories"].idxmin(), "month"])
    peak_cal   = round(monthly["avg_calories"].max(), 1)
    low_cal_m  = round(monthly["avg_calories"].min(), 1)
    trend_dir  = "upward" if monthly["avg_calories"].iloc[-1] > monthly["avg_calories"].iloc[0] else "downward"

    mean_sleep  = desc["sleep_hours"]["mean"]
    pct_healthy = round(len(df[(df["sleep_hours"] >= 7) & (df["sleep_hours"] <= 9)]) / len(df) * 100, 1)
    r_sleep_hr  = corr.loc["sleep_hours", "avg_heart_rate"]

    scatter_df      = df.dropna(subset=["daily_steps", "calories_burned"])
    r_steps_cal     = round(scatter_df["daily_steps"].corr(scatter_df["calories_burned"]), 3)
    concentration   = _scatter_concentration(scatter_df)
    scatter_act_cal = scatter_df.groupby("activity_type")["calories_burned"].mean()
    top_scatter_act = format_activity(scatter_act_cal.idxmax())
    top_scatter_cal = round(scatter_act_cal.max(), 1)
    mean_steps      = desc["daily_steps"]["mean"]

    return {
        "bar": (
            f"Among the {len(freq)} activity types tracked, {highest_act} records the highest average calorie burn "
            f"at {highest_cal:.0f} kcal per session, while {lowest_act} records the lowest at {lowest_cal:.0f} kcal. "
            f"The gap of {highest_cal - lowest_cal:.0f} kcal highlights how significant activity choice affects energy expenditure. "
            f"For maximum calorie output, prioritize {highest_act}; for time efficiency, {most_eff_act} leads at {most_eff_cpm:.1f} kcal/min. "
            f"{lowest_act} is best suited for active recovery sessions."
        ),
        "line": (
            f"Average calories burned per session fluctuated across the tracked period, peaking in {peak_month} at {peak_cal:.0f} kcal "
            f"and dropping lowest in {low_month} at {low_cal_m:.0f} kcal -- a difference of {peak_cal - low_cal_m:.0f} kcal. "
            f"The overall trend is {trend_dir}, "
            f"{'suggesting participants increased workout intensity over the period.' if trend_dir == 'upward' else 'suggesting workout intensity declined over the period.'} "
            f"Month-to-month variation may reflect seasonal changes or shifts in participant motivation."
        ),
        "pie": (
            f"{most_common} is the most frequently logged activity at {most_common_pct}% of all sessions, "
            f"while {least_common} is the least common at {least_common_pct}%. "
            f"{'The spread across activity types is relatively even, suggesting participants maintain varied routines.' if (most_common_pct - least_common_pct) < 15 else 'There is a noticeable imbalance in activity variety, with certain types dominating the logs.'} "
            f"Wellness coordinators can use this distribution to encourage underrepresented activities and promote variety."
        ),
        "histogram": (
            f"Sleep hours across all sessions average {mean_sleep:.2f} hours. "
            f"{pct_healthy:.1f}% of sessions fall within the recommended 7-9 hour healthy range, "
            f"while {pcts['low_sleep_pct']:.1f}% follow nights with fewer than {LOW_SLEEP_HOURS} hours of sleep. "
            f"The Pearson correlation between sleep hours and average heart rate is r = {r_sleep_hr:.3f} "
            f"({_correlation_label(r_sleep_hr)}), "
            f"{'confirming that less sleep is associated with elevated heart rate during activity.' if r_sleep_hr < 0 else 'suggesting sleep duration has limited influence on heart rate in this dataset.'} "
            f"Participants should aim for 7-9 hours of sleep to support cardiovascular recovery."
        ),
        "scatter": (
            f"The scatter plot shows the relationship between daily steps and calories burned across {len(scatter_df)} sessions. "
            f"The Pearson correlation is r = {r_steps_cal} ({_correlation_label(r_steps_cal)}): "
            f"{'as daily steps increase, calories burned tend to increase as well.' if r_steps_cal > 0 else 'daily step count alone is not a strong predictor of calorie burn in this dataset.'} "
            f"Looking at the point distribution, {concentration}. "
            f"Among all activity types, {top_scatter_act} shows the highest average calorie burn ({top_scatter_cal:.0f} kcal), "
            f"visible as a cluster of elevated points. "
            f"The trend line is {'positively sloped, reinforcing the step-calorie relationship.' if r_steps_cal > 0 else 'near flat, indicating other factors beyond step count drive calorie burn.'} "
            f"The cohort averages {mean_steps:,.0f} steps per session; "
            f"{step['participant_pct_met']:.1f}% of participants meet the {step['threshold']:,}-step daily benchmark "
            f"linked to meaningful health benefits."
        ),
    }


# Chart Renderer with Descriptions
def show_all_charts_with_descriptions(df: pd.DataFrame, stats: dict = None, save_dir: str = None) -> None:
    from fitness_analytics_viz import (
        plot_bar_calories_by_activity,
        plot_line_monthly_calories,
        plot_pie_activity_distribution,
        plot_histogram_sleep,
        plot_scatter_steps_vs_calories,
    )

    if stats is None:
        stats = compute_all_statistics(df)

    descriptions = generate_chart_descriptions(df, stats)

    # Save Path Builder
    def path(filename):
        import os
        return os.path.join(save_dir, filename) if save_dir else None

    # Single Chart Display
    def show(fn, df, filepath, key):
        fn(df, filepath)
        text = descriptions.get(key, "")
        if text:
            print(f"\n  [Insight] {text}\n")

    print("\n[PyPulse] Generating charts with descriptions...")
    show(plot_bar_calories_by_activity,  df, path("bar_calories_by_activity.png"),  "bar")
    show(plot_line_monthly_calories,     df, path("line_monthly_calories.png"),      "line")
    show(plot_pie_activity_distribution, df, path("pie_activity_distribution.png"), "pie")
    show(plot_histogram_sleep,           df, path("histogram_sleep_hours.png"),      "histogram")
    show(plot_scatter_steps_vs_calories, df, path("scatter_steps_vs_calories.png"), "scatter")
    print("[PyPulse] Done.\n")


# Script Entry Point
if __name__ == "__main__":
    df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])
    stats = compute_all_statistics(df)
    descriptions = generate_chart_descriptions(df, stats)
    for key, text in descriptions.items():
        print(f"\n--- {key.upper()} ---")
        print(text)