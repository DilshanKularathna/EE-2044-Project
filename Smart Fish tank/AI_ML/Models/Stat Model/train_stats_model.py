# train_stats_model.py
import pandas as pd
import json
from pathlib import Path

def load_data(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    return df[['pH', 'water_level', 'temperature', 'light']]

def train_and_save(csv_path: str,
                   out_path: str = "anomaly_params.json"):
    data = load_data(csv_path)
    params = {}
    for col in data.columns:
        params[col] = {
            'mean': data[col].mean(),
            'std': data[col].std(ddof=0)  # population std
        }
    # default threshold: 3σ
    model = {
        'params': params,
        'threshold': 3.0
    }
    Path(out_path).write_text(json.dumps(model, indent=2))
    print(f"Saved parameters to {out_path}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--data", required=True, help="CSV file")
    p.add_argument("-o", "--out", default="anomaly_params.json",
                   help="Where to save the JSON params")
    args = p.parse_args()
    train_and_save(args.data, args.out)
# To run use following command in cmd:
# python train_stats_model.py --data historical_readings.csv --out anomaly_params.json
# 