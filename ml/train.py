import numpy as np
import pandas as pd
import os
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
FEATURES_FILE = os.path.join(DATA_DIR, "ip_features.csv")

# The 6 features models will use
FEATURE_COLUMNS = [
    "requests_per_min",
    "endpoint_variety",
    "error_rate",
    "avg_time_between_reqs",
    "single_endpoint_ratio",
    "user_agent_variety",
]


# MODEL 1: ISOLATION FOREST
def train_isolation_forest(X_scaled: np.ndarray) -> IsolationForest:

    print("\n--- Training Model 1: Isolation Forest ---")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.18,
        random_state=42,
        n_jobs=-1,       # Use all CPU cores for speed
    )

    model.fit(X_scaled)

    # Predict on training data to see how it performs
    # predict() returns: 1 = normal, -1 = anomaly
    predictions = model.predict(X_scaled)
    n_anomalies = (predictions == -1).sum()
    n_normal = (predictions == 1).sum()

    print(f"   Trees:       {model.n_estimators}")
    print(f"   Contamination: {model.contamination}")
    print(f"   Detected:    {n_anomalies} anomalies, {n_normal} normal")

    # decision_function() returns the anomaly score
    # More negative = more anomalous
    scores = model.decision_function(X_scaled)
    print(f"   Score range:  [{scores.min():.3f}, {scores.max():.3f}]")
    print(f"   Score mean:   {scores.mean():.3f}")

    return model


# MODEL 2: K-MEANS CLUSTERING
def train_kmeans(X_scaled: np.ndarray) -> KMeans:

    print("\n--- Training Model 2: K-Means Clustering ---")

    model = KMeans(
        n_clusters=4,
        n_init=10,
        max_iter=300,
        random_state=42,
    )

    model.fit(X_scaled)

    # Show cluster sizes
    labels = model.labels_
    print(f"   Clusters:    {model.n_clusters}")
    print(f"   Iterations:  {model.n_iter_}")
    print(f"   Inertia:     {model.inertia_:.2f} (lower = tighter clusters)")

    for cluster_id in range(model.n_clusters):
        count = (labels == cluster_id).sum()
        print(f"   Cluster {cluster_id}:   {count} IPs")

    return model



# MODEL 3: LOGISTIC REGRESSION
def train_logistic_regression(X_train: np.ndarray, y_train: np.ndarray,X_test: np.ndarray, y_test: np.ndarray) -> LogisticRegression:

    print("\n--- Training Model 3: Logistic Regression ---")

    model = LogisticRegression(
        random_state=42,
        max_iter=1000,   
        solver="lbfgs",   
    )

    model.fit(X_train, y_train)

    # Check accuracy on both sets
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)

    print(f"   Training accuracy:  {train_acc:.4f} ({train_acc * 100:.1f}%)")
    print(f"   Test accuracy:      {test_acc:.4f} ({test_acc * 100:.1f}%)")

    # Show feature importance (weights)
    print(f"\n   Feature weights (importance):")
    feature_names = FEATURE_COLUMNS + ["anomaly_score"]
    weights = model.coef_[0]
    # Sort by absolute value (most important first)
    sorted_indices = np.argsort(np.abs(weights))[::-1]
    for idx in sorted_indices:
        direction = "+" if weights[idx] > 0 else "-"
        print(f"     {direction} {feature_names[idx]:30s}: {weights[idx]:+.4f}")

    print(f"   Bias (intercept):   {model.intercept_[0]:+.4f}")

    # Cross-validation: more robust accuracy estimate than a single split
    print(f"\n   Cross-validation (5-fold):")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")
    print(f"     F1 scores:  {cv_scores.round(4)}")
    print(f"     Mean F1:    {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

    # Show risk score distribution on test set
    probabilities = model.predict_proba(X_test)[:, 1]  # probability of class 1 (attack)
    print(f"\n   Risk score distribution (test set):")
    print(f"     HIGH risk   (>= 0.7): {(probabilities >= 0.7).sum()} IPs")
    print(f"     MEDIUM risk (0.3-0.7): {((probabilities >= 0.3) & (probabilities < 0.7)).sum()} IPs")
    print(f"     LOW risk    (< 0.3):  {(probabilities < 0.3).sum()} IPs")

    return model


# CLUSTER MAPPING — Map arbitrary cluster IDs to meaningful labels
def map_clusters_to_labels(kmeans_model: KMeans, X_scaled: np.ndarray,attack_types: pd.Series) -> dict:

    print("\n--- Mapping Clusters to Behavior Types ---")

    cluster_labels = kmeans_model.predict(X_scaled)
    cluster_map = {}

    for cluster_id in range(kmeans_model.n_clusters):
        mask = cluster_labels == cluster_id
        types_in_cluster = attack_types[mask]
        majority_type = types_in_cluster.value_counts().index[0]
        count = types_in_cluster.value_counts().iloc[0]
        total = mask.sum()

        cluster_map[int(cluster_id)] = majority_type
        print(f"   Cluster {cluster_id} → {majority_type:25s} "
              f"({count}/{total} IPs, {count/total*100:.0f}% purity)")

    return cluster_map



# MASTER TRAINING PIPELINE
def train_all_models():

    print("=" * 60)
    print("  SentinelAPI -- Model Training Pipeline")
    print("=" * 60)

    # STEP 1: Load feature data
    if not os.path.exists(FEATURES_FILE):
        print(f"ERROR: Feature file not found: {FEATURES_FILE}")
        print("Run 'python -m ml.features' first.")
        exit(1)

    df = pd.read_csv(FEATURES_FILE)
    print(f"\n   Loaded {len(df)} IP feature vectors")
    print(f"   Attack IPs:  {df['is_attack'].sum()}")
    print(f"   Normal IPs:  {(df['is_attack'] == 0).sum()}")

    # Extract feature matrix and labels
    X = df[FEATURE_COLUMNS].values       # Shape: (245, 6)
    y = df["is_attack"].values            # Shape: (245,)
    attack_types = df["attack_type"]      # For cluster mapping


    # STEP 2: Standardize features
    print("\n--- Standardizing Features ---")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"   Before scaling — mean: {X.mean(axis=0).round(3)}")
    print(f"   After scaling  — mean: {X_scaled.mean(axis=0).round(3)}")
    print(f"   After scaling  — std:  {X_scaled.std(axis=0).round(3)}")


    # STEP 3: Train Isolation Forest (on ALL data — unsupervised)
    iso_forest = train_isolation_forest(X_scaled)


    # STEP 4: Generate anomaly scores to feed into Logistic Regression
    # decision_function returns raw anomaly scores (more negative = more anomalous)
    # We NEGATE it so that higher score = more anomalous (more intuitive)
    anomaly_scores = -iso_forest.decision_function(X_scaled)
    print(f"\n   Anomaly scores added as extra feature for Logistic Regression")

    # Stack anomaly scores onto the feature matrix
    # X_with_anomaly shape: (245, 7) — original 6 features + anomaly score
    X_with_anomaly = np.column_stack([X_scaled, anomaly_scores])

    # STEP 5: Train/test split (for Logistic Regression)
    X_train, X_test, y_train, y_test = train_test_split(
        X_with_anomaly, y,
        test_size=0.2,       # 80% train, 20% test
        random_state=42,     # Reproducible split
        stratify=y,          # Keep same ratio of attack/normal in both sets
    )
    print(f"\n   Train/Test split: {len(X_train)} train, {len(X_test)} test")
    print(f"   Train attacks: {y_train.sum()}, Test attacks: {y_test.sum()}")


    # STEP 6: Train K-Means (on ALL data — unsupervised)
    kmeans = train_kmeans(X_scaled)

    # STEP 7: Train Logistic Regression (on TRAIN split only)
    log_reg = train_logistic_regression(X_train, y_train, X_test, y_test)


    # STEP 8: Map clusters to meaningful labels
    cluster_map = map_clusters_to_labels(kmeans, X_scaled, attack_types)


    # STEP 9: Save everything
    print("\n--- Saving Models ---")
    os.makedirs(MODELS_DIR, exist_ok=True)

    models_to_save = {
        "isolation_forest.pkl": iso_forest,
        "kmeans.pkl": kmeans,
        "logistic_regression.pkl": log_reg,
        "scaler.pkl": scaler,
        "cluster_map.pkl": cluster_map,
    }

    for filename, model in models_to_save.items():
        filepath = os.path.join(MODELS_DIR, filename)
        joblib.dump(model, filepath)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   Saved: {filename:30s} ({size_kb:.1f} KB)")

    # SUMMARY
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print("=" * 60)
    print(f"""
   Models saved to: {MODELS_DIR}

   Model 1 — Isolation Forest:
     - Detects anomalies based on isolation path length
     - Found {(iso_forest.predict(X_scaled) == -1).sum()} anomalies in training data

   Model 2 — K-Means (4 clusters):
     - Cluster mapping: {cluster_map}
     - Inertia: {kmeans.inertia_:.2f}

   Model 3 — Logistic Regression:
     - Test accuracy: {log_reg.score(X_test, y_test)*100:.1f}%
     - Uses 6 features + anomaly score = 7 inputs
    """)

    return iso_forest, kmeans, log_reg, scaler, cluster_map


# ENTRY POINT
if __name__ == "__main__":
    train_all_models()
