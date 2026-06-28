import pandas as pd
import numpy as np

# Load raw
df = pd.read_csv('Group4_FitnessAnalytics_raw.csv')

print(df.info()) 
# Show data types to identify inconsistent column i,e if a column that should just be int is not just int
print("\nFirst 5 rows:\n", df.head())

print("\nFind how many NaN:")
print(df.isna().sum())
# How many NaNs are in each column to identify where to do fillna()

print()
# Check unique values to see if there's any typos
categorical_cols = ['gender', 'activity_type']
for col in categorical_cols:
    print(f"Unique values in {col}:")
    print(df[col].unique())
    print("-" * 20)

print()
print(df.describe())
# Find min max and mean using .describe() to find outliers, columns that shouldn't have nagtive values

print()
print("Date column (target format after cleaning: YYYY-MM-DD):")
print(df['date'].head(20))
# Mixed raw inputs may use DD/MM/YYYY, MM/DD/YYYY, or month-name text.