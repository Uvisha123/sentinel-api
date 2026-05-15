import numpy as np
import pandas as pd
import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

FEATURE_COLUMNS = [
    "requests_per_min",
    "endpoint_variety",
    "error_rate",
    "avg_time_between_reqs",
    "single_endpoint_ratio",
    "user_agent_variety",
]

# Risk tier thresholds
HIGH_RISK_THRESHOLD = 0.7    # >= 0.7 → BLOCK
MEDIUM_RISK_THRESHOLD = 0.3  # >= 0.3 → MONITOR, < 0.3 → SAFE


# MODEL LOADING — Load once, cache forever
# Module-level cache: models are stored here after first load
_model_cache = {}


def _load_model(filename: str):
    if filename not in _model_cache:
        filepath = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Model file not found: {filepath}\n"
                f"Run 'python -m ml.train' first to train and save models."
            )
        _model_cache[filename] = joblib.load(filepath)
    return _model_cache[filename]


def load_all_models() -> dict:
    models = {
        "isolation_forest": _load_model("isolation_forest.pkl"),
        "kmeans": _load_model("kmeans.pkl"),
        "logistic_regression": _load_model("logistic_regression.pkl"),
        "scaler": _load_model("scaler.pkl"),
        "cluster_map": _load_model("cluster_map.pkl"),
    }
    print(f"   All {len(models)} models loaded into cache.")
    return models


def clear_cache():
    _model_cache.clear()
    print("   Model cache cleared.")



# CORE PREDICTION FUNCTIONS

def predict_ip(features: dict) -> dict:
    # Validate input — make sure all 6 features are present
    missing = [col for col in FEATURE_COLUMNS if col not in features]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    # Convert to numpy array in the correct order
    feature_values = np.array([[features[col] for col in FEATURE_COLUMNS]])

    # Load models (from cache if already loaded)
    scaler = _load_model("scaler.pkl")
    iso_forest = _load_model("isolation_forest.pkl")
    kmeans = _load_model("kmeans.pkl")
    log_reg = _load_model("logistic_regression.pkl")
    cluster_map = _load_model("cluster_map.pkl")


    # STEP 1: Scale features using the TRAINING scaler
    # NEVER fit a new scaler — always use the one from training
    X_scaled = scaler.transform(feature_values)

    # STEP 2: Isolation Forest — anomaly detection
    # predict: 1 = normal, -1 = anomaly
    iso_prediction = iso_forest.predict(X_scaled)[0]
    is_anomaly = bool(iso_prediction == -1)

    # decision_function: more negative = more anomalous
    # We negate it so higher = more suspicious (intuitive for users)
    raw_anomaly_score = -iso_forest.decision_function(X_scaled)[0]

    # Normalize anomaly score to roughly 0-1 range using sigmoid-like transform
    # This makes the score more interpretable for end users
    anomaly_score = float(_normalize_anomaly_score(raw_anomaly_score))


    # STEP 3: K-Means — behavior clustering
    cluster_id = int(kmeans.predict(X_scaled)[0])
    cluster_label = cluster_map.get(cluster_id, "unknown")

    # STEP 4: Logistic Regression — risk probability
    # Stack scaled features + raw anomaly score (same as training)
    X_with_anomaly = np.column_stack([X_scaled, [raw_anomaly_score]])

    # predict_proba returns [prob_class_0, prob_class_1]
    # We want prob_class_1 = probability of being an attack
    risk_probability = float(log_reg.predict_proba(X_with_anomaly)[0, 1])

    # Determine risk tier
    risk_tier = _classify_risk_tier(risk_probability)

    return {
        "anomaly": is_anomaly,
        "anomaly_score": round(anomaly_score, 4),
        "cluster_id": cluster_id,
        "cluster_label": cluster_label,
        "risk_probability": round(risk_probability, 4),
        "risk_tier": risk_tier,
    }


def predict_batch(features_df: pd.DataFrame) -> pd.DataFrame:
    # Validate columns
    missing = [col for col in FEATURE_COLUMNS if col not in features_df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    # Extract feature matrix
    X = features_df[FEATURE_COLUMNS].values

    # Load models
    scaler = _load_model("scaler.pkl")
    iso_forest = _load_model("isolation_forest.pkl")
    kmeans = _load_model("kmeans.pkl")
    log_reg = _load_model("logistic_regression.pkl")
    cluster_map = _load_model("cluster_map.pkl")

    # Step 1: Scale
    X_scaled = scaler.transform(X)

    # Step 2: Isolation Forest
    iso_predictions = iso_forest.predict(X_scaled)
    raw_anomaly_scores = -iso_forest.decision_function(X_scaled)
    normalized_scores = np.array([_normalize_anomaly_score(s) for s in raw_anomaly_scores])

    # Step 3: K-Means
    cluster_ids = kmeans.predict(X_scaled)
    cluster_labels = [cluster_map.get(int(c), "unknown") for c in cluster_ids]

    # Step 4: Logistic Regression
    X_with_anomaly = np.column_stack([X_scaled, raw_anomaly_scores])
    risk_probabilities = log_reg.predict_proba(X_with_anomaly)[:, 1]
    risk_tiers = [_classify_risk_tier(p) for p in risk_probabilities]

    # Build result DataFrame
    result = features_df.copy()
    result["anomaly"] = (iso_predictions == -1)
    result["anomaly_score"] = normalized_scores.round(4)
    result["cluster_id"] = cluster_ids
    result["cluster_label"] = cluster_labels
    result["risk_probability"] = np.round(risk_probabilities, 4)
    result["risk_tier"] = risk_tiers

    return result



# HELPER FUNCTIONS

def _normalize_anomaly_score(raw_score: float) -> float:
    # Clip to expected range (based on our training data statistics)
    clipped = np.clip(raw_score, -0.2, 0.3)
    # Scale to 0-1
    normalized = (clipped - (-0.2)) / (0.3 - (-0.2))
    return float(normalized)


def _classify_risk_tier(probability: float) -> str:
    if probability >= HIGH_RISK_THRESHOLD:
        return "BLOCK"
    elif probability >= MEDIUM_RISK_THRESHOLD:
        return "MONITOR"
    else:
        return "SAFE"


# DEMO — Show predictions on known IPs from our dataset
def run_demo():
    print("=" * 65)
    print("  SentinelAPI -- Prediction Pipeline Demo")
    print("=" * 65)

    # Load the feature data
    features_file = os.path.join(DATA_DIR, "ip_features.csv")
    if not os.path.exists(features_file):
        print("ERROR: Feature file not found. Run features.py first.")
        return

    df = pd.read_csv(features_file)

    # Pre-load all models
    print("\n   Loading models...")
    load_all_models()


    # DEMO 1: Single IP prediction
    print("\n" + "-" * 65)
    print("  DEMO 1: Single IP Prediction")
    print("-" * 65)

    # Pick one normal IP and one attack IP
    normal_ip = df[df["attack_type"] == "normal"].iloc[0]
    attack_ip = df[df["attack_type"] == "bruteforce"].iloc[0]

    for label, ip_row in [("NORMAL USER", normal_ip), ("BRUTE-FORCE ATTACKER", attack_ip)]:
        features = {col: ip_row[col] for col in FEATURE_COLUMNS}
        result = predict_ip(features)

        print(f"\n  >> {label}: {ip_row['ip']}")
        print(f"     Input features:")
        for col in FEATURE_COLUMNS:
            print(f"       {col:30s}: {features[col]}")
        print(f"     Prediction:")
        print(f"       Anomaly:          {result['anomaly']}")
        print(f"       Anomaly score:    {result['anomaly_score']}")
        print(f"       Cluster:          {result['cluster_id']} ({result['cluster_label']})")
        print(f"       Risk probability: {result['risk_probability']}")
        print(f"       Risk tier:        {result['risk_tier']}")


    # DEMO 2: Batch prediction on all IPs
    print("\n" + "-" * 65)
    print("  DEMO 2: Batch Prediction (all 245 IPs)")
    print("-" * 65)

    results = predict_batch(df)

    # Summary by attack type
    print("\n   Results by actual attack type:\n")
    for attack_type in ["normal", "bruteforce", "scraper", "credential_stuffing"]:
        subset = results[results["attack_type"] == attack_type]
        if len(subset) == 0:
            continue

        avg_risk = subset["risk_probability"].mean()
        anomalies = subset["anomaly"].sum()
        tiers = subset["risk_tier"].value_counts().to_dict()

        print(f"   {attack_type.upper():25s} ({len(subset):3d} IPs)")
        print(f"     Avg risk prob:     {avg_risk:.4f}")
        print(f"     Anomalies found:   {anomalies}/{len(subset)}")
        print(f"     Risk tiers:        {tiers}")
        print()


    # DEMO 3: Simulate a brand new suspicious IP
    print("-" * 65)
    print("  DEMO 3: Simulate a NEW Suspicious IP")
    print("-" * 65)

    # This IP doesn't exist in our dataset — it's completely new
    new_suspicious_ip = {
        "requests_per_min": 5.0,       # Very high (normal is ~0.3)
        "endpoint_variety": 2,          # Hitting few endpoints
        "error_rate": 0.75,             # 75% errors (lots of 401s)
        "avg_time_between_reqs": 10.0,  # Very fast requests
        "single_endpoint_ratio": 0.85,  # Hammering one endpoint
        "user_agent_variety": 1,        # Single bot user agent
    }

    result = predict_ip(new_suspicious_ip)
    print(f"\n  >> NEW IP (never seen before)")
    print(f"     Input: {new_suspicious_ip}")
    print(f"     Result:")
    print(f"       Anomaly:          {result['anomaly']}")
    print(f"       Anomaly score:    {result['anomaly_score']}")
    print(f"       Cluster:          {result['cluster_id']} ({result['cluster_label']})")
    print(f"       Risk probability: {result['risk_probability']}")
    print(f"       Risk tier:        {result['risk_tier']}")

    new_safe_ip = {
        "requests_per_min": 0.3,        # Low rate
        "endpoint_variety": 8,           # Browsing normally
        "error_rate": 0.05,              # Few errors
        "avg_time_between_reqs": 200.0,  # Slow, human-like
        "single_endpoint_ratio": 0.2,    # Spread across pages
        "user_agent_variety": 1,         # One browser
    }

    result = predict_ip(new_safe_ip)
    print(f"\n  >> NEW IP (safe user)")
    print(f"     Input: {new_safe_ip}")
    print(f"     Result:")
    print(f"       Anomaly:          {result['anomaly']}")
    print(f"       Anomaly score:    {result['anomaly_score']}")
    print(f"       Cluster:          {result['cluster_id']} ({result['cluster_label']})")
    print(f"       Risk probability: {result['risk_probability']}")
    print(f"       Risk tier:        {result['risk_tier']}")



# ENTRY POINT
if __name__ == "__main__":
    run_demo()
