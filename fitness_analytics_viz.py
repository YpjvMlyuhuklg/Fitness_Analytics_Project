"""Matplotlib charts for PyPulse."""

import os
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860", "#DA8BC3"]

plt.rcParams.update({
    "figure.facecolor": "#F7F9FC",
    "axes.facecolor": "#FFFFFF",
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--",
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})


def _finish(fig, save_path):
    fig.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved -> {save_path}")
    else:
        plt.show()
    plt.close(fig)


def plot_bar_calories_by_activity(df, save_path=None):
    data = (
        df.groupby("activity_type")["calories_burned"]
        .mean()
        .sort_values()
        .dropna()
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(data.index, data.values, color=PALETTE[: len(data)], edgecolor="white", height=0.6)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 4, bar.get_y() + bar.get_height() / 2, f"{width:.0f} kcal",
                va="center", ha="left", fontsize=9, fontweight="bold")

    ax.set_title("Average Calories per Session by Activity Type")
    ax.set_xlabel("Average Calories Burned (kcal)")
    ax.set_ylabel("Activity Type")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlim(right=data.max() * 1.15)
    _finish(fig, save_path)


def plot_line_monthly_calories(df, save_path=None):
    df_m = df.copy()
    df_m["month"] = df_m["date"].dt.to_period("M").astype(str)
    monthly = df_m.groupby("month")["calories_burned"].mean().sort_index()
    labels = [calendar.month_abbr[int(m.split("-")[1])] for m in monthly.index]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(labels, monthly.values, marker="o", linewidth=2.4, color=PALETTE[1],
            markersize=8, markerfacecolor="white", markeredgewidth=2.2, zorder=3)
    ax.fill_between(labels, monthly.values, alpha=0.12, color=PALETTE[1])

    for x, val in enumerate(monthly.values):
        ax.annotate(f"{val:.0f} kcal", xy=(x, val), xytext=(0, 12),
                    textcoords="offset points", ha="center", fontsize=8, color="#333333")

    ax.set_title("Monthly Average Calories Burned")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Calories Burned (kcal)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(monthly.min() * 0.88, monthly.max() * 1.14)
    _finish(fig, save_path)


def plot_pie_activity_distribution(df, save_path=None):
    counts = df["activity_type"].value_counts().dropna()
    fig, ax = plt.subplots(figsize=(7, 7))
    _, _, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%",
        colors=PALETTE[: len(counts)], startangle=140, pctdistance=0.80,
        wedgeprops={"edgecolor": "white", "linewidth": 1.8},
    )
    for label in autotexts:
        label.set_fontsize(9)
        label.set_fontweight("bold")
    ax.set_title("Distribution of Activity Types\n(Share of Total Sessions)")
    _finish(fig, save_path)


def plot_histogram_sleep(df, save_path=None):
    sleep_data = df["sleep_hours"].dropna()
    mean_val = sleep_data.mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(sleep_data, bins=14, color=PALETTE[2], edgecolor="white", linewidth=0.8, zorder=2)
    ax.axvspan(7, 9, alpha=0.12, color=PALETTE[2], label="Healthy range (7-9 hrs)")
    ax.axvline(mean_val, color=PALETTE[3], linewidth=2, linestyle="--",
               label=f"Mean: {mean_val:.2f} hrs", zorder=3)
    ax.set_title("Distribution of Sleep Hours per Session")
    ax.set_xlabel("Sleep Hours")
    ax.set_ylabel("Number of Sessions")
    ax.legend(fontsize=9)
    _finish(fig, save_path)


def plot_scatter_steps_vs_calories(df, save_path=None):
    plot_df = df.dropna(subset=["daily_steps", "calories_burned"]).copy()
    activities = sorted(plot_df["activity_type"].unique())
    color_map = {act: PALETTE[i % len(PALETTE)] for i, act in enumerate(activities)}

    fig, ax = plt.subplots(figsize=(9, 6))
    for act in activities:
        subset = plot_df[plot_df["activity_type"] == act]
        ax.scatter(subset["daily_steps"], subset["calories_burned"], label=act,
                   color=color_map[act], alpha=0.60, edgecolors="white", linewidths=0.4, s=50, zorder=2)

    x = plot_df["daily_steps"].values
    y = plot_df["calories_burned"].values
    slope, intercept = np.polyfit(x, y, 1)
    trend_x = np.linspace(x.min(), x.max(), 300)
    ax.plot(trend_x, slope * trend_x + intercept, color="black", linewidth=1.8,
            linestyle="--", label="Overall trend", zorder=3)

    ax.set_title("Daily Steps vs. Calories Burned (by Activity Type)")
    ax.set_xlabel("Daily Steps")
    ax.set_ylabel("Calories Burned (kcal)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9)
    _finish(fig, save_path)


def show_all_charts(df, save_dir=None):
    def path(filename):
        return os.path.join(save_dir, filename) if save_dir else None

    print("\n[PyPulse] Generating charts...")
    plot_bar_calories_by_activity(df, path("bar_calories_by_activity.png"))
    plot_line_monthly_calories(df, path("line_monthly_calories.png"))
    plot_pie_activity_distribution(df, path("pie_activity_distribution.png"))
    plot_histogram_sleep(df, path("histogram_sleep_hours.png"))
    plot_scatter_steps_vs_calories(df, path("scatter_steps_vs_calories.png"))
    print("[PyPulse] All charts done.\n")


if __name__ == "__main__":
    df = pd.read_csv("Group4_FitnessAnalytics_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])
    show_all_charts(df)
