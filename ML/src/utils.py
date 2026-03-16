"""
utils.py
────────
Shared helpers matching notebook logic exactly:
  - save_object / load_object
  - get_model_scores     (Cell 22)
  - get_confidence_band  (Cell 39)
  - build_models         (Cell 22)
  - train_model_suite    (Cell 22)
"""

import os
import sys
import time
import numpy as np
import dill

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, balanced_accuracy_score
)

from src.exception import CustomException
from src.logger import logging


# ── Save / Load ───────────────────────────────────────────────

def save_object(file_path: str, obj) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            dill.dump(obj, f)
        logging.info(f"Saved → {file_path}")
    except Exception as e:
        raise CustomException(e, sys)


def load_object(file_path: str):
    try:
        with open(file_path, "rb") as f:
            obj = dill.load(f)
        logging.info(f"Loaded ← {file_path}")
        return obj
    except Exception as e:
        raise CustomException(e, sys)


# ── get_model_scores  (mirrors Cell 22) ───────────────────────

def get_model_scores(model, X) -> np.ndarray:
    """
    Return continuous probability/score for ROC-AUC.
    Handles predict_proba, decision_function, plain predict.
    """
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        mn, mx = np.min(scores), np.max(scores)
        if mx - mn < 1e-12:
            return np.full_like(scores, 0.5, dtype=float)
        return (scores - mn) / (mx - mn)
    return model.predict(X).astype(float)


# ── Confidence band  (mirrors Cell 39) ───────────────────────

def get_confidence_band(prob: float) -> str:
    if prob >= 0.75:
        return "HIGH CONFIDENCE SUCCESS"
    elif prob >= 0.55:
        return "LIKELY SUCCESS"
    elif prob >= 0.45:
        return "UNCERTAIN"
    elif prob >= 0.25:
        return "LIKELY FAILURE"
    else:
        return "HIGH CONFIDENCE FAILURE"


# ── build_models  (mirrors Cell 22) ──────────────────────────

def build_models(y_train, n_train_rows: int, fast_mode: bool = True):
    """Exact copy of notebook build_models()."""
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import SVC, SVR, LinearSVC
        from xgboost import XGBClassifier

        y_arr = np.asarray(y_train)
        pos_count = int(np.sum(y_arr == 1))
        neg_count = int(np.sum(y_arr == 0))
        scale_pos_weight = float(neg_count / max(pos_count, 1))

        rf_trees = 120 if fast_mode else 300
        xgb_trees = 180 if fast_mode else 400

        models_local = {
            "Random Forest": (
                "raw",
                RandomForestClassifier(
                    n_estimators=rf_trees,
                    random_state=42,
                    n_jobs=-1,
                    class_weight="balanced"
                )
            ),
            "Logistic Regression": (
                "scaled",
                LogisticRegression(max_iter=2000, class_weight="balanced")
            ),
            "XGBoost": (
                "raw",
                XGBClassifier(
                    n_estimators=xgb_trees,
                    max_depth=6,
                    learning_rate=0.06,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    reg_lambda=1.0,
                    random_state=42,
                    eval_metric="logloss",
                    scale_pos_weight=scale_pos_weight,
                    n_jobs=-1
                )
            ),
        }

        # Switch to LinearSVC on large datasets (too slow otherwise)
        if n_train_rows > 60000 and fast_mode:
            models_local["Support Vector Machine (SVC)"] = (
                "scaled",
                LinearSVC(C=1.0, random_state=42, max_iter=5000,
                          class_weight="balanced")
            )
        else:
            models_local["Support Vector Machine (SVC)"] = (
                "scaled",
                SVC(kernel="rbf", C=2.0, gamma="scale",
                    probability=True, class_weight="balanced")
            )

        svr_local = SVR(C=5.0, gamma="scale", epsilon=0.05)
        return models_local, svr_local

    except Exception as e:
        raise CustomException(e, sys)


# ── train_model_suite  (mirrors Cell 22) ─────────────────────

def train_model_suite(
    X_train_raw, X_test_raw,
    X_train_scaled, X_test_scaled,
    y_train, y_test,
    tag: str = "dataset",
    fast_mode: bool = True
):
    """
    Train all 5 models + SVR, evaluate, return results.
    Exact mirror of notebook train_model_suite().
    """
    try:
        models_local, svr_local = build_models(
            y_train=y_train, n_train_rows=len(X_train_raw), fast_mode=fast_mode)
        results_local = []

        logging.info(f"Training suite: {tag}")
        print(f"\n===== Training suite: {tag} =====")
        t0 = time.time()

        for name, (mode, model) in models_local.items():
            start = time.time()
            print(f"Training: {name} ...", end=" ", flush=True)

            if mode == "scaled":
                model.fit(X_train_scaled, y_train)
                pred = model.predict(X_test_scaled)
                prob = get_model_scores(model, X_test_scaled)
            else:
                model.fit(X_train_raw, y_train)
                pred = model.predict(X_test_raw)
                prob = get_model_scores(model, X_test_raw)

            auc = roc_auc_score(y_test, prob)
            acc = accuracy_score(y_test, pred)
            prec = precision_score(y_test, pred, zero_division=0)
            rec = recall_score(y_test, pred, zero_division=0)
            f1 = f1_score(y_test, pred, zero_division=0)
            bal_acc = balanced_accuracy_score(y_test, pred)
            macro_f1 = f1_score(y_test, pred, average="macro", zero_division=0)
            failure_recall = recall_score(
                y_test, pred, pos_label=0, zero_division=0)
            results_local.append([
                name, acc, prec, rec, f1, auc, bal_acc, macro_f1, failure_recall
            ])
            print(f"AUC={auc:.4f}  time={time.time()-start:.1f}s")

        # SVR separately
        print("Training SVR ...", end=" ", flush=True)
        svr_start = time.time()
        svr_local.fit(X_train_scaled, y_train)
        svr_score = svr_local.predict(X_test_scaled)
        svr_score_clamped = np.clip(svr_score, 0, 1)
        svr_auc = roc_auc_score(y_test, svr_score_clamped)
        svr_pred = (svr_score_clamped >= 0.5).astype(int)
        results_local.append([
            "Support Vector Regression (SVR score)",
            accuracy_score(y_test, svr_pred),
            precision_score(y_test, svr_pred, zero_division=0),
            recall_score(y_test, svr_pred, zero_division=0),
            f1_score(y_test, svr_pred, zero_division=0),
            svr_auc,
            balanced_accuracy_score(y_test, svr_pred),
            f1_score(y_test, svr_pred, average="macro", zero_division=0),
            recall_score(y_test, svr_pred, pos_label=0, zero_division=0),
        ])
        print(f"AUC={svr_auc:.4f}  time={time.time()-svr_start:.1f}s")
        print(f"Suite '{tag}' completed in {time.time()-t0:.1f}s")
        logging.info(f"Suite '{tag}' done. Best checked externally.")

        return models_local, svr_local, results_local, svr_score_clamped, svr_auc

    except Exception as e:
        raise CustomException(e, sys)


def tune_threshold(y_true, y_score, optimize_for: str = "balanced_accuracy"):
    """
    Learn a decision threshold from validation scores instead of hardcoding 0.5.

    optimize_for supports:
      - balanced_accuracy (default)
      - macro_f1
    """
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score, dtype=float)

    if y_true.size == 0:
        return 0.5, {}

    thresholds = np.linspace(0.20, 0.80, 61)
    best_threshold = 0.5
    best_score = -1.0
    best_metrics = {}

    for thr in thresholds:
        pred = (y_score >= thr).astype(int)
        bal_acc = balanced_accuracy_score(y_true, pred)
        macro_f1 = f1_score(y_true, pred, average="macro", zero_division=0)
        failure_recall = recall_score(
            y_true, pred, pos_label=0, zero_division=0)
        success_recall = recall_score(
            y_true, pred, pos_label=1, zero_division=0)

        score = bal_acc if optimize_for == "balanced_accuracy" else macro_f1
        if (score > best_score) or (abs(score - best_score) < 1e-12 and abs(thr - 0.5) < abs(best_threshold - 0.5)):
            best_score = score
            best_threshold = float(thr)
            best_metrics = {
                "balanced_accuracy": float(bal_acc),
                "macro_f1": float(macro_f1),
                "failure_recall": float(failure_recall),
                "success_recall": float(success_recall),
            }

    return best_threshold, best_metrics
