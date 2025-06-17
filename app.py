from flask import Flask, request, jsonify
import pickle
import numpy as np
import joblib
import flask_cors as cors
import os

app = Flask(__name__)
cors.CORS(app)

FEATURE_ORDER = [
    "Age",
    "Height",
    "Weight",
    "Duration",
    "Heart_Rate",
    "Body_Temp",
    "Gender"
]

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "Calories_Prediction_model.pkl")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Check if model file exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found at {MODEL_PATH}. "
        f"Please place the model file in the 'model' directory."
    )

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully!")
    print(f"Model expects {model.n_features_in_} features in this order: {FEATURE_ORDER}")
except Exception as e:
    print(f"Error loading model with joblib from {MODEL_PATH}: {str(e)}")
    try:
        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file, encoding='latin1')
            print("Model loaded with pickle (latin1 encoding)")
    except Exception as e:
        print(f"Error loading with pickle (latin1) from {MODEL_PATH}: {str(e)}")
        try:
            with open(MODEL_PATH, "rb") as model_file:
                model = pickle.load(model_file)
                print("Model loaded with pickle (default)")
        except Exception as e:
            print(f"Final attempt to load model failed: {str(e)}")
            raise RuntimeError(
                f"Failed to load model from {MODEL_PATH}. "
                f"Please ensure the model file is correctly formatted and accessible."
            )

def validate_input_ranges(data):
    ranges = {
        "Age": (10, 80),
        "Height": (120, 220),
        "Weight": (40, 120),
        "Duration": (5, 180),
        "Heart_Rate": (60, 200),
        "Body_Temp": (36, 40),
        "Gender": (0, 1)
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
    return f"""
    API Kalori Siap Digunakan!
    
    Example POST request to /predict:
    
    curl -X POST {request.host_url}predict 
         -H "Content-Type: application/json" 
         -d '{{
             "Age": 25,
             "Height": 170,
             "Weight": 65,
             "Duration": 30,
             "Heart_Rate": 80,
             "Body_Temp": 37,
             "Gender": 1
         }}'
         
    Features must be provided in this order: {FEATURE_ORDER}
         
    Feature ranges:
    - Age: Adult age in years (10-80)
    - Height: Height in cm (120-220)
    - Weight: Weight in kg (40-120)
    - Duration: Exercise duration in minutes (5-180)
    - Heart_Rate: Heart rate in bpm (60-200)
    - Body_Temp: Body temperature in Celsius (36-40)
    - Gender: 1 for male, 0 for female
    """

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
        features = np.array([float(data[field]) for field in FEATURE_ORDER]).reshape(1, -1)
        prediction = model.predict(features)
        
        return jsonify({
            "predicted_calories": round(float(prediction[0]), 2),
            "input_data": {
                name: float(data[name]) for name in FEATURE_ORDER
            }
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
        }), 400

# Only use debug mode when running directly
if __name__ == "__main__":
    app.run(debug=False)
