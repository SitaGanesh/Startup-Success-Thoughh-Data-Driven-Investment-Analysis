"""
data_ingestion.py
─────────────────
Mirrors notebook Cells 4, 6, 8 with reliability updates:
    - Load start_up_data.csv + country_data.csv
    - Clean column names and string values
    - Create success target (acquired/ipo=1, closed=0)
    - Drop operating as censored/unknown outcome
    - Merge country data on country_code
    - Time-based split with class-drift guardrail fallback
    - Save raw.csv, train.csv, test.csv to artifacts/
"""

import os
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass
from sklearn.model_selection import train_test_split

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    raw_data_path:   str = os.path.join("artifacts", "raw.csv")
    train_data_path: str = os.path.join("artifacts", "train.csv")
    test_data_path:  str = os.path.join("artifacts", "test.csv")
    country_path:    str = os.path.join("..", "data", "country_data.csv")
    startup_path:    str = os.path.join("..", "data", "start_up_data.csv")
    angel_path:      str = os.path.join("..", "data", "AngelList_Startups.csv")


class DataIngestion:
    def __init__(self):
        self.config = DataIngestionConfig()

    # ── AngelList helpers (mirrors Cells 45, 47) ──────────────

    @staticmethod
    def _derive_success_angellist(row) -> float:
        """Exact copy of notebook derive_success_angellist()."""
        stage = row["Stage"]
        signal = row["Signal"]
        raised = row["Total Raised"]

        # Clear successes
        if stage == "Acquired":
            return 1
        if stage in ["Series B", "Series C"]:
            return 1
        if stage == "Series A" and signal >= 4:
            return 1
        if stage == "Seed" and signal >= 4 and pd.notna(raised) and raised >= 500000:
            return 1

        # Clear failures
        if signal <= 2:
            return 0
        if signal == 3 and (pd.isna(raised) or raised == 0):
            return 0
        if stage == "Seed" and signal == 3 and (pd.isna(raised) or raised < 100000):
            return 0

        return np.nan   # ambiguous — will be dropped

    def _load_angellist(self) -> pd.DataFrame:
        """Load + label AngelList data, mirror Cells 43-47."""
        CURRENT_YEAR = 2026
        emp_map = {
            "1-10":    5,
            "11-50":   30,
            "51-200":  125,
            "201-500": 350,
            "501-1000": 750,
        }

        angel = pd.read_csv(self.config.angel_path)
        angel.columns = [c.strip() for c in angel.columns]

        angel["success"] = angel.apply(
            self._derive_success_angellist, axis=1)
        angel_labeled = angel[angel["success"].notna()].copy()
        angel_labeled["success"] = angel_labeled["success"].astype(int)
        logging.info(
            f"AngelList usable rows: {len(angel_labeled)} "
            f"({angel_labeled['success'].mean():.1%} success)"
        )

        angel_feat = pd.DataFrame()
        angel_feat["market"] = angel_labeled["Market"].fillna("Unknown")
        angel_feat["funding_total_usd"] = pd.to_numeric(
            angel_labeled["Total Raised"], errors="coerce")
        angel_feat["founded_year"] = angel_labeled["Joining_Year"]
        angel_feat["startup_age"] = (
            CURRENT_YEAR - angel_labeled["Joining_Year"]).clip(lower=0)
        angel_feat["funding_rounds"] = np.nan
        angel_feat["country_code"] = "US"
        angel_feat["region"] = angel_labeled["Location"].fillna("Unknown")
        angel_feat["city"] = angel_labeled["Location"].fillna("Unknown")
        angel_feat["angellist_signal"] = angel_labeled["Signal"]
        angel_feat["employee_count"] = angel_labeled["Employees"].map(emp_map)
        angel_feat["latitude"] = angel_labeled["latitude"]
        angel_feat["longitude"] = angel_labeled["longitude"]
        angel_feat["funding_per_round"] = (
            angel_feat["funding_total_usd"] /
            (angel_feat["funding_rounds"].fillna(0) + 1)
        )
        angel_feat["rounds_per_year"] = (
            angel_feat["funding_rounds"].fillna(0) /
            (angel_feat["startup_age"] + 1)
        )
        angel_feat["success"] = angel_labeled["success"].values

        return angel_feat

    # ── Main ingestion method ─────────────────────────────────

    def initiate_data_ingestion(self):
        """
        Full ingestion pipeline matching notebook Cells 4-8, 18.
        Returns (train_path, test_path, country_df)
        """
        logging.info("Data ingestion started")
        try:
            # ── Cell 4: Load ──────────────────────────────────
            df = pd.read_csv(self.config.startup_path,
                             encoding="unicode_escape")
            country = pd.read_csv(self.config.country_path,
                                  encoding="unicode_escape")

            df.columns = [c.strip() for c in df.columns]
            country.columns = [c.strip() for c in country.columns]

            for c in df.select_dtypes(include=["object"]).columns:
                df[c] = df[c].astype(str).str.strip()
                df.loc[df[c].isin(["nan", "None", "NaT", ""]), c] = np.nan

            for c in country.select_dtypes(include=["object"]).columns:
                country[c] = country[c].astype(str).str.strip()

            logging.info(
                f"Loaded startup: {df.shape}  country: {country.shape}")

            # ── Cell 6: Create target ─────────────────────────
            # Treat "operating" as censored/unknown so the model learns
            # realized outcomes instead of defaulting to majority-success.
            df["status"] = (
                df["status"].astype("object").fillna(
                    "Unknown").astype(str).str.lower().str.strip()
            )
            df = df[df["status"].isin(["acquired", "ipo", "closed"])].copy()
            df["success"] = df["status"].map(
                {"acquired": 1, "ipo": 1, "closed": 0}
            ).astype(int)
            logging.info(
                f"Target created. Success rate: {df['success'].mean():.1%}")

            # ── Cell 8: Merge country ─────────────────────────
            country_merge = country.rename(
                columns={"Two_Letter_Country_Code": "country_code"})
            df_merged = df.merge(country_merge, on="country_code", how="left")
            logging.info(f"After country merge: {df_merged.shape}")

            # ── Cells 43-47: Append AngelList ─────────────────
            angel_feat = self._load_angellist()
            df_combined = pd.concat(
                [df_merged, angel_feat], ignore_index=True, sort=False)
            logging.info(
                f"After AngelList concat: {df_combined.shape}  "
                f"success: {df_combined['success'].mean():.1%}"
            )

            # ── Cell 51: Fill NaN from concat ─────────────────
            for c in df_combined.columns:
                if c == "success":
                    continue
                if df_combined[c].dtype == "object":
                    df_combined[c] = df_combined[c].fillna("Unknown")
                else:
                    df_combined[c] = df_combined[c].fillna(
                        df_combined[c].median())

            df_combined = df_combined.replace([np.inf, -np.inf], np.nan)
            for c in df_combined.columns:
                if c == "success":
                    continue
                if df_combined[c].dtype == "object":
                    df_combined[c] = df_combined[c].fillna("Unknown")
                else:
                    med = df_combined[c].median()
                    df_combined[c] = df_combined[c].fillna(
                        0 if pd.isna(med) else med)

            # ── Save raw ──────────────────────────────────────
            os.makedirs("artifacts", exist_ok=True)
            df_combined.to_csv(self.config.raw_data_path, index=False)

            # ── Cell 55: Time-based split ──────────────────────
            TARGET = "success"
            X_all = df_combined.drop(columns=[TARGET])
            y_all = df_combined[TARGET].astype(int)

            time_split_used = False
            split_reason = "random stratified"
            if "founded_year" in X_all.columns:
                cutoff = int(np.nanpercentile(X_all["founded_year"], 80))
                train_idx = X_all["founded_year"] <= cutoff
                test_idx = X_all["founded_year"] > cutoff

                if test_idx.sum() >= 500 and train_idx.sum() >= 1000:
                    candidate_train = df_combined[train_idx]
                    candidate_test = df_combined[test_idx]
                    train_pos = float(candidate_train[TARGET].mean())
                    test_pos = float(candidate_test[TARGET].mean())
                    class_rate_drift = abs(train_pos - test_pos)

                    if class_rate_drift <= 0.08:
                        train_df = candidate_train
                        test_df = candidate_test
                        time_split_used = True
                        split_reason = "time-based"
                    else:
                        split_reason = (
                            "random stratified (temporal class drift too high: "
                            f"{class_rate_drift:.3f})"
                        )
                        logging.warning(
                            "Temporal split skipped due to class-rate drift. "
                            f"train_success={train_pos:.3f}, test_success={test_pos:.3f}, "
                            f"drift={class_rate_drift:.3f}"
                        )

            if not time_split_used:
                from sklearn.model_selection import train_test_split
                train_df, test_df = train_test_split(
                    df_combined, test_size=0.20,
                    random_state=42, stratify=df_combined[TARGET]
                )

            split_type = "Time-based" if time_split_used else "Random stratified"
            logging.info(
                f"Split: {split_type} ({split_reason})  "
                f"Train: {train_df.shape}  Test: {test_df.shape}"
            )

            train_df.to_csv(self.config.train_data_path, index=False)
            test_df.to_csv(self.config.test_data_path,   index=False)

            logging.info("Data ingestion completed")
            # Return country_df so transformation can use it for preprocess_one
            return (
                self.config.train_data_path,
                self.config.test_data_path,
                country,
            )

        except Exception as e:
            raise CustomException(e, sys)
