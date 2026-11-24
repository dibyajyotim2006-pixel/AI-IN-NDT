import os
import joblib
import numpy as np
import pandas as pd
from paths import get_model_path

MODEL_FILE = get_model_path()

_model_bundle = None

def get_model_bundle():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_FILE):
            from model.train_model import train_and_save_model
            _model_bundle = train_and_save_model(model_output_path=MODEL_FILE)
        else:
            _model_bundle = joblib.load(MODEL_FILE)
    return _model_bundle

def validate_inputs(age, rebound_index, upv):
    """
    Validates input parameters according to physical testing limits.
    Returns (is_valid, error_message).
    """
    try:
        age_val = float(age)
        rebound_val = float(rebound_index)
        upv_val = float(upv)
    except (ValueError, TypeError):
        return False, "All numerical inputs must be valid positive numbers."
        
    if age_val <= 0:
        return False, "Concrete Age must be greater than 0 days (e.g., 1 to 365 days)."
    if age_val > 730:
        return False, "Concrete Age exceeds 730 days (2 years). NDT models are calibrated for standard curing up to 2 years."
        
    if rebound_val < 10.0 or rebound_val > 70.0:
        return False, "Rebound Hammer Index typically falls between 10.0 and 70.0 (ASTM C805 / IS 13311 Part 2)."
        
    if upv_val < 1500.0 or upv_val > 5500.0:
        return False, "Ultrasonic Pulse Velocity must be within reasonable acoustic limits (1500 to 5500 m/s as per IS 13311 Part 1)."
        
    return True, ""

def classify_concrete_quality(upv, strength, age):
    """
    Evaluates concrete quality based on IS 13311 (Part 1) ultrasonic grading
    combined with predicted compressive strength and age maturity.
    """
    # IS 13311 Part 1 Ultrasonic Pulse Velocity criteria:
    # UPV > 4400 m/s (4.4 km/s): Excellent
    # UPV 3750 - 4400 m/s: Good
    # UPV 3000 - 3750 m/s: Medium / Satisfactory
    # UPV < 3000 m/s: Doubtful / Poor
    if upv >= 4400:
        upv_grade = "Excellent"
        upv_color = "#10B981"  # Emerald
        upv_desc = "High density, homogeneous concrete with minimal voids"
    elif upv >= 3700:
        upv_grade = "Good"
        upv_color = "#06B6D4"  # Cyan
        upv_desc = "Sound structural concrete, standard porosity"
    elif upv >= 3000:
        upv_grade = "Medium / Satisfactory"
        upv_color = "#F59E0B"  # Amber
        upv_desc = "Moderate internal compactness, potential localized micro-voids"
    else:
        upv_grade = "Doubtful / Poor"
        upv_color = "#EF4444"  # Red
        upv_desc = "Significant internal voids, honeycombing or microcracking"

    # Strength Category according to IS 456
    if strength >= 50.0:
        strength_class = "High-Performance Concrete (M50+)"
        grade_rec = "M50 - M60"
    elif strength >= 38.0:
        strength_class = "High-Strength Structural Concrete (M35-M45)"
        grade_rec = "M35 - M45"
    elif strength >= 25.0:
        strength_class = "Standard Structural Concrete (M25-M30)"
        grade_rec = "M25 - M30"
    elif strength >= 15.0:
        strength_class = "Moderate Strength / Lean Concrete (M15-M20)"
        grade_rec = "M15 - M20"
    else:
        if age <= 3:
            strength_class = "Early-Age Curing Concrete (< 15 MPa)"
            grade_rec = "Early Development"
        else:
            strength_class = "Low Strength / Sub-Structural (< 15 MPa)"
            grade_rec = "< M15"

    full_assessment = f"{upv_grade} Quality ({strength_class})"
    
    return {
        "upv_grade": upv_grade,
        "upv_color": upv_color,
        "upv_desc": upv_desc,
        "strength_class": strength_class,
        "grade_recommendation": grade_rec,
        "full_assessment": full_assessment
    }

def predict_concrete_strength(sample_id, age, rebound_index, upv):
    """
    Executes input validation, feature engineering, and neural network prediction.
    """
    is_valid, err = validate_inputs(age, rebound_index, upv)
    if not is_valid:
        raise ValueError(err)
        
    age = float(age)
    rebound_index = float(rebound_index)
    upv = float(upv)
    
    # 6 Input features matching IDP project documentation
    f1_age = age
    f2_rebound = rebound_index
    f3_upv = upv
    f4_upv_age = upv / age
    f5_rebound_age = rebound_index / age
    f6_upv_x_rebound = upv * rebound_index
    
    feature_dict = {
        "Age": f1_age,
        "Rebound_Index": f2_rebound,
        "UPV": f3_upv,
        "UPV_over_Age": f4_upv_age,
        "Rebound_over_Age": f5_rebound_age,
        "UPV_x_Rebound": f6_upv_x_rebound
    }
    
    features_df = pd.DataFrame([feature_dict])
    
    bundle = get_model_bundle()
    pipeline = bundle["pipeline"]
    scaler_X = bundle["scaler_X"]
    
    features_scaled = scaler_X.transform(features_df)
    predicted_val = float(pipeline.predict(features_scaled)[0])
    predicted_val = round(max(1.0, predicted_val), 2)
    
    quality_info = classify_concrete_quality(upv, predicted_val, age)
    
    result = {
        "sample_id": str(sample_id).strip() if sample_id else "C-AUTO",
        "age": age,
        "rebound_index": rebound_index,
        "upv": upv,
        "predicted_strength": predicted_val,
        "assessment": quality_info["full_assessment"],
        "upv_grade": quality_info["upv_grade"],
        "upv_color": quality_info["upv_color"],
        "upv_desc": quality_info["upv_desc"],
        "strength_class": quality_info["strength_class"],
        "grade_recommendation": quality_info["grade_recommendation"],
        "features": feature_dict,
        "status": "Analysis Complete"
    }
    
    return result
