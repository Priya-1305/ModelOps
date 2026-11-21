from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


def evaluate_model_performance(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    target_names: list[str] = None
) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics for binary classification:
    - Accuracy
    - Precision (binary and weighted)
    - Recall (binary and weighted)
    - F1-score (binary and weighted)
    - ROC-AUC score
    - Confusion Matrix [ [TN, FP], [FN, TP] ]
    - Detailed classification report
    """
    target_names = target_names or ["malignant", "benign"]
    y_pred = model.predict(X)
    
    # Probabilities for positive class (1)
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X)[:, 1]
        try:
            roc_auc = float(roc_auc_score(y, y_proba))
        except Exception:
            roc_auc = 0.0
    else:
        y_proba = None
        roc_auc = 0.0

    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, average="binary", zero_division=0))
    rec = float(recall_score(y, y_pred, average="binary", zero_division=0))
    f1 = float(f1_score(y, y_pred, average="binary", zero_division=0))

    prec_weighted = float(precision_score(y, y_pred, average="weighted", zero_division=0))
    rec_weighted = float(recall_score(y, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y, y_pred).tolist()
    # cm is [[TN, FP], [FN, TP]] for binary classification
    tn, fp, fn, tp = int(cm[0][0]), int(cm[0][1]), int(cm[1][0]), int(cm[1][1])

    report = classification_report(y, y_pred, target_names=target_names, output_dict=True, zero_division=0)

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "precision_weighted": round(prec_weighted, 4),
        "recall_weighted": round(rec_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
        "confusion_matrix": {
            "matrix": cm,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
        },
        "sample_count": len(y),
        "classification_report": report,
    }
