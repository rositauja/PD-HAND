# predict.py 
import os
import joblib
import numpy as np
import pandas as pd
import cv2

# Load models
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spiral_model  = joblib.load(os.path.join(BASE_DIR, "models", "spiral", "spiral_model_combined.pkl"))
meander_model = joblib.load(os.path.join(BASE_DIR, "models", "meander", "meander_model_combined.pkl"))

FEATURE_ORDER = None

def predict_spiral(image_or_features):
    """
    CORRECTED: Now takes raw BGR image and preprocesses it correctly.
    
    Args:
        image_or_features: Either a raw BGR image (from upload) or a features dict
        
    Returns:
        tuple: (label, confidence)
    """
    # If features dict is passed directly, use it
    if isinstance(image_or_features, dict):
        features = image_or_features
    else:
        # If raw image is passed, preprocess it with training pipeline
        from core.preprocess import preprocess_spiral
        from core.features import extract_spiral_features
        
        image = image_or_features
        gray, thresh = preprocess_spiral(image)
        features = extract_spiral_features(thresh)
    
    feature_df = pd.DataFrame([features])

    prediction   = spiral_model.predict(feature_df)[0]
    probabilities = spiral_model.predict_proba(feature_df)[0]
    confidence   = float(max(probabilities))
    label        = "High Likelihood" if prediction == 1 else "Low Likelihood"
    return label, confidence

def predict_meander(image_or_features):
    """
    CORRECTED: Takes raw BGR image and preprocesses it correctly.
    
    Args:
        image_or_features: Either a raw BGR image (from upload) or a features dict
        
    Returns:
        tuple: (label, confidence)
    """
    # If features dict is passed directly, use it
    if isinstance(image_or_features, dict):
        features = image_or_features
    else:
        # If raw image is passed, preprocess it with training pipeline
        from core.preprocess import preprocess_meander
        from core.features import extract_meander_features
        
        image = image_or_features
        gray, thresh = preprocess_meander(image)
        features = extract_meander_features(thresh)
    
    feature_df = pd.DataFrame([features])

    prediction    = meander_model.predict(feature_df)[0]
    probabilities = meander_model.predict_proba(feature_df)[0]
    confidence    = float(max(probabilities))
    label         = "High Likelihood" if prediction == 1 else "Low Likelihood"
    return label, confidence

def predict_draw(image, pattern_type):
    from core.preprocess import preprocess_draw
    from core.features import extract_spiral_features, extract_meander_features

    gray, thresh = preprocess_draw(image)

    if pattern_type == "Spiral":
        features = extract_spiral_features(thresh)
        model = spiral_model
    else:
        features = extract_meander_features(thresh)
        model = meander_model

    feature_df = pd.DataFrame([features])

    prediction = model.predict(feature_df)[0]
    probabilities = model.predict_proba(feature_df)[0]

    confidence = float(max(probabilities))
    label = "High Likelihood" if prediction == 1 else "Low Likelihood"

    return label, confidence, features