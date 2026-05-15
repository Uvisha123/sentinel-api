import numpy as np
import pandas as pd
import os
import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (no GUI window needed)
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.decomposition import PCA



DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
FEATURES_FILE = os.path.join(DATA_DIR, "ip_features.csv")
PLOTS_DIR = os.path.join(DATA_DIR, "plots")

FEATURE_COLUMNS = [
    "requests_per_min",
    "endpoint_variety",
    "error_rate",
    "avg_time_between_reqs",
    "single_endpoint_ratio",
    "user_agent_variety",
]


# VISUALIZATION STYLE SETUP

def setup_plot_style():
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    })



# EVALUATION 1: ISOLATION FOREST
def evaluate_isolation_forest(X_scaled: np.ndarray, y_true: np.ndarray) -> dict:
    print("\n" + "=" * 60)
    print("  EVALUATION 1: Isolation Forest (Anomaly Detection)")
    print("=" * 60)

    iso_forest = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.pkl"))

    # Predict: 1 = normal, -1 = anomaly
    raw_predictions = iso_forest.predict(X_scaled)

    # Convert to our label scheme: -1 (anomaly) → 1 (attack), 1 (normal) → 0
    y_pred = (raw_predictions == -1).astype(int)

    # Compute metrics
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    # Confusion matrix breakdown
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    print(f"\n   True Positives  (attacks caught):       {tp}")
    print(f"   True Negatives  (normal correctly ok'd): {tn}")
    print(f"   False Positives (normal flagged wrongly): {fp}")
    print(f"   False Negatives (attacks missed):        {fn}")
    print(f"\n   Precision: {precision:.4f}  (of flagged IPs, {precision*100:.1f}% were real attacks)")
    print(f"   Recall:    {recall:.4f}  (caught {recall*100:.1f}% of all attacks)")
    print(f"   F1 Score:  {f1:.4f}  (harmonic mean of precision & recall)")

    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}



# EVALUATION 2: K-MEANS CLUSTERING
def evaluate_kmeans(X_scaled: np.ndarray, attack_types: pd.Series) -> dict:
    print("\n" + "=" * 60)
    print("  EVALUATION 2: K-Means Clustering (Behavior Profiling)")
    print("=" * 60)

    kmeans = joblib.load(os.path.join(MODELS_DIR, "kmeans.pkl"))
    cluster_map = joblib.load(os.path.join(MODELS_DIR, "cluster_map.pkl"))

    cluster_labels = kmeans.predict(X_scaled)

    # Silhouette score
    sil_score = silhouette_score(X_scaled, cluster_labels)
    print(f"\n   Silhouette Score: {sil_score:.4f}", end="")
    if sil_score > 0.7:
        print("  (Excellent separation)")
    elif sil_score > 0.5:
        print("  (Good separation)")
    elif sil_score > 0.25:
        print("  (Fair separation)")
    else:
        print("  (Poor separation — clusters overlap)")

    # Cluster purity
    print(f"\n   Cluster Purity Analysis:")
    total_pure = 0
    cluster_details = {}

    for cluster_id in range(kmeans.n_clusters):
        mask = cluster_labels == cluster_id
        types_in_cluster = attack_types[mask]
        total_in_cluster = mask.sum()

        if total_in_cluster == 0:
            continue

        # Purity = fraction of IPs that match the majority type
        majority_count = types_in_cluster.value_counts().iloc[0]
        purity = majority_count / total_in_cluster
        total_pure += majority_count

        mapped_label = cluster_map.get(cluster_id, "unknown")
        type_breakdown = types_in_cluster.value_counts().to_dict()

        print(f"\n     Cluster {cluster_id} -> '{mapped_label}' ({total_in_cluster} IPs, purity: {purity:.1%})")
        for atype, count in type_breakdown.items():
            marker = " <-- majority" if count == majority_count else ""
            print(f"       {atype:25s}: {count:3d}{marker}")

        cluster_details[cluster_id] = {
            "label": mapped_label,
            "size": total_in_cluster,
            "purity": purity,
        }

    overall_purity = total_pure / len(attack_types)
    print(f"\n   Overall Purity: {overall_purity:.4f} ({overall_purity*100:.1f}%)")

    return {"silhouette_score": sil_score, "overall_purity": overall_purity,
            "cluster_details": cluster_details}



# EVALUATION 3: LOGISTIC REGRESSION
def evaluate_logistic_regression(X_scaled: np.ndarray, y_true: np.ndarray,attack_types: pd.Series) -> dict:
    print("\n" + "=" * 60)
    print("  EVALUATION 3: Logistic Regression (Risk Scoring)")
    print("=" * 60)

    log_reg = joblib.load(os.path.join(MODELS_DIR, "logistic_regression.pkl"))
    iso_forest = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.pkl"))

    # Recreate the stacked features (6 features + anomaly score)
    anomaly_scores = -iso_forest.decision_function(X_scaled)
    X_with_anomaly = np.column_stack([X_scaled, anomaly_scores])

    # Predictions
    y_pred = log_reg.predict(X_with_anomaly)
    y_prob = log_reg.predict_proba(X_with_anomaly)[:, 1]

    # Classification report
    print("\n   Classification Report:\n")
    report = classification_report(y_true, y_pred, target_names=["Normal", "Attack"])
    # Indent each line for clean formatting
    for line in report.split("\n"):
        print(f"   {line}")

    # ROC-AUC
    roc_auc = roc_auc_score(y_true, y_prob)
    print(f"\n   ROC-AUC Score: {roc_auc:.4f}", end="")
    if roc_auc > 0.95:
        print("  (Excellent)")
    elif roc_auc > 0.9:
        print("  (Very Good)")
    elif roc_auc > 0.8:
        print("  (Good)")
    else:
        print("  (Needs improvement)")

    # Risk tier analysis
    print(f"\n   Risk Tier Breakdown:")
    for attack_type in ["normal", "bruteforce", "scraper", "credential_stuffing"]:
        mask = attack_types == attack_type
        if mask.sum() == 0:
            continue
        probs = y_prob[mask]
        tiers = pd.cut(probs, bins=[-0.01, 0.3, 0.7, 1.01],
                        labels=["SAFE", "MONITOR", "BLOCK"])
        tier_counts = tiers.value_counts().to_dict()
        print(f"     {attack_type:25s}: avg_prob={probs.mean():.4f}  tiers={tier_counts}")

    return {"roc_auc": roc_auc, "y_pred": y_pred, "y_prob": y_prob, "y_true": y_true}



# VISUALIZATION FUNCTIONS
def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray):
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Normal", "Attack"],
                yticklabels=["Normal", "Attack"],
                annot_kws={"size": 18},
                linewidths=2, linecolor="white",
                ax=ax)
    ax.set_xlabel("Predicted Label", fontsize=13)
    ax.set_ylabel("Actual Label", fontsize=13)
    ax.set_title("Confusion Matrix - Logistic Regression Risk Classifier", fontsize=14)

    filepath = os.path.join(PLOTS_DIR, "confusion_matrix.png")
    plt.savefig(filepath)
    plt.close()
    print(f"   Saved: {filepath}")


def plot_risk_distribution(y_prob: np.ndarray, attack_types: pd.Series):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        "normal": "#2ecc71",             # green
        "bruteforce": "#e74c3c",         # red
        "scraper": "#f39c12",            # orange
        "credential_stuffing": "#9b59b6" # purple
    }

    for attack_type in ["normal", "bruteforce", "scraper", "credential_stuffing"]:
        mask = attack_types == attack_type
        if mask.sum() == 0:
            continue
        ax.hist(y_prob[mask], bins=20, alpha=0.6, label=attack_type,
                color=colors.get(attack_type, "#95a5a6"), edgecolor="white")

    # Draw threshold lines
    ax.axvline(x=0.3, color="#2c3e50", linestyle="--", linewidth=1.5, label="MONITOR threshold (0.3)")
    ax.axvline(x=0.7, color="#c0392b", linestyle="--", linewidth=1.5, label="BLOCK threshold (0.7)")

    ax.set_xlabel("Risk Probability", fontsize=13)
    ax.set_ylabel("Number of IPs", fontsize=13)
    ax.set_title("Risk Score Distribution by Attack Type", fontsize=14)
    ax.legend(fontsize=10)

    filepath = os.path.join(PLOTS_DIR, "risk_distribution.png")
    plt.savefig(filepath)
    plt.close()
    print(f"   Saved: {filepath}")


def plot_feature_importance(feature_names: list):
    log_reg = joblib.load(os.path.join(MODELS_DIR, "logistic_regression.pkl"))
    weights = log_reg.coef_[0]

    all_features = feature_names + ["anomaly_score"]

    # Sort by absolute importance
    sorted_idx = np.argsort(np.abs(weights))
    sorted_features = [all_features[i] for i in sorted_idx]
    sorted_weights = weights[sorted_idx]

    # Color bars: positive = red (increases attack probability), negative = blue
    colors = ["#e74c3c" if w > 0 else "#3498db" for w in sorted_weights]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(sorted_features, sorted_weights, color=colors, edgecolor="white", height=0.6)
    ax.set_xlabel("Feature Weight (Coefficient)", fontsize=13)
    ax.set_title("Feature Importance — Logistic Regression", fontsize=14)

    # Add value labels on bars
    for bar, val in zip(bars, sorted_weights):
        x_pos = val + 0.02 if val >= 0 else val - 0.02
        ha = "left" if val >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va="center", ha=ha, fontsize=10)

    ax.axvline(x=0, color="#2c3e50", linewidth=0.8)

    filepath = os.path.join(PLOTS_DIR, "feature_importance.png")
    plt.savefig(filepath)
    plt.close()
    print(f"   Saved: {filepath}")


def plot_cluster_visualization(X_scaled: np.ndarray, attack_types: pd.Series):
    kmeans = joblib.load(os.path.join(MODELS_DIR, "kmeans.pkl"))

    # Reduce to 2D with PCA
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X_scaled)

    cluster_labels = kmeans.predict(X_scaled)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Colored by ACTUAL attack type
    colors_map = {
        "normal": "#2ecc71",
        "bruteforce": "#e74c3c",
        "scraper": "#f39c12",
        "credential_stuffing": "#9b59b6"
    }

    for attack_type, color in colors_map.items():
        mask = attack_types == attack_type
        if mask.sum() == 0:
            continue
        axes[0].scatter(X_2d[mask, 0], X_2d[mask, 1],
                        c=color, label=attack_type, alpha=0.7, s=50, edgecolors="white")

    axes[0].set_title("Actual Attack Types (Ground Truth)", fontsize=13)
    axes[0].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    axes[0].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    axes[0].legend(fontsize=9)

    # Plot 2: Colored by K-MEANS cluster assignment
    cluster_colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
    for cid in range(kmeans.n_clusters):
        mask = cluster_labels == cid
        axes[1].scatter(X_2d[mask, 0], X_2d[mask, 1],
                        c=cluster_colors[cid % len(cluster_colors)],
                        label=f"Cluster {cid}", alpha=0.7, s=50, edgecolors="white")

    # Plot centroids
    centroids_2d = pca.transform(kmeans.cluster_centers_)
    axes[1].scatter(centroids_2d[:, 0], centroids_2d[:, 1],
                    c="black", marker="X", s=200, linewidths=2,
                    edgecolors="white", label="Centroids", zorder=5)

    axes[1].set_title("K-Means Cluster Assignments", fontsize=13)
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    axes[1].legend(fontsize=9)

    plt.suptitle("Cluster Visualization (PCA 2D Projection)", fontsize=15, y=1.02)
    plt.tight_layout()

    filepath = os.path.join(PLOTS_DIR, "cluster_visualization.png")
    plt.savefig(filepath)
    plt.close()
    print(f"   Saved: {filepath}")


# MASTER EVALUATION FUNCTION
def run_full_evaluation():
    print("=" * 60)
    print("  SentinelAPI -- Full Model Evaluation")
    print("=" * 60)

    # Load data
    if not os.path.exists(FEATURES_FILE):
        print(f"ERROR: Feature file not found: {FEATURES_FILE}")
        print("Run 'python -m ml.features' first.")
        return

    df = pd.read_csv(FEATURES_FILE)
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))

    X = df[FEATURE_COLUMNS].values
    y = df["is_attack"].values
    attack_types = df["attack_type"]

    X_scaled = scaler.transform(X)

    print(f"\n   Dataset: {len(df)} IPs ({y.sum()} attacks, {(y == 0).sum()} normal)")

    # Create plots directory
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Setup plot style
    setup_plot_style()


    # Evaluate each model
    iso_results = evaluate_isolation_forest(X_scaled, y)
    kmeans_results = evaluate_kmeans(X_scaled, attack_types)
    lr_results = evaluate_logistic_regression(X_scaled, y, attack_types)

   # Generate visualizations
    print("\n" + "=" * 60)
    print("  GENERATING VISUALIZATIONS")
    print("=" * 60 + "\n")

    plot_confusion_matrix(lr_results["y_true"], lr_results["y_pred"])
    plot_risk_distribution(lr_results["y_prob"], attack_types)
    plot_feature_importance(FEATURE_COLUMNS)
    plot_cluster_visualization(X_scaled, attack_types)


    # Final Summary
    print("\n" + "=" * 60)
    print("  EVALUATION SUMMARY")
    print("=" * 60)
    print(f"""
   Isolation Forest (Anomaly Detection):
     Precision: {iso_results['precision']:.4f}
     Recall:    {iso_results['recall']:.4f}
     F1:        {iso_results['f1']:.4f}

   K-Means (Behavior Clustering):
     Silhouette Score:  {kmeans_results['silhouette_score']:.4f}
     Overall Purity:    {kmeans_results['overall_purity']:.4f}

   Logistic Regression (Risk Scoring):
     ROC-AUC:   {lr_results['roc_auc']:.4f}

   Visualizations saved to: {PLOTS_DIR}
     - confusion_matrix.png
     - risk_distribution.png
     - feature_importance.png
     - cluster_visualization.png
    """)


if __name__ == "__main__":
    run_full_evaluation()
