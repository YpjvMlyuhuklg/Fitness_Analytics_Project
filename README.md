# PyPulse: A Python-Driven Analytics System for Health and Fitness Tracking

**PyPulse** is an interactive desktop data analytics application designed to clean, process, analyze, visualize, and interpret fitness tracker data. Built entirely in Python, the application demonstrates a complete data analytics workflow, from raw data ingestion and preprocessing to statistical analysis, interactive visualizations, and dynamic data-driven insights that automatically adapt to the analyzed dataset. The system is packaged within a modern Tkinter graphical user interface (GUI), providing users with an intuitive platform for exploring health and fitness data.

Developed for **CCIS INTE 202 – Integrative Programming and Technologies** at the **Polytechnic University of the Philippines**.

---

# 🚀 Key Features

## 1. Data Preprocessing & Cleaning

- Automatic detection and removal of duplicate records.
- Mixed-format date normalization into the **YYYY-MM-DD** format.
- Processing of workout records covering **January to December 2025**.
- Detection and correction of missing values and invalid numerical entries.
- Standardization of categorical values, including inconsistent gender labels and activity names (e.g., **"Runing" → "Running"**).
- Correction of unrealistic values such as invalid workout durations, negative step counts, and implausible heart rates.
- Automatic generation of a cleaned CSV dataset that serves as the foundation for all analyses, visualizations, and reports.

---

## 2. Statistical Analytics

- **Descriptive Statistics** including Mean, Median, Mode, Standard Deviation, Minimum, and Maximum.
- **Correlation Analysis** using Pearson's correlation coefficient to identify relationships among key fitness variables.
- **Health Benchmarks** showing participant performance against recommended daily step and sleep goals.
- **Grouped Analysis** summarizing workout statistics by activity type and gender.
- **Dynamic Data-Driven Insights** that automatically interpret computed results instead of relying on predefined or hard-coded text.

---

## 3. Interactive Data Visualizations

- **Bar Graph** – Average calories burned by activity type.
- **Line Graph** – Monthly average calories burned throughout the year.
- **Pie Chart** – Distribution of workout sessions by activity type.
- **Histogram** – Distribution of sleep hours with the recommended healthy sleep range highlighted.
- **Scatter Plot** – Relationship between daily steps and calories burned with a regression trend line.

Each visualization is accompanied by automatically generated insights that adapt to the analyzed dataset, helping users interpret patterns and trends without requiring manual analysis.

---

## 4. Interactive Dashboard

### 📊 Data Center

- Load the raw fitness dataset.
- Execute the **Run Clean & Deduplication** process.
- Compare original and cleaned datasets.
- Browse records through a searchable and sortable data table.

### 📈 Analytics Dashboard

- View descriptive statistics.
- Explore correlation analysis.
- Monitor health benchmark indicators.
- Review grouped statistical summaries.

### 📉 Visualization Hub

- Display interactive charts directly within the application.
- Generate dynamic data-driven insights for every visualization.

### 📄 Summary & Export

- Generate a comprehensive analytical summary report.
- Copy or print generated reports.
- Export the cleaned dataset as a CSV file.
- Save generated summaries for future reference.

---

# 📂 Project Architecture

| File | Description |
|------|-------------|
| `pypulse_gui.py` | Main entry point of the Tkinter desktop application. |
| `cleaning.py` | Performs data cleaning and preprocessing operations. |
| `fitness_analytics_stats.py` | Computes descriptive statistics, grouped analyses, health benchmarks, and correlation analysis. |
| `fitness_analytics_viz.py` | Generates all visualizations and automatically creates dynamic insights based on the analyzed data. |
| `eda.py` | Performs exploratory data analysis on the raw dataset. |
| `Group4_FitnessAnalytics_raw.csv` | Original noisy fitness dataset containing **615 workout records** collected from **30 participants** between **January and December 2025**. |
| `Group4_FitnessAnalytics_cleaned.csv` | Automatically generated cleaned dataset containing **600 validated records** after running the cleaning process. |

---

# 🛠️ Installation

## Prerequisites

Ensure that **Python 3** is installed, then install the required libraries:

```bash
pip install pandas numpy matplotlib pillow
```

---

# ▶️ Running the Application

Launch the application by executing:

```bash
python pypulse_gui.py
```

After loading the raw dataset, click **Run Clean & Deduplication** to preprocess the data and generate the cleaned dataset. Once the cleaning process is completed successfully, the **Analytics Dashboard**, **Visualization Hub**, and **Summary & Export** modules become available for use.

---

# 👥 Development Team (Group 4)

- Acerden, Chelley Maxenne R.
- Atienza, Caryl Joy A.
- Democer, Sean Carlo D.
- Fernandez, Rico G.
- Gillegao, Arabella Liss R.
- Lazaro, Troy Lauren T.
- Mejorada, Ayen V.
- Ramos, Shawn Angel S.
- Tamayo, Francis John M.

**Submitted to:**  
**Assoc. Prof. Rachel A. Nayre**