"""
data_transformation.py
──────────────────────
Mirrors notebook Cells 10, 12, 14, 53:
  - Feature engineering (startup_age, funding_per_round, etc.)
  - Missing value imputation
  - Encoding (low-card → one-hot, high-card → freq encoding)
  - StandardScaler for LR / SVM / SVR
  - Saves preprocessor.pkl to artifacts/
"""

import os
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

CURRENT_YEAR = 2026


@dataclass
class DataTransformationConfig:
    preprocessor_path: str = os.path.join("artifacts", "preprocessor.pkl")


class DataTransformation:
    def __init__(self):
        self.config = DataTransformationConfig()

    # ── Cell 10: Feature engineering ─────────────────────────

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Exact mirror of notebook Cell 10."""
        try:
            # Drop identifier columns
            for c in ["permalink", "name", "homepage_url"]:
                if c in df.columns:
                    df = df.drop(columns=[c])

            # startup_age
            if "founded_year" in df.columns:
                df["founded_year"] = pd.to_numeric(
                    df["founded_year"], errors="coerce")
                df["startup_age"] = (
                    CURRENT_YEAR - df["founded_year"]).clip(lower=0)
            else:
                df["startup_age"] = np.nan

            # Numeric conversions
            if "funding_total_usd" in df.columns:
                df["funding_total_usd"] = pd.to_numeric(
                    df["funding_total_usd"], errors="coerce")
            if "funding_rounds" in df.columns:
                df["funding_rounds"] = pd.to_numeric(
                    df["funding_rounds"], errors="coerce")

            # funding_per_round
            if {"funding_total_usd", "funding_rounds"}.issubset(df.columns):
                df["funding_per_round"] = (
                    df["funding_total_usd"] /
                    (df["funding_rounds"].fillna(0) + 1)
                )

            # rounds_per_year
            if {"startup_age", "funding_rounds"}.issubset(df.columns):
                df["rounds_per_year"] = (
                    df["funding_rounds"] /
                    (df["startup_age"].fillna(0) + 1)
                )

            # funding_per_employee
            emp_cols = [c for c in df.columns if "employee" in c.lower()]
            if emp_cols:
                emp_col = emp_cols[0]
                df[emp_col] = pd.to_numeric(df[emp_col], errors="coerce")
                df["funding_per_employee"] = (
                    df["funding_total_usd"] /
                    (df[emp_col].fillna(0) + 1)
                )

            # Date features
            for c in ["founded_at", "first_funding_at", "last_funding_at"]:
                if c in df.columns:
                    df[c] = pd.to_datetime(df[c], errors="coerce")

            if {"first_funding_at", "last_funding_at"}.issubset(df.columns):
                df["funding_span_days"] = (
                    df["last_funding_at"] -
                    df["first_funding_at"]
                ).dt.days

            df = df.drop(
                columns=[c for c in ["founded_at", "first_funding_at",
                                     "last_funding_at"]
                         if c in df.columns],
                errors="ignore"
            )

            return df
        except Exception as e:
            raise CustomException(e, sys)

    # ── Cell 12: Imputation ───────────────────────────────────

    def _impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Numeric → median, Categorical → 'Unknown'. Mirrors Cell 12."""
        try:
            for c in df.columns:
                if c == "success":
                    continue
                if df[c].dtype == "object":
                    df[c] = df[c].fillna("Unknown")
                else:
                    df[c] = df[c].fillna(df[c].median())
            return df
        except Exception as e:
            raise CustomException(e, sys)

    # ── Cell 53: Encoding ─────────────────────────────────────

    def _encode(self, df: pd.DataFrame):
        """
        Mirrors notebook Cell 53 (combined-data encoding):
          - category_list → category_first
          - low-card → one-hot
          - high-card → frequency encoding
        Returns (encoded_df, freq_maps, low_card)
        """
        try:
            # category_list → category_first
            if "category_list" in df.columns:
                df["category_first"] = (
                    df["category_list"]
                    .fillna("Unknown").astype(str)
                    .str.split("|").str[0]
                )
                df = df.drop(columns=["category_list"])

            cat_cols = df.select_dtypes(
                include=["object"]).columns.tolist()
            cat_cols = [c for c in cat_cols if c not in ["status"]]

            low_card = []
            high_card = []
            for c in cat_cols:
                if df[c].nunique(dropna=True) <= 20:
                    low_card.append(c)
                else:
                    high_card.append(c)

            logging.info(
                f"Low-card (one-hot): {low_card}  "
                f"High-card (freq): {high_card}"
            )

            # Frequency encoding
            freq_maps = {}
            for c in high_card:
                freq = df[c].value_counts(normalize=True)
                freq_maps[c] = freq
                df[c] = df[c].map(freq).fillna(0)

            # One-hot
            df = pd.get_dummies(df, columns=low_card, drop_first=True)

            # Drop status if still present
            if "status" in df.columns:
                df = df.drop(columns=["status"])

            # Final inf/null pass
            df = df.replace([np.inf, -np.inf], np.nan)
            for c in df.columns:
                if c == "success":
                    continue
                if df[c].dtype == "object":
                    df[c] = df[c].fillna("Unknown")
                else:
                    med = df[c].median()
                    df[c] = df[c].fillna(0 if pd.isna(med) else med)

            return df, freq_maps, low_card

        except Exception as e:
            raise CustomException(e, sys)

    # ── Main public method ────────────────────────────────────

    def initiate_data_transformation(self,
                                     train_path: str,
                                     test_path:  str):
        """
        Full transformation pipeline.

        Returns
        -------
        X_train, X_test         : raw DataFrames (for RF/XGBoost)
        y_train, y_test         : Series
        X_train_scaled, X_test_scaled : np.ndarray (for LR/SVC/SVR)
        scaler                  : fitted StandardScaler
        preprocessor_path       : str path to saved preprocessor.pkl
        """
        logging.info("Data transformation started")
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info(f"Train: {train_df.shape}  Test: {test_df.shape}")

            # Feature engineering
            train_df = self._engineer_features(train_df)
            test_df = self._engineer_features(test_df)

            # Impute
            train_df = self._impute(train_df)
            test_df = self._impute(test_df)

            # Encode — fit on train only
            train_df, freq_maps, low_card = self._encode(train_df)

            # Apply same freq maps to test
            for c, freq in freq_maps.items():
                if c in test_df.columns:
                    test_df[c] = test_df[c].map(freq).fillna(0)

            # category_list → category_first on test if needed
            if "category_list" in test_df.columns:
                test_df["category_first"] = (
                    test_df["category_list"]
                    .fillna("Unknown").astype(str)
                    .str.split("|").str[0]
                )
                test_df = test_df.drop(columns=["category_list"])

            # One-hot same low_card cols on test
            low_card_present = [c for c in low_card if c in test_df.columns]
            test_df = pd.get_dummies(
                test_df, columns=low_card_present, drop_first=True)

            if "status" in test_df.columns:
                test_df = test_df.drop(columns=["status"])

            # Align columns
            TARGET = "success"
            train_cols = [c for c in train_df.columns if c != TARGET]

            for col in train_cols:
                if col not in test_df.columns:
                    test_df[col] = 0

            test_df = test_df[
                train_cols + ([TARGET] if TARGET in test_df.columns else [])
            ]

            # Split X / y
            X_train = train_df.drop(columns=[TARGET])
            y_train = train_df[TARGET].astype(int)
            X_test = test_df.drop(columns=[TARGET])
            y_test = test_df[TARGET].astype(int)

            logging.info(
                f"X_train: {X_train.shape}  X_test: {X_test.shape}  "
                f"Train success: {y_train.mean():.3f}  "
                f"Test success: {y_test.mean():.3f}"
            )

            # Scale (Cell 20 / Cell 55)
            scaler = StandardScaler()
            scaler.fit(X_train)
            X_train_scaled = scaler.transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            logging.info("Scaling done")

            # Save preprocessor
            preprocessor = {
                "freq_maps":  freq_maps,
                "low_card":   low_card,
                "scaler":     scaler,
                "X_columns":  list(X_train.columns),
            }
            save_object(self.config.preprocessor_path, preprocessor)

            logging.info("Data transformation completed")
            return (
                X_train, X_test,
                y_train, y_test,
                X_train_scaled, X_test_scaled,
                scaler,
                self.config.preprocessor_path
            )

        except Exception as e:
            raise CustomException(e, sys)
