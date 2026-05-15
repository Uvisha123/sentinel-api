import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.predict import predict_ip, predict_batch, load_all_models, clear_cache, FEATURE_COLUMNS



# MODEL LIFECYCLE MANAGEMENT
_models_loaded = False


def startup_load_models():
    global _models_loaded
    if not _models_loaded:
        try:
            load_all_models()
            _models_loaded = True
            print("   ML Service: Models loaded successfully")
        except FileNotFoundError as e:
            print(f"   ML Service WARNING: {e}")
            print("   ML endpoints will return errors until models are trained.")
            _models_loaded = False


def reload_models():
    global _models_loaded
    clear_cache()
    _models_loaded = False
    startup_load_models()
    return {"status": "Models reloaded successfully"}


def get_models_status() -> dict:
    return {
        "models_loaded": _models_loaded,
        "feature_columns": FEATURE_COLUMNS,
        "risk_thresholds": {
            "block": ">= 0.7",
            "monitor": "0.3 - 0.7",
            "safe": "< 0.3",
        },
    }


# PREDICTION FUNCTIONS
def score_ip(features: dict) -> dict:
    if not _models_loaded:
        raise RuntimeError(
            "ML models are not loaded. Run 'python -m ml.train' first, "
            "then restart the server."
        )

    result = predict_ip(features)

    # Add a human-readable recommendation
    if result["risk_tier"] == "BLOCK":
        result["recommendation"] = (
            "HIGH RISK — This IP shows attack-like behavior. "
            "Recommend immediate blocking."
        )
    elif result["risk_tier"] == "MONITOR":
        result["recommendation"] = (
            "MEDIUM RISK — This IP shows suspicious patterns. "
            "Recommend increased monitoring and rate limiting."
        )
    else:
        result["recommendation"] = (
            "LOW RISK — This IP appears to be a normal user. "
            "No action needed."
        )

    return result


def cluster_ip(features: dict) -> dict:
    if not _models_loaded:
        raise RuntimeError("ML models are not loaded.")

    result = predict_ip(features)

    # Build a behavioral profile based on the cluster
    profiles = {
        "normal": {
            "profile": "Normal User",
            "description": "Low request rate, varied endpoints, few errors. "
                           "Consistent with legitimate API usage.",
            "suggested_action": "Allow — no intervention needed.",
        },
        "bruteforce": {
            "profile": "Brute-Force Attacker",
            "description": "Extremely high request rate targeting a single endpoint "
                           "(likely /auth/login), with many 401 errors.",
            "suggested_action": "Block IP and enforce account lockout policy.",
        },
        "scraper": {
            "profile": "Scraper Bot",
            "description": "Systematically accessing many endpoints at medium-high rate. "
                           "Likely extracting data from the API.",
            "suggested_action": "Rate limit aggressively and consider CAPTCHA challenges.",
        },
        "credential_stuffing": {
            "profile": "Credential Stuffing",
            "description": "Burst traffic targeting auth endpoints with many 401 errors "
                           "and rotating user agents. Using leaked credential lists.",
            "suggested_action": "Block IP, flag affected accounts, enable MFA.",
        },
    }

    cluster_label = result["cluster_label"]
    profile_info = profiles.get(cluster_label, {
        "profile": "Unknown",
        "description": "Behavior pattern not recognized.",
        "suggested_action": "Monitor and investigate manually.",
    })

    return {
        "cluster_id": result["cluster_id"],
        "cluster_label": cluster_label,
        "anomaly": result["anomaly"],
        "anomaly_score": result["anomaly_score"],
        "risk_probability": result["risk_probability"],
        "risk_tier": result["risk_tier"],
        **profile_info,
        "input_features": features,
    }
