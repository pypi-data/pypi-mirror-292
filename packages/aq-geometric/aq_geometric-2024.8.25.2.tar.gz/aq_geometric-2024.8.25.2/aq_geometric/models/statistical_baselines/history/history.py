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


class AqGeometricHistoryModel(BaseModel):
    """This class is used to write the ground-truth values to the database using the BaseModel interface."""

    def __init__(
        self,
        name: str = "AqGeometricHistoryModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        num_samples_in_node_feature: int = 48,
        num_samples_in_node_target: int = 48,
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
        self.state_dict = None

    def fit(
        self,
        train_set: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
        val_set: Optional[Union[AqGeometricInMemoryDataset, AqGeometricDataset]],
        batch_size: int = 32,
        n_epoch: int = 20,
        **kwargs
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
        # we do not train a model, instead we save the train_set as the state_dict
        # so that we can write the historical data to the database in the same
        # format as the model predictions.
        pass

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
        h3_indices = graph["h3_index"]
        graph_data = graph["x"]
        graph_data_mask = graph["x_mask"]

        # apply the mask to graph_data
        graph_data[~graph_data_mask] = np.nan

        return h3_indices, graph_data

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
        raise NotImplementedError("This model copies the training data to the database, so it does not need to be evaluated.")

    def generate_forecasts(
        self,
        graph: dict,
        n_forecast_timesteps: int = 12,
        targets: Union[List[str], None] = None,
        verbose: Union[List[str], None] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Obtain the history for each feature from the `state_dict` (saved training dataset).
        
        Args:
            graph (dict): The graph data dictionary, not used.
            n_forecast_timesteps (int, optional): Number of timesteps to forecast, not used.
            targets (List[str], optional): List of targets to predict. If None, uses self.targets, not used.
            verbose (List[str], optional): Verbosity levels. If None, uses self.verbose.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing the history for each feature.
        """
        # this method does not actually generate forecasts, it just returns the input graphs
        # with the same format as the model predictions using the state_dict
        h3_indices = graph["h3_index"]
        feature_timestamps = graph["feature_timestamps"]
        feature_data = graph["x"]
        feature_data_mask = graph["x_mask"]

        # apply the mask to graph_data
        feature_data[~feature_data_mask] = np.nan

        # take only the last n_forecast_timesteps from the feature_timestamps
        feature_timestamps = feature_timestamps[-n_forecast_timesteps:]
        feature_data = feature_data[:, -n_forecast_timesteps:, :]

        timestamp_series = pd.Series(pd.to_datetime(feature_timestamps))

        if verbose:
            print(
                f"[{datetime.now()}] obtaining history for {len(h3_indices)} h3 indices and {len(timestamp_series)} timestamps"
            )

        # prepare the forecasts
        feature_dfs = {}
        for i, target in enumerate(self.features):
            
            if verbose:
                print(f"[{datetime.now()}] preparing history for {target}")
            
            history_df = pd.DataFrame(
                feature_data[:, :, i], columns=timestamp_series,
                index=h3_indices)
            
            if verbose:
                print(
                    f"[{datetime.now()}] history df shape for {target}: {history_df.shape}"
                )
            
            feature_dfs[target] = history_df
            
            if verbose:
                print(f"[{datetime.now()}] added DataFrame {history_df.shape}")

        return feature_dfs

    def eval(self):
        """We match the interface of other models."""
        pass

    def cpu(self):
        """We match the interface of other models."""
        pass

    def save(self, path: str):
        """Save the model to a file."""
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
