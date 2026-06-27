import pandas as pd
import numpy as np

def clean_fitness_data(input_file, output_file):
    # Loads the dataset, read file into a DataFrame
    print("Loading data...")
    df = pd.read_csv(input_file)
    
    # Store original shape for the report. .shape to return tuple
    original_shape = df.shape

    # Remove Duplicate Rows (i.e, deduplication)
    df = df.drop_duplicates()

    # Fix Date Formats (handling mixed formats)
    print("Cleaning dates...")
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='mixed') # Convert strings to date objects, If there's invalids turn to NaN, indicate inconsistent date formats
    # Drop rows where date is missing after conversion
    df = df.dropna(subset=['date'])

    # Standardize Gender
    # Map all variations to 'Male' or 'Female'
    print("Standardizing gender...")
    # Dictionary
    gender_map = {
        'M': 'Male', 'MALE': 'Male', 'male': 'Male', 'Male': 'Male',
        'F': 'Female', 'FEMALE': 'Female', 'female': 'Female', 'Female': 'Female'
    }
    df['gender'] = df['gender'].str.strip().map(gender_map) # Replace values in the gender column based on the dict

    # Standardize Activity Type
    print("Standardizing activity types...")
    df['activity_type'] = df['activity_type'].str.strip().str.title() # Basic string manipulation
    # Fix the specific typo 'Runing' to 'Running'
    df['activity_type'] = df['activity_type'].replace('Runing', 'Running')

    # Handle Numerical Outliers
    print("Handling outliers...")
    # Duration: 450 is impossible. Replace with median.
    dur_median = df.loc[df['duration_minutes'] != 450, 'duration_minutes'].median() # Get median of those who ain't 450
    df.loc[df['duration_minutes'] == 450, 'duration_minutes'] = dur_median # Overwrite those who are 450 with the median

    # Negative steps is impossible. Replace with NaN then fill.
    df.loc[df['daily_steps'] < 0, 'daily_steps'] = np.nan
    df['daily_steps'] = df['daily_steps'].fillna(df['daily_steps'].median())

    # Heart Rate: 300 is impossible. Replace with NaN then fill.
    df.loc[df['avg_heart_rate'] > 250, 'avg_heart_rate'] = np.nan
    df['avg_heart_rate'] = df['avg_heart_rate'].fillna(df['avg_heart_rate'].median())

    # Handle Missing Values (NaNs and Blank Spaces)
    print("Filling missing values...")
    # Replace empty strings or spaces with NaN
    df = df.replace(r'^\s*$', np.nan, regex=True)
    
    # Fill remaining numeric NaNs with the median of their respective columns
    numeric_cols = ['calories_burned', 'duration_minutes', 'daily_steps', 'avg_heart_rate', 'sleep_hours']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce') # Ensure they are numbers
        df[col] = df[col].fillna(df[col].median())

    # Save the cleaned dataset
    df.to_csv(output_file, index=False)
    
    print("-" * 30)
    print(f"Cleaning Complete!")
    print(f"Original rows: {original_shape[0]}")
    print(f"Cleaned rows: {df.shape[0]}")
    print(f"Cleaned file saved as: {output_file}")
    print("-" * 30)

if __name__ == "__main__":
    clean_fitness_data('Group4_FitnessAnalytics_raw.csv', 'Group4_FitnessAnalytics_cleaned.csv')