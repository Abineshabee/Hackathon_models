import pandas as pd
import numpy as np

# Function to calculate flags based on the conditions
def calculate_flags(row):
    delta_t = row['ActualReadingTime'] - row['EstimatedReadingTime']
    z_speed = (row['ScrollSpeed'] - row['MeanScrollSpeed']) / row['StdScrollSpeed']

    red_flag = False
    black_flag = False

    # Time-based Flags
    if delta_t > (row['MeanReadingTime'] + 1.5 * row['StdReadingTime']):
        red_flag = True  # Takes too long - confusion
    elif delta_t < (row['MeanReadingTime'] - 1.5 * row['StdReadingTime']):
        black_flag = True  # Too fast - skimming

    # Scroll Speed Flags
    if z_speed < -1.5:
        red_flag = True  # Scrolling too slow - struggling
    elif z_speed > 1.5:
        black_flag = True  # Scrolling too fast - skimming

    # Scroll Depth Flags
    if row['ScrollDepth'] < 50 and row['BookComplexity'] > 0.8:
        black_flag = True  # Incomplete reading of a complex book

    # Backtracking Rate Flags
    if row['BacktrackingRate'] > (row['MeanBacktrackingRate'] + 1.5 * row['StdBacktrackingRate']):
        red_flag = True  # Frequent re-reading - confusion

    # Page Jump Rate Flags
    if row['PageJumpRate'] > (row['MeanPageJumpRate'] + 1.5 * row['StdPageJumpRate']):
        black_flag = True  # Excessive jumping - distraction

    # Exit Frequency Flags
    if row['ExitFrequency'] > (row['MeanExitFrequency'] + 1.5 * row['StdExitFrequency']):
        red_flag = True  # Frequent exits - frustration

    # Assign flag based on detected conditions
    if red_flag and black_flag:
        return np.random.choice([1, 2])  # Randomly assign red or black if both occur
    elif red_flag:
        return 1  # Red Flag
    elif black_flag:
        return 2  # Black Flag
    return 0  # No Flag

# Generate dataset
np.random.seed(42)
num_rows = 30000

data = {
    'UserID': np.random.randint(1000, 2000, num_rows),
    'BookID': np.random.randint(3000, 4000, num_rows),
    'TotalPages': np.random.randint(150, 500, num_rows),
    'BookComplexity': np.random.uniform(0.5, 1, num_rows),
    'ReadabilityScore': np.random.uniform(0.6, 0.9, num_rows),
    'EstimatedReadingTime': np.random.randint(800, 2000, num_rows),
    'ActualReadingTime': np.random.randint(500, 2500, num_rows),  # Increased variation
    'ScrollSpeed': np.random.normal(1.5, 0.7, num_rows),  # Normal distribution for more variation
    'ScrollDepth': np.random.uniform(30, 100, num_rows),
    'BacktrackingRate': np.random.normal(10, 5, num_rows),  # More natural variation
    'PageJumpRate': np.random.normal(20, 10, num_rows),
    'ExitFrequency': np.random.uniform(0, 30, num_rows),
}

# Create mean and std for dynamic flag calculation
for feature in ['ReadingTime', 'ScrollSpeed', 'BacktrackingRate', 'PageJumpRate', 'ExitFrequency']:
    data[f'Mean{feature}'] = np.mean(data[f'Estimated{feature}' if feature == 'ReadingTime' else feature])
    data[f'Std{feature}'] = np.std(data[f'Estimated{feature}' if feature == 'ReadingTime' else feature])

# Create DataFrame
df = pd.DataFrame(data)

# Calculate Flags
df['Flag'] = df.apply(calculate_flags, axis=1)

# Drop mean and std columns before saving
cols_to_drop = [col for col in df.columns if col.startswith(('Mean', 'Std'))]
df.drop(columns=cols_to_drop, inplace=True)

# Save to CSV
df.to_csv('book_reading_dataset.csv', index=False)

print("Dataset generated and saved as 'book_reading_dataset.csv'")

