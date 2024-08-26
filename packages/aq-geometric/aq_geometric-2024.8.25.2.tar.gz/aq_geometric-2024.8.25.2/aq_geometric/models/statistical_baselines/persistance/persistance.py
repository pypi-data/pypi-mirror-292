import os
import pickle
from datetime import datetime
from typing import Dict, List, Tuple, Union, Optional

import uuid
import numpy as np
import pandas as pd

from aq_geometric.models.base_model import BaseModel
from aq_geometric.datasets.in_memory.aq_geometric_dataset import AqGeometricInMemoryDataset
from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset
import aq_geometric.metrics.metrics as aq_metrics


class AqGeometricPersistanceModel(BaseModel):
    def __init__(
        self,
        name: str = "AqGeometricPersistanceModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        num_samples_in_node_feature: int = 48,
        num_samples_in_node_target: int = 12,
        is_iterative: bool = False,
        verbose: bool = False,
    ):
        super().__init__(
            name=name,
            guid=guid,
            stations=stations,
            features=features,
            targets=targets,
            num_samples_in_node_feature=num_samples_in_node_feature,
            num_samples_in_node_target=num_samples_in_node_target,
            is_iterative=is_iterative,
        )
        self.num_features_in_node_feature = len(features)
        self.num_features_in_node_target = len(targets)
        self.verbose = verbose
        self.last_training_obs = None

    def fit(
        self,
        train_set: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
        val_set: Optional[Union[AqGeometricInMemoryDataset, AqGeometricDataset]],
        batch_size: int = 32,
        n_epoch: int = 20,
        **kwargs,
    ) -> None:
        """
        Trains or fine-tunes the model, handling either Dataset objects or iterators.
        
        Args:
            train_set (Union[AqGeometricInMemoryDataset, AqGeometricDataset]): Training data.
            val_set (Optional[Union[AqGeometricInMemoryDataset, AqGeometricDataset]]): Validation data.
            batch_size (int): Batch size for training.
            n_epoch (int): Number of training epochs.
            **kwargs: Additional training parameters (overrides defaults).
        """
        g = train_set.get(len(train_set)-1)
        graph_data = g["x"]
        last_training_obs = graph_data[:, -1:, :]  # (n_h3_index, 1, n_targets)
        last_training_h3_index = g["h3_index"]

        if self.verbose:
            print(f"last_training_obs shape: {np.shape(last_training_obs)}")

        self.state_dict = {
            "last_training_obs": last_training_obs,
            "last_training_h3_index": last_training_h3_index,
        }

    def predict(
        self,
        graph: dict,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Predicts target values for the given dataset using the trained model.

        Args:
            graph (dict): The input graph for prediction.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing the h3_indices and the predictions.
        """
        assert self.state_dict is not None, "model must be trained before predicting"

        valid_h3_indices = self.state_dict["last_training_h3_index"]
        pred_data = self.state_dict["last_training_obs"]

        h3_indices = graph["h3_index"]
        target_timestamps = graph["target_timestamps"]

        # repeat pred_data len(target_timesamps) times
        pred = np.repeat(pred_data, len(target_timestamps), axis=1)

        if self.verbose:
            print(
                f"[{datetime.now()}] before re-indexing to h3_index, predictions has shape {pred.shape}"
            )

        # ensure we match the input h3_indecies
        preds_dfs = []
        for i in range(len(self.targets)):
            tmp = pd.DataFrame(pred[:, :, i], columns=target_timestamps,
                               index=valid_h3_indices)
            tmp = tmp.join(
                pd.DataFrame(h3_indices,
                             columns=["h3_index"]).set_index("h3_index"),
                how="right")
            preds_dfs.append(tmp)
        pred = np.stack([p.to_numpy() for p in preds_dfs], axis=2)

        if self.verbose:
            print(
                f"[{datetime.now()}] after re-indexing to h3_index, predictions has shape {pred.shape}"
            )

        return h3_indices, pred

    def evaluate(
        self,
        dataset: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
        metrics: List[str] = ["root_mean_squared_error", "mean_absolute_error"],
    ) -> Dict[str, float]:
        """Evaluates the model on the given dataset.

        Args:
            dataset (Union[AqGeometricInMemoryDataset, AqGeometricDataset]): Dataset for evaluation.
            metrics (List[str]): List of evaluation metrics to compute (the names of functions from the aq_geometric.metrics.metrics module).

        Returns:
            Dict[str, List[float]]: A dictionary containing the computed evaluation metrics for each graph in the dataset.
        """
        assert self.state_dict is not None, "model must be trained before evaluating"

        evaluation_results = {t: {m: [] for m in metrics} for t in self.targets}
        metric_fns = {m: getattr(aq_metrics, m) for m in metrics}

        for i in dataset.indices:
            g = dataset.get(i)
            h3_index = g["h3_index"]
            y = g["y"]
            y_mask = g["y_mask"]

            pred_h3_index, pred = self.predict(g)

            # align model_h3_index with h3_index
            pred_aligned = np.zeros_like(y)  
            for i, h3idx in enumerate(h3_index):
                if h3idx in pred_h3_index:
                    model_idx = np.where(pred_h3_index == h3idx)[0][0]
                    pred_aligned[i] = pred[model_idx]

            if y_mask.shape != pred_aligned.shape:
                raise ValueError("The shapes of the true mask and predictions are mismatched")            

            for i, t in enumerate(self.targets):
                y_masked = y[:, :, i][y_mask[:, :, i]]
                pred_masked = pred_aligned[:, :, i][y_mask[:, :, i]]
                for m in metrics:
                    evaluation_results[t][m].append(
                        metric_fns[m](y_masked, pred_masked)  # Calculate metric on masked values
                    )

        return evaluation_results

    def generate_forecasts(
        self,
        graph: dict,
        n_forecast_timesteps: int = 12,
        targets: Union[List[str], None] = None,
        verbose: Union[List[str], None] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate forecasts using the loaded model.
        
        Args:
            graph (dict): The graph data dictionary.
            n_forecast_timesteps (int, optional): Number of timesteps to forecast.
            targets (List[str], optional): List of targets to predict. If None, uses self.targets.
            verbose (List[str], optional): Verbosity levels. If None, uses self.verbose.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing the forecasts for each target.
        """
        return self._generate_forecasts_direct(
            graph=graph,
            n_forecast_timesteps=n_forecast_timesteps,
            targets=targets if targets is not None else self.targets,
            verbose=verbose if verbose is not None else self.verbose)

    def _generate_forecasts_direct(
        self,
        graph: dict,
        n_forecast_timesteps: int = 12,
        targets: Union[List[str], None] = None,
        verbose: Union[List[str], None] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate forecasts using the loaded model.
        
        Args:
            graph (dict): The graph data dictionary.
            n_forecast_timesteps (int, optional): Number of timesteps to forecast.
            targets (List[str], optional): List of targets to predict. If None, uses self.targets.
            verbose (List[str], optional): Verbosity levels. If None, uses self.verbose.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing the forecasts for each target.
        """
        h3_indices = graph["h3_index"]
        target_timestamps = graph["target_timestamps"]
        
        series = pd.Series(pd.to_datetime(target_timestamps))
        inferred_freq = pd.infer_freq(series)
        
        timestamps = pd.date_range(start=series[0], periods=n_forecast_timesteps, freq=inferred_freq)

        if verbose:
            print(
                f"[{datetime.now()}] generating forecasts for {len(h3_indices)} h3 indices and {len(timestamps)} timestamps"
            )

        graph["target_timestamps"] = timestamps
        valid_h3_indices, preds = self.predict(graph)

        if verbose:
            print(
                f"[{datetime.now()}] model generating forecasts for {len(valid_h3_indices)} valid h3 indices and {len(timestamps)} timestamps"
            )

        # prepare the forecasts
        target_dfs = {}
        for i, target in enumerate(targets):
            
            if verbose:
                print(f"[{datetime.now()}] preparing forecast for {target}")
            
            forecast_df = pd.DataFrame(
                preds[:, :, i], columns=target_timestamps,
                index=valid_h3_indices)
            
            if verbose:
                print(
                    f"[{datetime.now()}] forecast df shape for {target}: {forecast_df.shape}"
                )
            
            target_dfs[target] = forecast_df
            
            if verbose:
                print(f"[{datetime.now()}] added DataFrame {forecast_df.shape}")

        return target_dfs

    def eval(self):
        """We match the interface of other models."""
        pass

    def cpu(self):
        """We match the interface of other models."""
        pass

    def save(self, path: str):
        """Save the model to a file."""
        assert self.state_dict is not None, "model must be trained before saving"

        # ensure the path exists
        # check if the path has a directory
        if os.path.dirname(path):
            # create the directory if it does not exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

        # gather the model data
        model_data = {
            "name": self.name,
            "guid": self.guid,
            "stations": self.stations,
            "features": self.features,
            "targets": self.targets,
            "num_samples_in_node_feature": self.num_samples_in_node_feature,
            "num_samples_in_node_target": self.num_samples_in_node_target,
            "is_iterative": self.is_iterative,
            "state_dict": self.state_dict,
            **self.kwargs
        }
        # save the model data
        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    def load(self, path: str):
        """Load the model from a file."""
        # load the model data
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        # set the model data
        self.name = model_data["name"]
        self.guid = model_data["guid"]
        self.stations = model_data["stations"]
        self.features = model_data["features"]
        self.targets = model_data["targets"]
        self.num_samples_in_node_feature = model_data[
            "num_samples_in_node_feature"]
        self.num_samples_in_node_target = model_data[
            "num_samples_in_node_target"]
        self.num_features_in_node_feature = len(self.features)
        self.num_features_in_node_target = len(self.targets)
        self.is_iterative = model_data.get(
            "is_iterative", False)  # for backwards compatibility
        self.load_state_dict(model_data["state_dict"])

        # set the kwargs
        for key, value in model_data.items():
            if key not in [
                    "name", "guid", "stations", "features", "targets",
                    "num_samples_in_node_feature",
                    "num_samples_in_node_target",
                    "num_features_in_node_feature",
                    "num_features_in_node_target", "is_iterative", "state_dict"
            ]:
                setattr(self, key, value)

    def load_state_dict(self, state_dict: Dict):
        """We match the interface of other models."""
        self.state_dict = state_dict
