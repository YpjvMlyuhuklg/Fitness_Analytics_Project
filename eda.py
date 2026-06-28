import pandas as pd
import numpy as np

df = pd.read_csv('Group4_FitnessAnalytics_raw.csv')

print(df.info()) 
print("\nFirst 5 rows:\n", df.head())

print()
print("\nShow Duplicates:\n")
duplicates = df[df.duplicated(keep=False)]

if not duplicates.empty:
    print(f"Found {len(duplicates)} duplicate entries.")
    print("\nIdentical records (sorted for comparison):")
    print(duplicates.sort_values(by=["participant_id", "date"]))
else:
    print("No duplicate records found.")

print()
print("\nFind how many NaN:")
print(df.isna().sum())

print()
categorical_cols = ['gender', 'activity_type']
for col in categorical_cols:
    print(f"Unique values in {col}:")
    print(df[col].unique())
    print("-" * 20)

print()
print(df.describe())

print()
print("Date column (target format after cleaning: YYYY-MM-DD):")
print(df['date'].head(20))

