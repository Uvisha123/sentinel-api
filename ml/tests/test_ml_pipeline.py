import numpy as np
import pandas as pd
import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)


# TEST 1: DATA GENERATOR
class TestDataGenerator:
    """Tests for ml/data_generator.py"""

    def test_generate_dataset_creates_dataframe(self):
        """generate_dataset() should return a non-empty DataFrame."""
        from ml.data_generator import generate_dataset
        df = generate_dataset()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 5000, "Dataset should have 5000+ rows"

    def test_dataset_has_required_columns(self):
        """Dataset must have all required columns."""
        from ml.data_generator import generate_dataset
        df = generate_dataset()
        required = ["ip", "timestamp", "endpoint", "status_code",
                     "response_time_ms", "user_agent", "is_attack", "attack_type"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_dataset_has_attack_types(self):
        """Dataset should contain all 4 traffic types."""
        from ml.data_generator import generate_dataset
        df = generate_dataset()
        types = set(df["attack_type"].unique())
        expected = {"normal", "bruteforce", "scraper", "credential_stuffing"}
        assert expected == types, f"Expected {expected}, got {types}"

    def test_attack_labels_are_binary(self):
        """is_attack should only contain 0 and 1."""
        from ml.data_generator import generate_dataset
        df = generate_dataset()
        assert set(df["is_attack"].unique()) == {0, 1}

    def test_status_codes_are_valid(self):
        """All status codes should be realistic HTTP codes."""
        from ml.data_generator import generate_dataset
        df = generate_dataset()
        valid_codes = {200, 201, 400, 401, 403, 404, 429, 500}
        actual_codes = set(df["status_code"].unique())
        assert actual_codes.issubset(valid_codes), f"Unexpected codes: {actual_codes - valid_codes}"


# TEST 2: FEATURE ENGINEERING
class TestFeatureEngineering:
    """Tests for ml/features.py"""

    @pytest.fixture
    def sample_data(self):
        """Create a small sample DataFrame for testing."""
        return pd.DataFrame({
            "ip": ["1.1.1.1"] * 10,
            "timestamp": pd.date_range("2025-01-01 10:00", periods=10, freq="30s"),
            "endpoint": ["/login"] * 7 + ["/profile"] * 2 + ["/docs"],
            "status_code": [200] * 6 + [401] * 3 + [500],
            "response_time_ms": [100] * 10,
            "user_agent": ["Chrome"] * 8 + ["Firefox"] * 2,
            "is_attack": [0] * 10,
            "attack_type": ["normal"] * 10,
        })

    def test_requests_per_min(self, sample_data):
        """requests_per_min should be positive."""
        from ml.features import compute_requests_per_min
        result = compute_requests_per_min(sample_data)
        assert result > 0

    def test_endpoint_variety(self, sample_data):
        """endpoint_variety should count unique endpoints."""
        from ml.features import compute_endpoint_variety
        result = compute_endpoint_variety(sample_data)
        assert result == 3  # /login, /profile, /docs

    def test_error_rate_range(self, sample_data):
        """error_rate should be between 0 and 1."""
        from ml.features import compute_error_rate
        result = compute_error_rate(sample_data)
        assert 0 <= result <= 1
        assert result == 0.4  # 4 errors out of 10

    def test_single_endpoint_ratio(self, sample_data):
        """single_endpoint_ratio should be between 0 and 1."""
        from ml.features import compute_single_endpoint_ratio
        result = compute_single_endpoint_ratio(sample_data)
        assert 0 <= result <= 1
        assert result == 0.7  # 7 out of 10 go to /login

    def test_user_agent_variety(self, sample_data):
        """user_agent_variety should count unique agents."""
        from ml.features import compute_user_agent_variety
        result = compute_user_agent_variety(sample_data)
        assert result == 2  # Chrome, Firefox

    def test_engineer_features_output_shape(self, sample_data):
        """engineer_features should return 1 row per unique IP."""
        from ml.features import engineer_features
        result = engineer_features(sample_data)
        assert len(result) == 1  # Only 1 unique IP
        assert "requests_per_min" in result.columns
        assert "is_attack" in result.columns


# TEST 3: PREDICTIONS
class TestPredictions:
    """Tests for ml/predict.py — requires trained models."""

    @pytest.fixture
    def safe_features(self):
        """Features that look like a normal user."""
        return {
            "requests_per_min": 0.3,
            "endpoint_variety": 8,
            "error_rate": 0.05,
            "avg_time_between_reqs": 200.0,
            "single_endpoint_ratio": 0.2,
            "user_agent_variety": 1,
        }

    @pytest.fixture
    def attack_features(self):
        """Features that look like a brute-force attacker."""
        return {
            "requests_per_min": 5.0,
            "endpoint_variety": 2,
            "error_rate": 0.85,
            "avg_time_between_reqs": 10.0,
            "single_endpoint_ratio": 0.90,
            "user_agent_variety": 1,
        }

    def test_predict_ip_returns_dict(self, safe_features):
        """predict_ip should return a dict with required keys."""
        from ml.predict import predict_ip
        result = predict_ip(safe_features)
        assert isinstance(result, dict)
        required_keys = ["anomaly", "anomaly_score", "cluster_id",
                          "cluster_label", "risk_probability", "risk_tier"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_safe_ip_gets_safe_tier(self, safe_features):
        """A clearly normal IP should get SAFE tier."""
        from ml.predict import predict_ip
        result = predict_ip(safe_features)
        assert result["risk_tier"] == "SAFE"
        assert result["risk_probability"] < 0.3

    def test_attack_ip_gets_block_tier(self, attack_features):
        """A clearly malicious IP should get BLOCK tier."""
        from ml.predict import predict_ip
        result = predict_ip(attack_features)
        assert result["risk_tier"] == "BLOCK"
        assert result["risk_probability"] >= 0.7

    def test_risk_probability_in_range(self, safe_features):
        """Risk probability should always be between 0 and 1."""
        from ml.predict import predict_ip
        result = predict_ip(safe_features)
        assert 0 <= result["risk_probability"] <= 1

    def test_missing_features_raises_error(self):
        """predict_ip should raise ValueError if features are missing."""
        from ml.predict import predict_ip
        with pytest.raises(ValueError, match="Missing features"):
            predict_ip({"requests_per_min": 1.0})  # Only 1 of 6 features

    def test_batch_prediction(self):
        """predict_batch should handle multiple IPs."""
        from ml.predict import predict_batch
        df = pd.DataFrame([
            {"requests_per_min": 0.3, "endpoint_variety": 8, "error_rate": 0.05,
             "avg_time_between_reqs": 200, "single_endpoint_ratio": 0.2, "user_agent_variety": 1},
            {"requests_per_min": 5.0, "endpoint_variety": 2, "error_rate": 0.85,
             "avg_time_between_reqs": 10, "single_endpoint_ratio": 0.9, "user_agent_variety": 1},
        ])
        result = predict_batch(df)
        assert len(result) == 2
        assert "risk_tier" in result.columns


# TEST 4: RISK TIER CLASSIFICATION
class TestRiskTiers:
    """Tests for risk tier thresholds."""

    def test_block_threshold(self):
        """Probability >= 0.7 should be BLOCK."""
        from ml.predict import _classify_risk_tier
        assert _classify_risk_tier(0.7) == "BLOCK"
        assert _classify_risk_tier(0.95) == "BLOCK"
        assert _classify_risk_tier(1.0) == "BLOCK"

    def test_monitor_threshold(self):
        """Probability 0.3-0.7 should be MONITOR."""
        from ml.predict import _classify_risk_tier
        assert _classify_risk_tier(0.3) == "MONITOR"
        assert _classify_risk_tier(0.5) == "MONITOR"
        assert _classify_risk_tier(0.69) == "MONITOR"

    def test_safe_threshold(self):
        """Probability < 0.3 should be SAFE."""
        from ml.predict import _classify_risk_tier
        assert _classify_risk_tier(0.0) == "SAFE"
        assert _classify_risk_tier(0.1) == "SAFE"
        assert _classify_risk_tier(0.29) == "SAFE"
