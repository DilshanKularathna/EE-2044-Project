# anomaly_functions.py
import json
import numpy as np
from pathlib import Path

# Auto‑load params file on first call
_PARAMS = None

def _load_params(path: str = None):
    global _PARAMS
    if _PARAMS is None:
        # default: same folder as this .py
        base = Path(__file__).parent
        p = Path(path) if path else base / "anomaly_params.json"
        _PARAMS = json.loads(p.read_text())
    return _PARAMS

def detect_from_json(pH : float, water_level : float, temperature : float, light : float) -> str:
    """
    Input: JSON string {"pH":…, "water_level":…, "temperature":…, "light":…}
    Output: JSON string {"anomaly":bool, "max_z":float}
    """
    json_input = json.dumps({"pH": pH, "water_level": water_level, "temperature": temperature, "light": light})
    pm = _load_params()
    reading = json.loads(json_input)
    
    zscores = []
    for key, val in reading.items():
        if key not in pm['params']:
            continue
        m = pm['params'][key]['mean']
        s = pm['params'][key]['std']
        z = (val - m) / s if s > 0 else 0.0
        zscores.append(abs(z))
    
    max_z = max(zscores) if zscores else 0.0
    anomaly = max_z > pm.get('threshold', 3.0)
    
    return json.dumps({
        'anomaly': anomaly,
        'max_z': max_z
    })

#{"pH":7,"water_level":17.3,"temperature":30,"light":300}