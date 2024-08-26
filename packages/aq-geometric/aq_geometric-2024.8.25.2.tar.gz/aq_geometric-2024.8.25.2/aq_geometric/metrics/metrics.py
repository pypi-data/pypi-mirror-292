from typing import Callable, Tuple, Union, Optional

import numpy as np


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    null_model_pred: Optional[np.ndarray] = None,
    metrics: Optional[list[str]] = None,
) -> dict:
    """Calculates a set of metrics for two model predictions."""
    if metrics is None:
        metrics = [
            "mae",
            "rmse",
            "r2_score"
        ]

    y_true_filtered, y_pred_filtered, null_model_pred_filtered = _filter_missing_values(y_true, y_pred, null_model_pred)

    results = {}
    for metric in metrics:
        if metric == "mae":
            results[metric] = mean_absolute_error(y_true_filtered, y_pred_filtered)
        elif metric == "mse":
            results[metric] = mean_squared_error(y_true_filtered, y_pred_filtered)
        elif metric == "rmse":
            results[metric] = root_mean_squared_error(y_true_filtered, y_pred_filtered)
        elif metric == "mape":
            results[metric] = mean_absolute_percentage_error(y_true_filtered, y_pred_filtered)
        elif metric == "smape":
            results[metric] = symmetric_mean_absolute_percentage_error(y_true_filtered, y_pred_filtered)
        elif metric == "msle":
            results[metric] = mean_squared_log_error(y_true_filtered, y_pred_filtered)
        elif metric == "r2_score":
            results[metric] = r2_score(y_true_filtered, y_pred_filtered)
        elif metric == "me":
            results[metric] = mean_error(y_true_filtered, y_pred_filtered)
        elif metric == "mpe":
            results[metric] = mean_percentage_error(y_true_filtered, y_pred_filtered)
        elif metric == "nmse":
            results[metric] = normalized_mean_squared_error(y_true_filtered, y_pred_filtered, null_model_pred_filtered)
        elif metric == "ia":
            results[metric] = index_agreement(y_true_filtered, y_pred_filtered, null_model_pred_filtered)
        elif metric == "mss":
            results[metric] = mean_skill_score(y_true_filtered, y_pred_filtered, null_model_pred_filtered)
        else:
            raise ValueError(f"Invalid metric: {metric}")

    return results


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean absolute error (MAE)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean(np.abs(y_true_filtered - y_pred_filtered))


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean squared error (MSE)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean(np.square(y_true_filtered - y_pred_filtered))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the root mean squared error (RMSE)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.sqrt(mean_squared_error(y_true_filtered, y_pred_filtered))


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean absolute percentage error (MAPE)."""
    epsilon = np.finfo(np.float64).eps
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean(np.abs((y_true_filtered - y_pred_filtered) / (y_true_filtered + epsilon))) * 100


def symmetric_mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the symmetric mean absolute percentage error (SMAPE)."""
    epsilon = np.finfo(np.float64).eps
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return 100/len(y_true_filtered) * np.sum(2 * np.abs(y_pred_filtered - y_true_filtered) / (np.abs(y_true_filtered) + np.abs(y_pred_filtered) + epsilon))


def mean_squared_log_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean squared logarithmic error (MSLE)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean(np.square(np.log(y_true_filtered + 1) - np.log(y_pred_filtered + 1)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the R-squared (coefficient of determination)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    ss_res = np.sum(np.square(y_true_filtered - y_pred_filtered))
    ss_tot = np.sum(np.square(y_true_filtered - np.mean(y_true_filtered)))
    return 1 - (ss_res / ss_tot)


def mean_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean error (ME)."""
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean(y_pred_filtered - y_true_filtered)


def mean_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the mean percentage error (MPE)."""
    epsilon = np.finfo(np.float64).eps
    y_true_filtered, y_pred_filtered = _filter_missing_values(y_true, y_pred)

    return np.mean((y_true_filtered - y_pred_filtered) / (y_true_filtered + epsilon)) * 100


def normalized_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray, null_model_pred: np.ndarray) -> float:
    """Calculates the normalized mean squared error (NMSE)."""
    y_true_filtered, y_pred_filtered, null_model_pred_filtered = _filter_missing_values(y_true, y_pred, null_model_pred)

    mse = mean_squared_error(y_true_filtered, y_pred_filtered)
    mse_null = mean_squared_error(y_true_filtered, null_model_pred_filtered)
    return mse / mse_null


def index_agreement(y_true: np.ndarray, y_pred: np.ndarray, null_model_pred: np.ndarray) -> float:
    """Calculates the index of agreement (d) between two model predictions."""
    y_true_filtered, y_pred_filtered, null_model_pred_filtered = _filter_missing_values(y_true, y_pred, null_model_pred)

    d1 = 1 - np.sum(np.square(y_true_filtered - y_pred_filtered)) / np.sum(np.square(np.abs(y_pred_filtered - np.mean(y_true_filtered)) + np.abs(y_true_filtered - np.mean(y_true_filtered))))
    d2 = 1 - np.sum(np.square(y_true_filtered - null_model_pred_filtered)) / np.sum(np.square(np.abs(null_model_pred_filtered - np.mean(y_true_filtered)) + np.abs(y_true_filtered - np.mean(y_true_filtered))))
    return d1 - d2


def mean_skill_score(y_true: np.ndarray, y_pred: np.ndarray, null_model_pred: np.ndarray, metric_func: Callable = mean_squared_error) -> float:
    """Calculates the mean skill score (MSS) for two models using a specified metric function."""
    y_true_filtered, y_pred_filtered, null_model_pred_filtered = _filter_missing_values(y_true, y_pred, null_model_pred)

    skill_scores = []
    for i in range(len(y_true_filtered)):
        error1 = metric_func(y_true_filtered[i], y_pred_filtered[i])
        error2 = metric_func(y_true_filtered[i], null_model_pred_filtered[i])
        if error2 > 0:
            skill_score = 1 - (error1 / error2)
            skill_scores.append(skill_score)
    return np.mean(skill_scores)


def skill_score(y_true, y_pred, null_model_pred, metric_func: Callable = mean_squared_error):
    """Calculates the skill score (SS) for two models using a specified metric function."""
    return 1 - (metric_func(y_true, y_pred) / metric_func(y_true, null_model_pred))


def _filter_missing_values(y_true: np.ndarray, y_pred: np.ndarray, null_model_pred: Optional[np.ndarray] = None) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Filter the input arrays to remove missing values."""
    if null_model_pred is None:
        mask = ~np.isnan(y_true) & ~np.isnan(y_pred)

        y_true_filtered = y_true[mask]
        y_pred_filtered = y_pred[mask]

        return y_true_filtered, y_pred_filtered
    else:
        mask = ~np.isnan(y_true) & ~np.isnan(y_pred) & ~np.isnan(null_model_pred)

        y_true_filtered = y_true[mask]
        y_pred_filtered = y_pred[mask]
        null_model_pred_filtered = null_model_pred[mask]

        return y_true_filtered, y_pred_filtered, null_model_pred_filtered
