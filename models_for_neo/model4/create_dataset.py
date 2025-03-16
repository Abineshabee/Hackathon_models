import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Define dataset size (larger to allow balanced sampling)
num_samples = 15000  

# Generate base features
TotalPages = np.random.randint(50, 1000, num_samples)  
BookComplexity = np.random.randint(100, 1000, num_samples)  
ReadabilityScore = np.random.uniform(1, 5, num_samples)  

# Standard Control Variable: Reading Engagement Index (REI)
ReadingEngagementIndex = (TotalPages * 0.3 + BookComplexity * 0.2 + ReadabilityScore * 10) / 100

# Estimated Reading Time (depends on REI)
EstimatedReadingTime = TotalPages * (1.2 - (ReadabilityScore / 5)) * np.random.uniform(0.8, 1.2, num_samples)

# Actual Reading Time (adjusted using REI)
ActualReadingTime = EstimatedReadingTime * (0.7 + ReadingEngagementIndex * 0.6) * np.random.uniform(0.8, 1.2, num_samples)

# Scroll Speed (depends on Readability + Complexity + REI)
ScrollSpeed = np.random.uniform(50, 150, num_samples) * (1 + ReadabilityScore / 5) * (1 - ReadingEngagementIndex / 2)

# Scroll Depth (higher for engaged users)
ScrollDepth = np.clip(100 - (ScrollSpeed / 2), 60, 100) * (1 + ReadingEngagementIndex / 2)

# Backtracking Rate (higher for more complex books, follows REI)
BacktrackingRate = np.clip(BookComplexity / 40, 5, 30) * (1 + ReadingEngagementIndex / 2)

# Page Jump Rate (inverse of Backtracking, depends on REI)
PageJumpRate = np.clip(20 - BacktrackingRate / 2, 1, 20) * (1 - ReadingEngagementIndex / 2)

# Exit Frequency (higher for skimmers, lower for engaged users, follows REI)
ExitFrequency = np.clip(PageJumpRate / 2, 0, 10) * (1 - ReadingEngagementIndex)

# Define function to assign Flag (0, 1, or 2) based on REI
def generate_flag(reading_engagement):
    """Assigns flag based on the Reading Engagement Index (REI)."""
    if reading_engagement > 2.5:
        return 0  # Engaged
    elif reading_engagement < 1.5:
        return 2  # Skimming
    else:
        return 1  # Trying to Engage

# Generate the Flag labels
Flag = np.array([generate_flag(ReadingEngagementIndex[i]) for i in range(num_samples)])

# Create DataFrame
df = pd.DataFrame({
    "TotalPages": TotalPages,
    "BookComplexity": BookComplexity,
    "ReadabilityScore": ReadabilityScore,
    "ReadingEngagementIndex": ReadingEngagementIndex,  # Standard control variable
    "EstimatedReadingTime": EstimatedReadingTime,
    "ActualReadingTime": ActualReadingTime,
    "ScrollSpeed": ScrollSpeed,
    "ScrollDepth": ScrollDepth,
    "BacktrackingRate": BacktrackingRate,
    "PageJumpRate": PageJumpRate,
    "ExitFrequency": ExitFrequency,
    "Flag": Flag  # Target variable (0=Engaged, 1=Trying to Engage, 2=Skimming)
})

# Ensure equal proportion of each class
num_per_class = min(df["Flag"].value_counts().min(), 5000)  # Limit each class to 5000
df_balanced = df.groupby("Flag", group_keys=False).apply(lambda x: x.sample(num_per_class, random_state=42)).reset_index(drop=True)

# Save to CSV
df_balanced.to_csv("balanced_reading_behavior.csv", index=False)

# Display first few rows
print(df_balanced.head())

# Check label distribution
print(df_balanced["Flag"].value_counts())  # Should show equal numbers of 0, 1, and 2

# Compute correlation matrix
correlation_matrix = df_balanced.corr()

# Display correlated features (strong correlations)
print("\nTop Correlated Feature Pairs:")
strong_correlations = correlation_matrix.unstack().reset_index()
strong_correlations.columns = ["Feature 1", "Feature 2", "Correlation"]
strong_correlations = strong_correlations[strong_correlations["Feature 1"] != strong_correlations["Feature 2"]]
strong_correlations = strong_correlations[abs(strong_correlations["Correlation"]) > 0.5]  # Strong correlations
strong_correlations = strong_correlations.sort_values(by="Correlation", ascending=False)
print(strong_correlations)

