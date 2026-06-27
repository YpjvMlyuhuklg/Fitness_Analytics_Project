# PyPulse: A Python-Driven Analytics System for Health and Fitness Tracking

**PyPulse** is an interactive desktop data analytics application designed to clean, process, analyze, and visualize fitness tracker logs. Built using Python, it demonstrates a complete data science workflow—from raw data ingestion to clinical insights—packaged inside an elegant, lightweight Tkinter graphical user interface (GUI) styled with a modern, slate-and-teal theme.

Developed for CCIS *INTE 202 - Integrative Programming and Technologies* at the **Polytechnic University of the Philippines**.

---

## 🚀 Key Features

1. **Data Preprocessing & Cleaning**:
   - Automatic record deduplication.
   - Mixed-format date normalization into standard datetimes.
   - String normalization for categorical attributes (Gender spelling mappings, typo corrections like 'Runing' $\rightarrow$ 'Running').
   - Outlier detection and replacement with median values (handling invalid workout durations of 450 minutes, negative daily steps, and heart rates exceeding 250 bpm).

2. **Statistical Engine**:
   - **Descriptive Statistics**: Calculations of Mean, Median, Mode, Standard Deviation, and ranges for all numeric dimensions.
   - **Correlation Matrix**: Computes Pearson correlation coefficients ($r$) mapping key relationships (e.g., Workout Duration vs. Calories Burned, Sleep Hours vs. Heart Rate).
   - **Percentage Ratios**: Measures percentages of days meeting target thresholds (high intensity days, sleep deprivation indicators).
   - **Aggregation broken down by group**: Breakdowns sorted by activity type and gender.

3. **Data Visualizations**:
   - **Bar Chart**: Average calories burned by activity type (highest to lowest).
   - **Line Chart**: Timeline of monthly average calorie burns.
   - **Pie Chart**: Proportion of all workouts represented by each activity type.
   - **Histogram**: Distribution of sleep hours with a highlighted healthy benchmark zone.
   - **Scatter Plot**: Step count vs. calorie burn regression.

4. **Interactive GUI Dashboard**:
   - **Data Center**: Load files, run pre-processing, view original-vs-cleaned statistics, and scroll the dataset in an interactive grid supporting real-time filter searches and header-click column sorting.
   - **Analytics**: Tabbed grids showing descriptives, indicator cards, and correlations.
   - **Visualization Hub**: Seamlessly switch and view charts inside the dashboard.
   - **Export Tab**: View, print, or copy the formatted clinical summary report, export cleaned data to CSV, or save summaries.

---

## 📂 Project Architecture

* `pypulse_gui.py`: Main Tkinter graphical application entry point.
* `cleaning.py`: Standalone script containing the cleaning pipeline.
* `fitness_analytics_stats.py`: Computes descriptive and grouped analytical dataframes.
* `fitness_analytics_viz.py`: Matplotlib visual generation wrapper.
* `eda.py`: Initial raw CSV Exploratory Data Analysis.
* `Group4_FitnessAnalytics_raw.csv`: Raw, noisy fitness dataset (615 rows).
* `Group4_FitnessAnalytics_cleaned.csv`: Standardized, cleaned dataset output (599 rows).

---

## 🛠️ Installation & Execution

### 1. Prerequisites
Ensure you have Python 3 installed. Install the required external Python libraries:
```bash
pip install pandas numpy matplotlib pillow
```

### 2. Launch the Application
Run the GUI dashboard by executing:
```bash
python pypulse_gui.py
```

---

## 👥 Development Team (Group 4)
* Acerden, Chelley Maxenne R.
* Atienza, Caryl Joy A.
* Democer, Sean Carlo D.
* Fernandez, Rico G.
* Gillegao, Arabella Liss R.
* Lazaro, Troy Lauren T.
* Mejorada, Ayen V.
* Ramos, Shawn Angel S.
* Tamayo, Francis John M.

**Submitted to:** Assoc. Prof. Rachel A. Nayre