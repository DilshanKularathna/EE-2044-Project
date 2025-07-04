# # train_model.py
# import pandas as pd
# from sklearn.ensemble import IsolationForest
# from joblib import dump

# def load_data(csv_path: str):
#     df = pd.read_csv(csv_path, parse_dates=['timestamp'])
#     return df[['pH', 'water_level', 'temperature', 'light']]

# def train_and_save(csv_path: str, model_path: str = "model.joblib"):
#     data = load_data(csv_path)
#     model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
#     model.fit(data)
#     dump(model, model_path)
#     print(f"Model saved to {model_path}")

# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-d", "--data", required=True, help="Path to CSV file")
#     parser.add_argument("-o", "--out", default="model.joblib", help="Model output path")
#     args = parser.parse_args()
#     train_and_save(args.data, args.out)


# train_model.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import dump

def load_data(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    return df[['pH', 'water_level', 'temperature', 'light']]

def train_and_save(csv_path: str, model_path: str = "model.joblib"):
    data = load_data(csv_path)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(data)
    dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", required=True, help="Path to CSV file")
    parser.add_argument("-o", "--out", default="model.joblib", help="Model output path")
    args = parser.parse_args()
    train_and_save(args.data, args.out)
