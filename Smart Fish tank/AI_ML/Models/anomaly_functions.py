# # anomaly_functions.py
# import json
# import numpy as np
# from joblib import load
# from pathlib import Path

# _MODEL = None
# _MODEL_PATH = Path(__file__).with_name("model.joblib")

# def load_model(model_path: str = None):
#     global _MODEL
#     if model_path:
#         _MODEL = load(model_path)
#     else:
#         _MODEL = load(_MODEL_PATH)

# def detect_anomaly(data: dict) -> dict:
#     if _MODEL is None:
#         raise RuntimeError("Model not loaded. Call load_model() first.")
    
#     X = np.array([[data["pH"], data["water_level"], data["temperature"], data["light"]]])
#     score = _MODEL.decision_function(X)[0]
#     label = _MODEL.predict(X)[0]  # +1 = normal, -1 = anomaly
#     return {
#         "anomaly": label == -1,
#         "score": float(score)
#     }

# def detect_from_json(json_input: str) -> str:
#     global _MODEL
#     if _MODEL is None:
#         load_model()
    
#     data = json.loads(json_input)
#     result = detect_anomaly(data)
#     return json.dumps(result)

# anomaly_functions.py
import json
import numpy as np
from joblib import load
from pathlib import Path

_MODEL = None
_MODEL_PATH = Path(__file__).with_name("model.joblib")

def load_model(model_path: str = None):
    global _MODEL
    if model_path:
        _MODEL = load(model_path)
    else:
        _MODEL = load(_MODEL_PATH)

def detect_anomaly(data: dict) -> dict:
    if _MODEL is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    X = np.array([[data["pH"], data["water_level"], data["temperature"], data["light"]]])
    score = _MODEL.decision_function(X)[0]
    label = _MODEL.predict(X)[0]  # +1 = normal, -1 = anomaly
    return {
        "anomaly": bool(label == -1),  # Ensure native Python bool for JSON serialization
        "score": float(score)
    }

def detect_from_json(json_input: str) -> str:
    global _MODEL
    if _MODEL is None:
        load_model()
    
    data = json.loads(json_input)
    result = detect_anomaly(data)
    return json.dumps(result)

#{"pH":7,"water_level":12.3,"temperature":30,"light":300}