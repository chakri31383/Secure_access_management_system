# # detection.py
# import os
# import pickle
# import random
# import datetime
# import json
# from typing import List, Optional, Dict, Any
#
# from sklearn.ensemble import IsolationForest
#
# # Configuration
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "anomaly_model.pkl")
# STORE_PATH = os.path.join(os.path.dirname(__file__), "activity_store.json")
# DEFAULT_MODEL_CONTAMINATION = 0.05  # tune for your environment
#
#
# # ---------- Model functions ----------
# def train_anomaly_model(activities: List[List[float]],
#                         model_path: str = MODEL_PATH,
#                         contamination: float = DEFAULT_MODEL_CONTAMINATION,
#                         random_state: int = 42):
#     """
#     Train an IsolationForest model on `activities`.
#     Each item in activities should be a numeric feature-vector (list/tuple).
#     Returns the trained model and writes it to disk.
#     """
#     if not activities or len(activities) < 5:
#         # Not enough data to train
#         return None
#
#     clf = IsolationForest(contamination=contamination, random_state=random_state)
#     clf.fit(activities)
#
#     # save
#     with open(model_path, "wb") as f:
#         pickle.dump(clf, f)
#
#     return clf
#
#
# def load_anomaly_model(model_path: str = MODEL_PATH):
#     """Load and return the trained model or None if not present."""
#     if not os.path.exists(model_path):
#         return None
#     with open(model_path, "rb") as f:
#         return pickle.load(f)
#
#
# def predict_anomaly(features: List[float], model_path: str = MODEL_PATH) -> bool:
#     """
#     Return True if features are anomalous according to saved model.
#     features must be a 1D list-like of numeric values.
#     """
#     clf = load_anomaly_model(model_path)
#     if clf is None:
#         # No model yet -> treat as non-anomalous by default
#         return False
#     pred = clf.predict([features])
#     # sklearn IsolationForest returns -1 for outliers, 1 for normal
#     return int(pred[0]) == -1
#
#
# # ---------- Simple persistent activity store ----------
# # Keeps per-user counters and last-updated timestamp.
# # Saved to JSON (STORE_PATH). It's trivial and human-readable.
#
# def _load_store(path: str = STORE_PATH) -> Dict[str, Any]:
#     if os.path.exists(path):
#         try:
#             with open(path, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception:
#             # If corrupted, reset gracefully
#             return {}
#     return {}
#
#
# def _save_store(store: Dict[str, Any], path: str = STORE_PATH):
#     tmp = path + ".tmp"
#     with open(tmp, "w", encoding="utf-8") as f:
#         json.dump(store, f, default=str, indent=2)
#     os.replace(tmp, path)
#
#
# def record_user_activity(user_id: int, downloads: int = 0, files: int = 0, failed_logins: int = 0,
#                          path: str = STORE_PATH):
#     """
#     Increment counters for a user in the persistent store.
#     """
#     store = _load_store(path)
#     key = str(user_id)
#     stats = store.get(key, {"downloads": 0, "files": 0, "failed_logins": 0, "time": None})
#     stats["downloads"] = stats.get("downloads", 0) + int(downloads)
#     stats["files"] = stats.get("files", 0) + int(files)
#     stats["failed_logins"] = stats.get("failed_logins", 0) + int(failed_logins)
#     stats["time"] = datetime.datetime.utcnow().isoformat()
#     store[key] = stats
#     _save_store(store, path)
#
#
# def get_user_activity(user_id: int, path: str = STORE_PATH) -> Dict[str, Any]:
#     store = _load_store(path)
#     return store.get(str(user_id), {"downloads": 0, "files": 0, "failed_logins": 0, "time": None})
#
#
# def get_all_activity(path: str = STORE_PATH) -> Dict[str, Any]:
#     return _load_store(path)
#
#
# # ---------- Convenience helpers for testing / UI ----------
#
# def generate_test_activity(num_users: int = 10, path: str = STORE_PATH):
#     """Generate test activity for `num_users` users and persist it."""
#     for uid in range(1, num_users + 1):
#         downloads = random.randint(1, 5)
#         files = random.randint(0, 3)
#         failed_logins = random.randint(0, 1)
#         record_user_activity(uid, downloads=downloads, files=files, failed_logins=failed_logins, path=path)
#
#
# def prepare_training_matrix(path: str = STORE_PATH) -> List[List[float]]:
#     """
#     Build a matrix of features suitable for training:
#     [downloads, files, failed_logins] per user.
#     """
#     store = _load_store(path)
#     rows = []
#     for uid, stats in store.items():
#         rows.append([
#             int(stats.get("downloads", 0)),
#             int(stats.get("files", 0)),
#             int(stats.get("failed_logins", 0))
#         ])
#     return rows
#
#
# def test_normal_behavior(model_path: str = MODEL_PATH, path: str = STORE_PATH):
#     """
#     Convenience: run a set of normal patterns through the predictor and print results.
#     """
#     normal_patterns = [
#         [2, 1, 0],
#         [3, 2, 0],
#         [1, 0, 1],
#         [4, 1, 0],
#     ]
#     print("Normal behavior tests:")
#     for i, p in enumerate(normal_patterns, 1):
#         print(f" Pattern {i}: {p} -> Anomaly? {predict_anomaly(p, model_path)}")
#
#
# def test_suspicious_behavior(model_path: str = MODEL_PATH, path: str = STORE_PATH):
#     suspicious_patterns = [
#         [50, 0, 0],
#         [20, 10, 0],
#         [5, 5, 10],
#         [0, 0, 15],
#         [30, 20, 5],
#     ]
#     print("Suspicious behavior tests:")
#     for i, p in enumerate(suspicious_patterns, 1):
#         print(f" Pattern {i}: {p} -> Anomaly? {predict_anomaly(p, model_path)}")
#
#
# # ---------- Streamlit helpers (optional) ----------
# # If you want to integrate into Streamlit monitor page, you can call these
# # functions from your streamlit code. They won't import streamlit by default
# # so this file remains pure python and importable from Django.
#
# def build_and_save_model_from_store(path: str = STORE_PATH, model_path: str = MODEL_PATH, contamination: float = DEFAULT_MODEL_CONTAMINATION):
#     rows = prepare_training_matrix(path)
#     if len(rows) < 5:
#         print("Not enough activity rows to train model.")
#         return None
#     clf = train_anomaly_model(rows, model_path=model_path, contamination=contamination)
#     print("Model trained and saved to", model_path)
#     return clf
#
#
# # ---------- CLI quick-run for dev/test ----------
# if __name__ == "__main__":
#     print("detection.py quick-start")
#     # 1) generate some test activity
#     generate_test_activity(num_users=12)
#     print("Sample activity generated.")
#     # 2) prepare and train model (if enough data)
#     rows = prepare_training_matrix()
#     print("Training matrix rows:", len(rows))
#     if len(rows) >= 5:
#         train_anomaly_model(rows)
#         print("Model trained.")
#     else:
#         print("Not enough rows to train (need >=5).")
#     # 3) run tests
#     test_normal_behavior()
#     test_suspicious_behavior()
#     # 4) show store
#     print("Activity store snapshot:", get_all_activity())
# ai_anomaly/detection.py

import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from django.conf import settings

MODEL_DIR = os.path.join(settings.BASE_DIR, "ai_anomaly")
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.pkl")


def ensure_model_dir():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)


# -----------------------------
# TRAIN MODEL
# -----------------------------
def train_anomaly_model(activity_queryset):
    """
    Train Isolation Forest using real user activity data
    activity_queryset: QuerySet of UserActivity
    """
    if activity_queryset.count() < 20:
        # Not enough data to train
        return None

    X = np.array([
        [a.downloads, a.files, a.failed_logins]
        for a in activity_queryset
    ])

    model = IsolationForest(
        n_estimators=150,
        contamination=0.05,   # assume ~5% abnormal
        random_state=42
    )

    model.fit(X)

    ensure_model_dir()
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    return model


# -----------------------------
# LOAD MODEL
# -----------------------------
def load_anomaly_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


# -----------------------------
# PREDICT
# -----------------------------
def predict_anomaly(downloads, files, failed_logins):
    """
    Returns True if anomaly detected, else False
    """
    model = load_anomaly_model()
    if model is None:
        return False  # fail-safe

    features = np.array([[downloads, files, failed_logins]])
    prediction = model.predict(features)

    # -1 => anomaly, 1 => normal
    return prediction[0] == -1
