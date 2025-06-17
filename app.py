from flask import Flask, request, jsonify
import pickle
import numpy as np
import joblib
import flask_cors as cors
import os

app = Flask(__name__)
cors.CORS(app)

FEATURE_ORDER = [
    "Gender",
    "Age",
    "Height",
    "Weight",
    "Duration",
    "Heart_Rate",
    "Body_Temp"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "Calories_Prediction_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# Load model
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

# Load scaler
try:
    scaler = joblib.load(SCALER_PATH)
    print("Scaler loaded successfully!")
except Exception as e:
    raise RuntimeError(f"Failed to load scaler: {str(e)}")

def validate_input_ranges(data):
    ranges = {
        "Gender": (0, 1),
        "Age": (10, 80),
        "Height": (120, 220),
        "Weight": (40, 120),
        "Duration": (5, 180),
        "Heart_Rate": (60, 200),
        "Body_Temp": (36, 40)
    }
    errors = []
    for field, (min_val, max_val) in ranges.items():
        try:
            value = float(data[field])
            if not min_val <= value <= max_val:
                errors.append(f"{field} must be between {min_val} and {max_val}")
        except (KeyError, ValueError):
            continue
    return errors

@app.route("/")
def home():
    return f"API Kalori siap digunakan!"

@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json",
            "example_request": {name: 0 for name in FEATURE_ORDER}
        }), 415

    data = request.get_json()
    missing_fields = [field for field in FEATURE_ORDER if field not in data]
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}",
            "required_fields": FEATURE_ORDER
        }), 400

    range_errors = validate_input_ranges(data)
    if range_errors:
        return jsonify({
            "error": "Input validation failed",
            "details": range_errors
        }), 400

    try:
        raw_features = np.array([float(data[field]) for field in FEATURE_ORDER]).reshape(1, -1)

        gender = raw_features[:, [0]]
        features_to_scale = raw_features[:, 1:]

        scaled_features = scaler.transform(features_to_scale)

        # Gabungkan kembali
        final_input = np.hstack((gender, scaled_features))

        # Prediksi
        prediction = model.predict(final_input)
        return jsonify({
            "predicted_calories": round(float(prediction[0]), 5),
            "raw_prediction": prediction[0]
        })
    except ValueError as e:
        return jsonify({
            "error": "Invalid data type. All fields must be numbers.",
            "detail": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "detail": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=False)