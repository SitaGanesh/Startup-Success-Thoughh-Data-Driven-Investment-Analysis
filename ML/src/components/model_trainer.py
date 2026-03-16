"""
model_trainer.py
────────────────
Mirrors notebook Cells 22, 24, 27:
  - Uses train_model_suite() from utils (exact notebook function)
  - Picks best model by ROC_AUC
  - Saves model.pkl + model_results.csv to artifacts/
"""

import os
import sys
import pandas as pd
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.svm import SVR

from src.exception import CustomException
from src.logger import logging
from src.utils import (
    save_object,
    train_model_suite,
    load_object,
    get_model_scores,
    tune_threshold,
)


@dataclass
class ModelTrainerConfig:
    model_path:   str = os.path.join("artifacts", "model.pkl")
    results_path: str = os.path.join("artifacts", "model_results.csv")


class ModelTrainer:
    def __init__(self):
        self.config = ModelTrainerConfig()

    def initiate_model_training(
        self,
        X_train, X_test,
        y_train, y_test,
        preprocessor_path: str,
        fast_mode: bool = True
    ):
        """
        Train all 5 models using train_model_suite(),
        pick best by balanced metrics, save model.pkl + results CSV.

        Returns
        -------
        best_model_name : str
        best_roc_auc    : float
        results_df      : DataFrame (sorted by Balanced_Accuracy, Macro_F1, ROC_AUC)
        """
        logging.info("Model training started")
        try:
            # Load preprocessor to get scaler + column info
            preprocessor = load_object(preprocessor_path)
            scaler = preprocessor["scaler"]
            X_columns = preprocessor["X_columns"]

            # Scale for LR / SVC / SVR
            X_train_scaled = scaler.transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train all models — exact notebook Cell 22 function
            models, svr_model, results, svr_score_clamped, svr_auc = train_model_suite(
                X_train_raw=X_train,
                X_test_raw=X_test,
                X_train_scaled=X_train_scaled,
                X_test_scaled=X_test_scaled,
                y_train=y_train,
                y_test=y_test,
                tag="Original + AngelList",
                fast_mode=fast_mode
            )

            # Build results DataFrame with additional class-balance metrics.
            results_df = pd.DataFrame(
                results,
                columns=["Model", "Accuracy", "Precision",
                         "Recall", "F1", "ROC_AUC",
                         "Balanced_Accuracy", "Macro_F1", "Failure_Recall"]
            ).sort_values(
                by=["Balanced_Accuracy", "Macro_F1", "ROC_AUC"],
                ascending=False
            ).reset_index(drop=True)

            logging.info("\n" + results_df.to_string(index=False))

            # Save results CSV
            os.makedirs("artifacts", exist_ok=True)
            results_df.to_csv(self.config.results_path, index=False)

            # Best model selected for balanced class performance.
            best_model_name = results_df.loc[0, "Model"]
            best_roc_auc = float(results_df.loc[0, "ROC_AUC"])
            logging.info(
                f"Best model: {best_model_name}  "
                f"Balanced_Accuracy: {results_df.loc[0, 'Balanced_Accuracy']:.4f}  "
                f"Failure_Recall: {results_df.loc[0, 'Failure_Recall']:.4f}"
            )

            # Learn threshold on held-out validation split from training data.
            X_thr_train, X_thr_val, y_thr_train, y_thr_val = train_test_split(
                X_train,
                y_train,
                test_size=0.20,
                random_state=42,
                stratify=y_train
            )
            X_thr_train_scaled = scaler.transform(X_thr_train)
            X_thr_val_scaled = scaler.transform(X_thr_val)

            if best_model_name == "Support Vector Regression (SVR score)":
                threshold_model = SVR(C=5.0, gamma="scale", epsilon=0.05)
                threshold_model.fit(X_thr_train_scaled, y_thr_train)
                val_scores = threshold_model.predict(
                    X_thr_val_scaled).clip(0, 1)
            else:
                best_mode, fitted_best_model = models[best_model_name]
                threshold_model = clone(fitted_best_model)
                if best_mode == "scaled":
                    threshold_model.fit(X_thr_train_scaled, y_thr_train)
                    val_scores = get_model_scores(
                        threshold_model, X_thr_val_scaled)
                else:
                    threshold_model.fit(X_thr_train, y_thr_train)
                    val_scores = get_model_scores(threshold_model, X_thr_val)

            decision_threshold, threshold_metrics = tune_threshold(
                y_true=y_thr_val,
                y_score=val_scores,
                optimize_for="balanced_accuracy",
            )
            logging.info(
                f"Learned decision threshold: {decision_threshold:.3f} | "
                f"metrics={threshold_metrics}"
            )

            # Package everything needed for predict_pipeline
            model_package = {
                "best_model_name": best_model_name,
                "models":          models,          # all 4 classifiers
                "svr_model":       svr_model,        # trained SVR
                "scaler":          scaler,
                "X_columns":       X_columns,
                "preprocessor":    preprocessor,
                "decision_threshold": decision_threshold,
                "threshold_metrics": threshold_metrics,
            }
            save_object(self.config.model_path, model_package)

            logging.info("Model training completed")
            return best_model_name, best_roc_auc, results_df

        except Exception as e:
            raise CustomException(e, sys)
