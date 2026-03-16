"""
train_pipeline.py
─────────────────
Runs the full training pipeline end-to-end:
  DataIngestion → DataTransformation → ModelTrainer

Usage:
    python -m src.pipeline.train_pipeline
    # or called from FastAPI: POST /api/train
"""

import sys
from src.exception import CustomException
from src.logger import logging

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer


class TrainPipeline:
    def run(self):
        """
        Execute full ML pipeline.

        Returns
        -------
        dict with keys:
            best_model_name, best_roc_auc, results_df,
            train_shape, test_shape
        """
        try:
            logging.info("══════════════════════════════════")
            logging.info("   TRAIN PIPELINE STARTED         ")
            logging.info("══════════════════════════════════")

            # ── Step 1: Data Ingestion ────────────────────────
            logging.info("Step 1/3 → Data Ingestion")
            ingestion = DataIngestion()
            train_path, test_path, country_df = ingestion.initiate_data_ingestion()

            # ── Step 2: Data Transformation ───────────────────
            logging.info("Step 2/3 → Data Transformation")
            transformation = DataTransformation()
            (X_train, X_test,
             y_train, y_test,
             X_train_scaled, X_test_scaled,
             scaler,
             preprocessor_path) = transformation.initiate_data_transformation(
                train_path, test_path
            )

            # Save country_df into preprocessor so predict_pipeline can use it
            from src.utils import load_object, save_object
            preprocessor = load_object(preprocessor_path)
            preprocessor["country_df"] = country_df
            save_object(preprocessor_path, preprocessor)

            # ── Step 3: Model Training ─────────────────────────
            logging.info("Step 3/3 → Model Training")
            trainer = ModelTrainer()
            best_model_name, best_roc_auc, results_df = trainer.initiate_model_training(
                X_train, X_test,
                y_train, y_test,
                preprocessor_path
            )

            logging.info("══════════════════════════════════")
            logging.info(f"   TRAINING COMPLETE              ")
            logging.info(f"   Best Model : {best_model_name}")
            logging.info(f"   ROC-AUC    : {best_roc_auc:.4f}")
            logging.info(f"   Train rows : {X_train.shape[0]:,}")
            logging.info(f"   Features   : {X_train.shape[1]}")
            logging.info("══════════════════════════════════")

            return {
                "best_model_name": best_model_name,
                "best_roc_auc":    best_roc_auc,
                "results_df":      results_df,
                "train_shape":     X_train.shape,
                "test_shape":      X_test.shape,
            }

        except Exception as e:
            raise CustomException(e, sys)


# ── Run directly ───────────────────────────────────────────────
if __name__ == "__main__":
    pipeline = TrainPipeline()
    result = pipeline.run()

    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)
    print(f"Best Model : {result['best_model_name']}")
    print(f"ROC-AUC    : {result['best_roc_auc']:.4f}")
    print(f"Train rows : {result['train_shape'][0]:,}")
    print(f"Features   : {result['train_shape'][1]}")
    print("\nAll model results:")
    print(result["results_df"].to_string(index=False))
