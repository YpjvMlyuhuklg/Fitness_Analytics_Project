"""Statistical computations, insights, and report text for PyPulse."""

import pandas as pd

STEP_BENCHMARK = 7000
HIGH_INTENSITY_HR = 130
LOW_SLEEP_HOURS = 6
HIGH_CALORIE = 300
LONG_SESSION_MIN = 60

NUMERIC_COLS = [
    "duration_minutes",
    "calories_burned",
    "daily_steps",
    "avg_heart_rate",
    "sleep_hours",
]

COL_LABELS = {
    "duration_minutes": "Duration (min)",
    "calories_burned": "Calories Burned (kcal)",
    "daily_steps": "Daily Steps",
    "avg_heart_rate": "Avg Heart Rate (bpm)",
    "sleep_hours": "Sleep Hours",
    "calories_per_minute": "Calories per Minute",
    "activity_type": "Activity Type",
    "gender": "Gender",
    "sessions": "Sessions",
    "total_calories": "Total Calories",
    "avg_calories": "Avg Calories",
    "avg_duration": "Avg Duration",
    "avg_steps": "Avg Steps",
    "avg_heart_rate": "Avg Heart Rate",
    "avg_sleep": "Avg Sleep (hrs)",
    "participant_id": "Participant",
    "risk_reason": "Risk Flags",
}


def format_activity(name) -> str:
    text = str(name)
    return "HIIT" if text == "Hiit" else text


def format_display_value(col: str, val):
    if pd.isna(val):
        return ""
    if col == "activity_type":
        return format_activity(val)
    if col in ("daily_steps", "avg_steps", "total_steps", "sessions", "total_sessions"):
        return f"{int(round(float(val))):,}"
    if col in ("avg_heart_rate",):
        return f"{float(val):.0f}"
    if isinstance(val, float) and col not in ("calories_per_minute",):
        if col in ("avg_calories", "avg_duration", "avg_sleep", "total_calories"):
            return f"{val:.2f}"
        return f"{val:,.2f}" if abs(val) >= 100 else f"{val:.2f}"
    return val


def compute_all_statistics(df: pd.DataFrame) -> dict:
    """Return all analytics used by the GUI and summary report."""
    total = len(df)

    descriptive = {}
    for col in NUMERIC_COLS:
        s = df[col].dropna()
        descriptive[col] = {
            "mean": round(float(s.mean()), 2),
            "median": round(float(s.median()), 2),
            "mode": round(float(s.mode().iloc[0]), 2) if not s.mode().empty else None,
            "std": round(float(s.std()), 2),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
        }

    activity = (
        df.groupby("activity_type")
        .agg(
            sessions=("activity_type", "count"),
            total_calories=("calories_burned", "sum"),
            avg_calories=("calories_burned", "mean"),
            avg_duration=("duration_minutes", "mean"),
            avg_steps=("daily_steps", "mean"),
            avg_heart_rate=("avg_heart_rate", "mean"),
            avg_sleep=("sleep_hours", "mean"),
        )
        .round(2)
        .reset_index()
    )
    activity["calories_per_minute"] = (
        activity["avg_calories"] / activity["avg_duration"]
    ).round(2)

    by_calories = activity.sort_values("avg_calories", ascending=False).reset_index(drop=True)
    by_efficiency = activity.sort_values("calories_per_minute", ascending=False).reset_index(drop=True)

    participant_steps = df.groupby("participant_id")["daily_steps"].mean()
    participants_met = int((participant_steps >= STEP_BENCHMARK).sum())
    participant_total = len(participant_steps)

    participant_summary = (
        df.groupby("participant_id")
        .agg(
            total_sessions=("activity_type", "count"),
            total_calories=("calories_burned", "sum"),
            avg_calories=("calories_burned", "mean"),
            total_steps=("daily_steps", "sum"),
            avg_steps=("daily_steps", "mean"),
            avg_sleep=("sleep_hours", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_calories", ascending=False)
    )

    at_risk = participant_summary[
        (participant_summary["avg_steps"] < STEP_BENCHMARK)
        | (participant_summary["avg_sleep"] < LOW_SLEEP_HOURS)
    ].copy()
    flags = []
    for _, row in at_risk.iterrows():
        reasons = []
        if row["avg_steps"] < STEP_BENCHMARK:
            reasons.append(f"low steps ({row['avg_steps']:.0f})")
        if row["avg_sleep"] < LOW_SLEEP_HOURS:
            reasons.append(f"low sleep ({row['avg_sleep']:.1f}h)")
        flags.append(", ".join(reasons))
    at_risk["risk_reason"] = flags

    return {
        "descriptive": descriptive,
        "percentages": {
            "high_intensity_pct": round(len(df[df["avg_heart_rate"] >= HIGH_INTENSITY_HR]) / total * 100, 2),
            "low_sleep_pct": round(len(df[df["sleep_hours"] < LOW_SLEEP_HOURS]) / total * 100, 2),
            "high_calorie_pct": round(len(df[df["calories_burned"] >= HIGH_CALORIE]) / total * 100, 2),
            "steps_benchmark_pct": round(len(df[df["daily_steps"] >= STEP_BENCHMARK]) / total * 100, 2),
            "long_session_pct": round(len(df[df["duration_minutes"] >= LONG_SESSION_MIN]) / total * 100, 2),
        },
        "activity_summary": by_calories,
        "activity_by_efficiency": by_efficiency,
        "activity_effectiveness": {
            "highest_avg_calories": by_calories.iloc[0].to_dict(),
            "lowest_avg_calories": by_calories.iloc[-1].to_dict(),
            "most_efficient": by_efficiency.iloc[0].to_dict(),
            "least_efficient": by_efficiency.iloc[-1].to_dict(),
        },
        "step_benchmark": {
            "threshold": STEP_BENCHMARK,
            "participants_met": participants_met,
            "participants_total": participant_total,
            "participant_pct_met": round(participants_met / participant_total * 100, 2) if participant_total else 0,
        },
        "gender_summary": (
            df.groupby("gender")
            .agg(
                sessions=("activity_type", "count"),
                total_calories=("calories_burned", "sum"),
                avg_calories=("calories_burned", "mean"),
                avg_steps=("daily_steps", "mean"),
                avg_sleep=("sleep_hours", "mean"),
                avg_heart_rate=("avg_heart_rate", "mean"),
            )
            .round(2)
            .reset_index()
        ),
        "gender_activity": (
            df.groupby(["gender", "activity_type"])
            .agg(sessions=("activity_type", "count"), avg_calories=("calories_burned", "mean"))
            .round(2)
            .reset_index()
        ),
        "participant_summary": participant_summary,
        "at_risk_participants": at_risk.sort_values("avg_steps"),
        "monthly_trend": _monthly_trend(df),
        "weekly_trend": _weekly_trend(df),
        "correlation_matrix": df[NUMERIC_COLS].corr().round(3),
        "activity_frequency": _activity_frequency(df, total),
        "rankings": _rankings(df),
    }


def _monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    trend = (
        monthly.groupby("month")
        .agg(
            sessions=("activity_type", "count"),
            total_calories=("calories_burned", "sum"),
            avg_calories=("calories_burned", "mean"),
            total_steps=("daily_steps", "sum"),
            avg_steps=("daily_steps", "mean"),
            avg_sleep=("sleep_hours", "mean"),
            avg_heart_rate=("avg_heart_rate", "mean"),
            avg_duration=("duration_minutes", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("month")
    )
    trend["calories_pct_change"] = (trend["avg_calories"].pct_change() * 100).round(2)
    return trend


def _weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    weekly = df.copy()
    weekly["week"] = weekly["date"].dt.to_period("W").apply(lambda r: str(r.start_time.date()))
    trend = (
        weekly.groupby("week")
        .agg(
            sessions=("activity_type", "count"),
            total_calories=("calories_burned", "sum"),
            avg_calories=("calories_burned", "mean"),
            total_steps=("daily_steps", "sum"),
            avg_steps=("daily_steps", "mean"),
            avg_sleep=("sleep_hours", "mean"),
            avg_heart_rate=("avg_heart_rate", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("week")
    )
    trend["calories_pct_change"] = (trend["total_calories"].pct_change() * 100).round(2)
    return trend


def _activity_frequency(df: pd.DataFrame, total: int) -> pd.DataFrame:
    counts = df["activity_type"].value_counts().reset_index()
    counts.columns = ["activity_type", "count"]
    counts["pct"] = (counts["count"] / total * 100).round(2)
    return counts


def _rankings(df: pd.DataFrame) -> dict:
    rankings = {}
    for col in NUMERIC_COLS:
        top = (
            df.sort_values(col, ascending=False)
            .head(10)[["participant_id", "date", "gender", "activity_type", col]]
            .reset_index(drop=True)
        )
        top.index += 1
        top.index.name = "rank"
        rankings[col] = top
    return rankings


def build_stakeholder_insights(stats: dict) -> dict:
    """Short insight blurbs tailored to each stakeholder group."""
    eff = stats["activity_effectiveness"]
    step = stats["step_benchmark"]
    desc = stats["descriptive"]
    pcts = stats["percentages"]
    at_risk = stats["at_risk_participants"]
    top = format_activity(stats["activity_frequency"].iloc[0]["activity_type"])

    return {
        "individuals": (
            f"Cohort averages {desc['daily_steps']['mean']:,.0f} steps and {desc['sleep_hours']['mean']:.1f} hrs sleep per session. "
            f"{pcts['steps_benchmark_pct']:.1f}% of sessions meet the {STEP_BENCHMARK:,}-step benchmark. "
            f"Most logged activity: {top}."
        ),
        "coaches": (
            f"Highest session burn: {format_activity(eff['highest_avg_calories']['activity_type'])} "
            f"({eff['highest_avg_calories']['avg_calories']:.0f} kcal). "
            f"Best time efficiency: {format_activity(eff['most_efficient']['activity_type'])} "
            f"({eff['most_efficient']['calories_per_minute']:.1f} kcal/min). "
            f"Use {format_activity(eff['lowest_avg_calories']['activity_type'])} for recovery programming."
        ),
        "administrators": (
            f"{len(at_risk)} of {step['participants_total']} participants ({100 - step['participant_pct_met']:.0f}% below step target) "
            f"may need wellness intervention (avg steps < {STEP_BENCHMARK:,} or sleep < {LOW_SLEEP_HOURS}h). "
            f"{pcts['low_sleep_pct']:.1f}% of sessions follow low-sleep nights."
        ),
    }


def generate_recommendations(stats: dict) -> list[str]:
    """Build data-driven recommendations from computed statistics."""
    eff = stats["activity_effectiveness"]
    step = stats["step_benchmark"]
    pcts = stats["percentages"]
    corr = stats["correlation_matrix"]
    desc = stats["descriptive"]

    r_sleep_hr = corr.loc["sleep_hours", "avg_heart_rate"]
    r_dur_cal = corr.loc["duration_minutes", "calories_burned"]

    recs = [
        (
            f"For maximum calories per session, prioritize {format_activity(eff['highest_avg_calories']['activity_type'])} "
            f"({eff['highest_avg_calories']['avg_calories']:.0f} kcal avg). "
            f"For time-limited workouts, choose {format_activity(eff['most_efficient']['activity_type'])} "
            f"({eff['most_efficient']['calories_per_minute']:.1f} kcal/min)."
        ),
        (
            f"{step['participants_met']} of {step['participants_total']} participants "
            f"({step['participant_pct_met']:.1f}%) average at least {step['threshold']:,} daily steps. "
            f"Participants below this threshold should increase daily walking or active commuting."
        ),
        (
            f"{pcts['low_sleep_pct']:.1f}% of sessions follow nights with under {LOW_SLEEP_HOURS} hours of sleep. "
            f"Sleep and heart rate correlate at r={r_sleep_hr:.3f}; schedule high-intensity work after adequate rest."
        ),
        (
            f"Workout duration and calories correlate at r={r_dur_cal:.3f}. "
            f"Sessions under {LONG_SESSION_MIN} minutes can still be effective when choosing efficient activities "
            f"such as {format_activity(eff['most_efficient']['activity_type'])}."
        ),
        (
            f"Average daily steps are {desc['daily_steps']['mean']:,.0f}. "
            f"Use {format_activity(eff['lowest_avg_calories']['activity_type'])} for recovery days "
            f"({eff['lowest_avg_calories']['avg_calories']:.0f} kcal avg) and reserve high-burn activities for peak training days."
        ),
    ]
    return recs


def build_summary_report(stats: dict, df: pd.DataFrame, raw_path: str, cleaned_path: str) -> str:
    """Build the full text report shown in the GUI."""
    desc = stats["descriptive"]
    eff = stats["activity_effectiveness"]
    step = stats["step_benchmark"]
    corr = stats["correlation_matrix"]
    top_activity = stats["activity_frequency"].iloc[0]
    recommendations = generate_recommendations(stats)
    stakeholders = build_stakeholder_insights(stats)

    rec_block = "\n".join(f"  {i}. {rec}" for i, rec in enumerate(recommendations, 1))

    return f"""=============================================================================
             PYPULSE: DATA ANALYTICS & INSIGHTS REPORT
                  Fitness and Health Tracking System
=============================================================================

[1] SYSTEM OVERVIEW
-----------------------------------------------------------------------------
Raw file              : {raw_path}
Cleaned file          : {cleaned_path}
Date range            : {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
Participants          : {df['participant_id'].nunique()}
Workout logs          : {len(df)}

[2] DESCRIPTIVE STATISTICS
-----------------------------------------------------------------------------
| Variable         | Mean      | Median    | Std Dev   | Range (Min-Max)      |
|------------------|-----------|-----------|-----------|----------------------|
| Duration (min)   | {desc['duration_minutes']['mean']:<9} | {desc['duration_minutes']['median']:<9} | {desc['duration_minutes']['std']:<9} | {desc['duration_minutes']['min']} - {desc['duration_minutes']['max']} |
| Calories (kcal)  | {desc['calories_burned']['mean']:<9} | {desc['calories_burned']['median']:<9} | {desc['calories_burned']['std']:<9} | {desc['calories_burned']['min']} - {desc['calories_burned']['max']} |
| Daily Steps      | {desc['daily_steps']['mean']:<9.0f} | {desc['daily_steps']['median']:<9.0f} | {desc['daily_steps']['std']:<9.0f} | {desc['daily_steps']['min']} - {desc['daily_steps']['max']} |
| Heart Rate (bpm) | {desc['avg_heart_rate']['mean']:<9} | {desc['avg_heart_rate']['median']:<9} | {desc['avg_heart_rate']['std']:<9} | {desc['avg_heart_rate']['min']} - {desc['avg_heart_rate']['max']} |
| Sleep (hrs)      | {desc['sleep_hours']['mean']:<9} | {desc['sleep_hours']['median']:<9} | {desc['sleep_hours']['std']:<9} | {desc['sleep_hours']['min']} - {desc['sleep_hours']['max']} |

[3] ACTIVITY EFFECTIVENESS
-----------------------------------------------------------------------------
Highest avg calories per session : {format_activity(eff['highest_avg_calories']['activity_type'])} ({eff['highest_avg_calories']['avg_calories']:.0f} kcal)
Most calories per minute         : {format_activity(eff['most_efficient']['activity_type'])} ({eff['most_efficient']['calories_per_minute']:.1f} kcal/min)
Lowest avg calories per session  : {format_activity(eff['lowest_avg_calories']['activity_type'])} ({eff['lowest_avg_calories']['avg_calories']:.0f} kcal)

Ranked by avg calories:
{stats['activity_summary'][['activity_type', 'avg_calories', 'calories_per_minute']].to_string(index=False)}

[4] KEY FINDINGS
-----------------------------------------------------------------------------
* Most logged activity: {top_activity['activity_type']} ({top_activity['count']} sessions, {top_activity['pct']}%)
* Step benchmark ({step['threshold']:,} steps): {step['participants_met']}/{step['participants_total']} participants meet it ({step['participant_pct_met']:.1f}%)
* Duration vs calories: r = {corr.loc['duration_minutes', 'calories_burned']:.3f}
* Sleep vs heart rate: r = {corr.loc['sleep_hours', 'avg_heart_rate']:.3f}
* Steps vs calories: r = {corr.loc['daily_steps', 'calories_burned']:.3f}

[5] RECOMMENDATIONS
-----------------------------------------------------------------------------
{rec_block}

[6] STAKEHOLDER INSIGHTS
-----------------------------------------------------------------------------
Health-Conscious Individuals : {stakeholders['individuals']}
Athletic Trainers & Coaches  : {stakeholders['coaches']}
Wellness Administrators      : {stakeholders['administrators']}

At-risk participants ({len(stats['at_risk_participants'])}):
{stats['at_risk_participants'][['participant_id', 'avg_steps', 'avg_sleep', 'risk_reason']].to_string(index=False) if len(stats['at_risk_participants']) else '  None identified'}

=============================================================================
Report generated by PyPulse from cleaned tracker data.
=============================================================================
"""


def print_statistics_report(stats: dict) -> None:
    """Console-friendly stats dump for standalone testing."""
    sep = "=" * 60
    print(f"\n{sep}\nPyPulse Statistical Report\n{sep}")
    for col, values in stats["descriptive"].items():
        print(f"\n{COL_LABELS[col]}")
        for key, val in values.items():
            print(f"  {key}: {val}")
    print(f"\nRecommendations:")
    for rec in generate_recommendations(stats):
        print(f"  - {rec}")
    print(sep)


if __name__ == "__main__":
    df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])
    print_statistics_report(compute_all_statistics(df))
