import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# Load Models using joblib
knn_model = joblib.load("knn_model.pkl")
scaler = joblib.load("scaler.pkl")
student_performance_model = joblib.load("student_performance_model.pkl")
random_forest_model = joblib.load("random_forest_model.pkl")
recommendation_model = joblib.load("recommendation_model.pkl")

# Model mapping
models = {
    "knn": knn_model,
    "student_performance": student_performance_model,
    "random_forest": random_forest_model,
    "recommendation": recommendation_model,
}


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get JSON request
        data = request.get_json()

        # Extract parameters
        model_name = data.get("model_name")
        features = data.get("features")

        # Ensure features is a list
        if not isinstance(features, list):
            return jsonify({"error": "Features must be a list"}), 400

        # Validate model name
        if model_name not in models:
            return jsonify({"error": "Invalid model name"}), 400

        # Convert features to DataFrame
        X = pd.DataFrame([features])

        # Apply Scaling if using KNN
        if model_name == "knn":
            X = scaler.transform(X)

        # Make Prediction
        model = models[model_name]
        prediction = model.predict(X)

        return jsonify({"model": model_name, "prediction": prediction.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

