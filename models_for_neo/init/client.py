import requests
import pandas as pd

# Flask Server URL
SERVER_URL = "http://127.0.0.1:8000/predict"

# Define expected feature names and sample values for each model
feature_data = {
    "knn": {
        "columns": ["CGPA", "GPA", "Attendance Percentage", "Assignment Due Days", "Project Due Days", "Fees Due"],
        "values": [[3.9, 3.8, 85, 1, 3, 0]]
    },
    "student_performance": {
        "columns": [
            "CGPA", "GPA", "Average Assignment Marks", "Average Project Marks",
            "Attendance Percentage", "Class Participation Credits", "Extracurricular Activities",
            "Achievements Credits", "No. of Students in Class", "Rank in Class", "Certifications Count"
        ],
        "values": [[3.7, 3.6, 80, 85, 90, 8, 7, 5, 50, 5, 2]]
    },
    "random_forest": {
        "columns": [
            "TotalPages", "BookComplexity", "ReadabilityScore", "ReadingEngagementIndex",
            "EstimatedReadingTime", "ActualReadingTime", "ScrollSpeed", "ScrollDepth",
            "BacktrackingRate", "PageJumpRate", "ExitFrequency"
        ],
        "values": [[500, 400, 3.5, 70, 1200, 1250, 80, 85, 15, 10, 3]]
    },
    "recommendation": {
        "columns": ["featureA", "featureB", "featureC"],
        "values": [[1, 2, 3]]
    }
}

def send_request(model_name, features):
    """Send a POST request to the Flask API with model name and features."""
    payload = {
        "model_name": model_name,
        "features": features
    }

    try:
        response = requests.post(SERVER_URL, json=payload)
        result = response.json()
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Model: {result['model']}")
            print(f"Prediction: {result['prediction']}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test all models
    for model_name, data in feature_data.items():
        df = pd.DataFrame(data["values"], columns=data["columns"])
        features = df.values.tolist()[0]  # Convert DataFrame row to list
        print(f"\nSending request to {model_name} model...")
        send_request(model_name, features)

