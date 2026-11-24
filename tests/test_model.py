import pytest
import numpy as np
from model.predictor import validate_inputs, classify_concrete_quality, predict_concrete_strength
from model.train_model import engineer_features
import pandas as pd

def test_validate_inputs():
    # Valid
    is_valid, msg = validate_inputs(28, 35, 4200)
    assert is_valid is True
    assert msg == ""
    
    # Negative age
    is_valid, msg = validate_inputs(-1, 35, 4200)
    assert is_valid is False
    assert "Age" in msg
    
    # Rebound out of range
    is_valid, msg = validate_inputs(28, 5, 4200)
    assert is_valid is False
    assert "Rebound" in msg
    
    # UPV out of range
    is_valid, msg = validate_inputs(28, 35, 800)
    assert is_valid is False
    assert "Ultrasonic" in msg

def test_feature_engineering():
    df = pd.DataFrame([{
        "Age": 28.0,
        "Rebound_Index": 35.0,
        "UPV": 4200.0
    }])
    X = engineer_features(df)
    assert list(X.columns) == [
        "Age", "Rebound_Index", "UPV", "UPV_over_Age", "Rebound_over_Age", "UPV_x_Rebound"
    ]
    assert X["UPV_over_Age"].iloc[0] == pytest.approx(4200.0 / 28.0)
    assert X["Rebound_over_Age"].iloc[0] == pytest.approx(35.0 / 28.0)
    assert X["UPV_x_Rebound"].iloc[0] == pytest.approx(4200.0 * 35.0)

def test_predict_known_anchor_c001():
    # C001: Age 1, Rebound 21.3, UPV 3649, Actual Strength 8.00
    res = predict_concrete_strength("C001", 1.0, 21.3, 3649.0)
    assert res["status"] == "Analysis Complete"
    assert 6.5 <= res["predicted_strength"] <= 8.5
    assert res["upv_grade"] == "Medium / Satisfactory"

def test_classify_concrete_quality():
    q_exc = classify_concrete_quality(4600, 45.0, 28)
    assert q_exc["upv_grade"] == "Excellent"
    
    q_good = classify_concrete_quality(4000, 30.0, 28)
    assert q_good["upv_grade"] == "Good"
    
    q_med = classify_concrete_quality(3300, 20.0, 14)
    assert q_med["upv_grade"] == "Medium / Satisfactory"
    
    q_doubt = classify_concrete_quality(2800, 12.0, 7)
    assert q_doubt["upv_grade"] == "Doubtful / Poor"
