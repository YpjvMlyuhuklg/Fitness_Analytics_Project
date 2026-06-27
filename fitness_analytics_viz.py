# =============================================================================
# PyPulse: A Python-Driven Analytics System for Health and Fitness Tracking
# fitness_analytics_viz.py - Data Visualizations
#
# ROLE OF THIS FILE:
#   This file is responsible for Phase 6 of the project workflow:
#   Data Visualization. It takes the cleaned DataFrame produced by
#   cleaning.py and generates all required charts.
#
# HOW TO USE (from the main Tkinter app or any other file):
#   from fitness_analytics_viz import show_all_charts
#
#   df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
#   df["date"] = pd.to_datetime(df["date"])
#
#   # Show charts interactively (one at a time, blocks until closed):
#   show_all_charts(df)
#
#   # OR save as PNG files (recommended for Tkinter - to embed with ImageTk):
#   show_all_charts(df, save_dir="charts/")
#
# INDIVIDUAL CHART FUNCTIONS (call separately if needed by the GUI):
#   plot_bar_calories_by_activity(df)   - Figure 1 in the paper (Bar Graph)
#   plot_line_monthly_calories(df)      - Figure 2 in the paper (Line Graph)
#   plot_pie_activity_distribution(df)  - Figure 3 in the paper (Pie Chart)
#   plot_histogram_sleep(df)            - Figure 4 in the paper (Histogram)
#   plot_scatter_steps_vs_calories(df)  - Figure 5 / 4 alt (Scatter Plot)
#
# OVERLAP NOTICE:
#   This file has NO overlaps with any files from other group members.
#   The data it uses (groupby results, value counts, correlations) is
#   computed internally from the cleaned df - it does NOT import from
#   fitness_analytics_stats.py. If the integration group member wants to
#   avoid recomputing groupby results, they can refactor the chart functions
#   to accept pre-computed DataFrames as optional parameters.
#   For now, each chart is self-contained.
#
# EXPECTED COLUMNS (output of cleaning.py):
#   participant_id, date (datetime), gender, activity_type,
#   duration_minutes, calories_burned, daily_steps,
#   avg_heart_rate, sleep_hours
# =============================================================================


# Import necessary libraries
import os
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# =======================================================
# SHARED STYLE
# Applied globally so all charts have a consistent look.
# =======================================================

# 7 colors - one per activity type (Walking, Running, Cycling, Swimming,
# Yoga, HIIT, Weight Training)
PALETTE = [
    "#4C72B0",  # blue
    "#DD8452",  # orange
    "#55A868",  # green
    "#C44E52",  # red
    "#8172B2",  # purple
    "#937860",  # brown
    "#DA8BC3",  # pink
]

plt.rcParams.update({
    "figure.facecolor": "#F7F9FC",
    "axes.facecolor":   "#FFFFFF",
    "axes.grid":        True,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelsize":   11,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
})


def _finish(fig, save_path):
    """
    Internal helper: tighten layout, then either save to file or show
    interactively. Always closes the figure afterward to free memory.
    Not intended to be called directly from outside this file.
    """
    fig.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved -> {save_path}")
    else:
        plt.show()
    plt.close(fig)


# =============================================================================
# CHART 1 - Bar Graph: Average Calories Burned per Activity Type
#
# Paper reference: Figure 1
# Requirement met: at least 1 Bar Graph
#
# What it shows: average calories burned for each of the 7 activity types,
# sorted highest to lowest, so the most energy-intensive activities are
# immediately visible.
#
# Data used: groupby("activity_type")["calories_burned"].mean()
# [NO OVERLAP] No group member file produces this chart.
# The underlying groupby result is the same as 'by_activity' in
# fitness_analytics_filter_sort_group.py (Group B) and 'activity_summary'
# in fitness_analytics_stats.py, but those produce tables, not charts.
# =============================================================================

def plot_bar_calories_by_activity(df, save_path=None):
    """
    Horizontal bar chart: average calories burned per activity type,
    sorted from highest (top) to lowest (bottom).
    """
    data = (
        df.groupby("activity_type")["calories_burned"]
        .mean()
        .sort_values()   # ascending so the longest bar sits at the top
        .dropna()
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.barh(
        data.index,
        data.values,
        color=PALETTE[: len(data)],
        edgecolor="white",
        height=0.6,
    )

    # Value label at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 4,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.0f} kcal",
            va="center", ha="left", fontsize=9, fontweight="bold",
        )

    ax.set_title("Average Calories Burned per Activity Type")
    ax.set_xlabel("Average Calories Burned (kcal)")
    ax.set_ylabel("Activity Type")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    # Extra right margin so value labels are not clipped
    ax.set_xlim(right=data.max() * 1.15)

    _finish(fig, save_path)


# =============================================================================
# CHART 2 - Line Graph: Monthly Average Calories Burned
#
# Paper reference: Figure 2
# Requirement met: at least 1 Line Graph
#
# What it shows: how average calories burned per session changed month by
# month across Jan-Dec 2026, revealing seasonal or behavioral trends.
#
# Data used: groupby("month")["calories_burned"].mean()
# [NO OVERLAP] No group member file produces this chart.
# The underlying monthly aggregation matches 'monthly_trend' in
# fitness_analytics_totals_trends_corr.py and in fitness_analytics_stats.py,
# but those produce tables, not charts.
# =============================================================================

def plot_line_monthly_calories(df, save_path=None):
    """
    Line chart: average calories burned per session for each month
    (January to December 2026), with annotated data points.
    """
    df_m = df.copy()
    df_m["month"] = df_m["date"].dt.to_period("M").astype(str)

    monthly = (
        df_m.groupby("month")["calories_burned"]
        .mean()
        .sort_index()
    )

    # Convert "2026-01" -> "Jan", "2026-02" -> "Feb", etc.
    labels = [
        calendar.month_abbr[int(m.split("-")[1])]
        for m in monthly.index
    ]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        labels,
        monthly.values,
        marker="o",
        linewidth=2.4,
        color=PALETTE[1],
        markersize=8,
        markerfacecolor="white",
        markeredgewidth=2.2,
        zorder=3,
    )

    # Light fill under the line for readability
    ax.fill_between(labels, monthly.values, alpha=0.12, color=PALETTE[1])

    # Annotate each data point with its value
    for x, val in enumerate(monthly.values):
        ax.annotate(
            f"{val:.0f} kcal",
            xy=(x, val),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color="#333333",
        )

    ax.set_title("Monthly Average Calories Burned (Jan - Dec 2026)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Calories Burned (kcal)")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    # Headroom so top annotations are not clipped
    ax.set_ylim(monthly.min() * 0.88, monthly.max() * 1.14)

    _finish(fig, save_path)


# =============================================================================
# CHART 3 - Pie Chart: Activity Type Distribution
#
# Paper reference: Figure 3
# Requirement met: at least 1 Pie Chart
#
# What it shows: each activity type's share of the total recorded sessions,
# so you can immediately see which activities participants logged most.
#
# Data used: value_counts() on "activity_type"
# [NO OVERLAP] No group member file produces this chart.
# The underlying counts match 'activity_frequency' in
# fitness_analytics_stats.py and pct_of_all_sessions in
# fitness_analytics_filter_sort_group.py, but those are tables, not charts.
# =============================================================================

def plot_pie_activity_distribution(df, save_path=None):
    """
    Pie chart: proportion of all sessions accounted for by each
    of the seven activity types.
    """
    counts = df["activity_type"].value_counts().dropna()

    fig, ax = plt.subplots(figsize=(7, 7))

    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[: len(counts)],
        startangle=140,
        pctdistance=0.80,
        wedgeprops={"edgecolor": "white", "linewidth": 1.8},
    )

    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")

    ax.set_title("Distribution of Activity Types\n(Share of Total Sessions)")

    _finish(fig, save_path)


# =============================================================================
# CHART 4 - Histogram: Sleep Hours Distribution
#
# Paper reference: Figure 4
# Requirement met: at least 1 Histogram or Scatter Plot
#
# What it shows: how sleep hours are distributed across all sessions.
# A vertical mean line and a shaded healthy-sleep zone (7-9 hrs) give
# the viewer an instant benchmark to compare against.
#
# Data used: df["sleep_hours"] directly (no groupby needed)
# [NO OVERLAP] No group member file produces this chart.
# =============================================================================

def plot_histogram_sleep(df, save_path=None):
    """
    Histogram: distribution of sleep hours per session, with a mean
    reference line and a shaded 7-9 hour healthy-sleep zone.
    """
    sleep_data = df["sleep_hours"].dropna()
    mean_val   = sleep_data.mean()

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(
        sleep_data,
        bins=14,
        color=PALETTE[2],
        edgecolor="white",
        linewidth=0.8,
        zorder=2,
    )

    # Shaded healthy-sleep zone (7-9 hrs, per the paper's recommendation)
    ax.axvspan(
        7, 9,
        alpha=0.12,
        color=PALETTE[2],
        label="Healthy range (7-9 hrs)",
    )

    # Vertical mean line
    ax.axvline(
        mean_val,
        color=PALETTE[3],
        linewidth=2,
        linestyle="--",
        label=f"Mean: {mean_val:.2f} hrs",
        zorder=3,
    )

    ax.set_title("Distribution of Sleep Hours per Session")
    ax.set_xlabel("Sleep Hours")
    ax.set_ylabel("Number of Sessions")
    ax.legend(fontsize=9)

    _finish(fig, save_path)


# =============================================================================
# CHART 5 / 4 alt - Scatter Plot: Daily Steps vs. Calories Burned
#
# Paper reference: Figure 4 (alternative - satisfies the same requirement)
# Requirement met: at least 1 Histogram or Scatter Plot
#
# What it shows: the relationship between daily steps and calories burned,
# with each point colour-coded by activity type and an overall trend line.
# Supports Finding 1 in the paper (steps vs. calories correlation).
#
# Data used: df["daily_steps"] and df["calories_burned"] with activity colour
# [NO OVERLAP] No group member file produces this chart.
# =============================================================================

def plot_scatter_steps_vs_calories(df, save_path=None):
    """
    Scatter plot: daily steps (x) vs. calories burned (y), colour-coded
    by activity type, with a linear trend line across all points.
    """
    plot_df    = df.dropna(subset=["daily_steps", "calories_burned"]).copy()
    activities = sorted(plot_df["activity_type"].unique())
    color_map  = {
        act: PALETTE[i % len(PALETTE)]
        for i, act in enumerate(activities)
    }

    fig, ax = plt.subplots(figsize=(9, 6))

    for act in activities:
        subset = plot_df[plot_df["activity_type"] == act]
        ax.scatter(
            subset["daily_steps"],
            subset["calories_burned"],
            label=act,
            color=color_map[act],
            alpha=0.60,
            edgecolors="white",
            linewidths=0.4,
            s=50,
            zorder=2,
        )

    # Linear trend line fitted across all activity types combined
    x = plot_df["daily_steps"].values
    y = plot_df["calories_burned"].values
    m, b    = np.polyfit(x, y, 1)
    trend_x = np.linspace(x.min(), x.max(), 300)
    ax.plot(
        trend_x, m * trend_x + b,
        color="black",
        linewidth=1.8,
        linestyle="--",
        label="Overall trend",
        zorder=3,
    )

    ax.set_title("Daily Steps vs. Calories Burned (by Activity Type)")
    ax.set_xlabel("Daily Steps")
    ax.set_ylabel("Calories Burned (kcal)")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9)

    _finish(fig, save_path)


# =======================================================
# CONVENIENCE WRAPPER - generate all five charts at once
# =======================================================

def show_all_charts(df, save_dir=None):
    """
    Run all five chart functions in sequence.

    Parameters
    ----------
    df       : Cleaned DataFrame. The 'date' column must already be
               converted to datetime before calling this.
    save_dir : Optional output folder path (str). If provided, each chart
               is saved as a PNG file instead of being displayed
               interactively. Create the folder first if it does not exist,
               or let this function create it automatically.

               Recommended for Tkinter: save to a folder, then load the
               PNG files with PIL.ImageTk to embed them in the GUI.

               Example:
                   show_all_charts(df, save_dir="charts/")

               Files saved:
                   charts/bar_calories_by_activity.png
                   charts/line_monthly_calories.png
                   charts/pie_activity_distribution.png
                   charts/histogram_sleep_hours.png
                   charts/scatter_steps_vs_calories.png
    """
    def path(filename):
        # Returns full save path if save_dir is set, otherwise None
        # (None causes _finish to call plt.show() instead of saving)
        return os.path.join(save_dir, filename) if save_dir else None

    print("\n[PyPulse] Generating charts...")
    plot_bar_calories_by_activity  (df, path("bar_calories_by_activity.png"))
    plot_line_monthly_calories     (df, path("line_monthly_calories.png"))
    plot_pie_activity_distribution (df, path("pie_activity_distribution.png"))
    plot_histogram_sleep           (df, path("histogram_sleep_hours.png"))
    plot_scatter_steps_vs_calories (df, path("scatter_steps_vs_calories.png"))
    print("[PyPulse] All charts done.\n")


# ===========================================================
# LOCAL TEST - remove or comment out before final submission
# ===========================================================

if __name__ == "__main__":
    df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])

    # Show charts interactively (one window at a time; close each to advance):
    show_all_charts(df)

    # To save as PNG files instead:
    # show_all_charts(df, save_dir="charts/")