"""
predict_pipeline.py
───────────────────
Mirrors notebook Cells 35, 37, 39:
  - preprocess_one() — exact copy from Cell 35
  - predict()        — exact copy of Cell 39 logic
  - get_confidence_band — exact copy of Cell 39 band logic

Called by FastAPI: POST /api/predict
"""

import os
import sys
import numpy as np
import pandas as pd

from src.exception import CustomException
from src.logger import logging
from src.utils import load_object, get_model_scores, get_confidence_band

CURRENT_YEAR = 2026


# ──────────────────────────────────────────────────────────────
# preprocess_one  (exact copy of notebook Cell 35)
# ──────────────────────────────────────────────────────────────

def preprocess_one(record_dict: dict,
                   X_columns,
                   country_df,
                   freq_maps: dict,
                   low_card: list) -> pd.DataFrame:
    """
    Preprocess a single startup record exactly like training.
    Returns a DataFrame with the same columns as X_train.

    Mirrors notebook Cell 35 preprocess_one() function exactly.
    """
    r = pd.DataFrame([record_dict]).copy()
    r.columns = [c.strip() for c in r.columns]

    # Basic string clean
    for c in r.select_dtypes(include=["object"]).columns:
        r[c] = r[c].astype(str).str.strip()
        r.loc[r[c].isin(["nan", "None", "NaT", ""]), c] = np.nan

    # Merge country fields (two-letter code)
    if "country_code" in r.columns and country_df is not None:
        ctry = country_df.rename(
            columns={"Two_Letter_Country_Code": "country_code"})
        r = r.merge(ctry, on="country_code", how="left")

    # Drop id cols
    for c in ["permalink", "name", "homepage_url"]:
        if c in r.columns:
            r = r.drop(columns=[c])

    # Drop target if present
    if "status" in r.columns:
        r = r.drop(columns=["status"])
    if "success" in r.columns:
        r = r.drop(columns=["success"])

    # Numeric conversions
    for col in ["funding_total_usd", "funding_rounds", "founded_year"]:
        if col in r.columns:
            r[col] = pd.to_numeric(r[col], errors="coerce")

    # startup_age
    if "founded_year" in r.columns:
        r["startup_age"] = (CURRENT_YEAR - r["founded_year"]).clip(lower=0)
    else:
        r["startup_age"] = np.nan

    # Derived features
    if {"funding_total_usd", "funding_rounds"}.issubset(r.columns):
        r["funding_per_round"] = (
            r["funding_total_usd"] /
            (r["funding_rounds"].fillna(0) + 1)
        )
    if {"startup_age", "funding_rounds"}.issubset(r.columns):
        r["rounds_per_year"] = (
            r["funding_rounds"] /
            (r["startup_age"].fillna(0) + 1)
        )

    # category_first
    if "category_list" in r.columns:
        r["category_first"] = (
            r["category_list"]
            .fillna("Unknown").astype(str)
            .str.split("|").str[0]
        )
        r = r.drop(columns=["category_list"])

    # Missing values
    for c in r.columns:
        if r[c].dtype == "object":
            r[c] = r[c].fillna("Unknown")
        else:
            r[c] = r[c].fillna(0)

    # Frequency encoding (use training freq_maps)
    for c, freq in freq_maps.items():
        if c in r.columns:
            r[c] = r[c].map(freq).fillna(0)

    # One-hot for low-card
    r = pd.get_dummies(
        r, columns=[c for c in low_card if c in r.columns], drop_first=True)

    # Align columns — add missing as 0
    for col in X_columns:
        if col not in r.columns:
            r[col] = 0
    r = r[X_columns]

    # Drop any remaining object columns (XGBoost can't handle them)
    obj_cols = r.select_dtypes(include=["object"]).columns.tolist()
    if obj_cols:
        r = r.drop(columns=obj_cols)

    # Final alignment
    for col in X_columns:
        if col not in r.columns:
            r[col] = 0
    final_cols = [c for c in X_columns if c in r.columns]
    r = r[final_cols]

    return r


# ──────────────────────────────────────────────────────────────
# PredictPipeline class
# ──────────────────────────────────────────────────────────────

class PredictPipeline:
    """
    Loads saved model.pkl from artifacts/ and predicts
    success probability for a single startup.
    Mirrors notebook Cell 39 prediction logic exactly.
    """

    def __init__(self):
        self.model_path = os.path.join("artifacts", "model.pkl")
        self._pkg = None

    def _load(self):
        if self._pkg is None:
            self._pkg = load_object(self.model_path)
            logging.info("model.pkl loaded")

    def predict(self, startup_data: dict) -> dict:
        """
        Predict success for one startup.

        Parameters
        ----------
        startup_data : dict of startup features

        Returns
        -------
        dict with keys:
            success          (0 or 1)
            probability      (float 0-1)
            confidence_band  (str)
            best_model_name  (str)
        """
        try:
            self._load()
            pkg = self._pkg
            best_model_name = pkg["best_model_name"]
            models = pkg["models"]
            svr_model = pkg["svr_model"]
            scaler = pkg["scaler"]
            preprocessor = pkg["preprocessor"]
            decision_threshold = float(pkg.get("decision_threshold", 0.5))

            freq_maps = preprocessor["freq_maps"]
            low_card = preprocessor["low_card"]
            X_columns = preprocessor["X_columns"]
            country_df = preprocessor.get("country_df", None)

            # Preprocess — exact Cell 35 function
            X_one = preprocess_one(
                startup_data, X_columns, country_df, freq_maps, low_card)

            # Predict — exact Cell 39 logic
            if best_model_name == "Support Vector Regression (SVR score)":
                one_scaled = scaler.transform(X_one)
                score = float(svr_model.predict(one_scaled)[0])
                prob = float(np.clip(score, 0, 1))
                pred = int(prob >= decision_threshold)
            else:
                best_mode, best_model = models[best_model_name]
                if best_mode == "scaled":
                    one_scaled = scaler.transform(X_one)
                    prob = float(get_model_scores(best_model, one_scaled)[0])
                    pred = int(prob >= decision_threshold)
                else:
                    prob = float(get_model_scores(best_model, X_one)[0])
                    pred = int(prob >= decision_threshold)

            band = get_confidence_band(prob)
            logging.info(
                f"Prediction → {pred} | prob={prob:.4f} | {band}")

            return {
                "success":         pred,
                "probability":     round(prob, 4),
                "confidence_band": band,
                "best_model_name": best_model_name,
            }

        except Exception as e:
            raise CustomException(e, sys)


# ── Quick test ─────────────────────────────────────────────────
if __name__ == "__main__":
    pipeline = PredictPipeline()

    # Matches notebook Cell 37 sample_company
    sample = {
        "funding_total_usd": 5000000,
        "funding_rounds":    2,
        "country_code":      "US",
        "founded_year":      2015,
        "seed":              1,
        "venture":           1,
    }

    result = pipeline.predict(sample)

    print("\n==============================")
    print("SINGLE COMPANY PREDICTION")
    print("==============================")
    print("Predicted Success (0=Fail, 1=Success):", result["success"])
    print("Predicted Success Probability/Score:  ", result["probability"])
    print("Prediction Band:", result["confidence_band"])
    print("Model used:     ", result["best_model_name"])
