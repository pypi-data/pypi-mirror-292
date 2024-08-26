import os
import random
from typing import Union, Optional, Tuple, List, Dict

import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data

from aq_geometric.models.base_model import BaseModel
from aq_geometric.datasets.adapters.torch.aq_geometric_dataset import TorchGeometricDatasetAdapter


class TorchBaseModelAdapter(BaseModel, torch.nn.Module):
    """
    Adapter class to provide PyTorch compatibility for BaseModel.
    """

    def __init__(self, *args, **kwargs):
        # Initialize both base classes
        BaseModel.__init__(self, *args, **kwargs)
        torch.nn.Module.__init__(self)

        self.transform_graph_fn = []
        self.inverse_transform_graph_fn = []
        self.inverse_transform_predictions_fn = []

    def forward(self, graph: Data) -> torch.Tensor:
        """
        Forward pass of the PyTorch model.
        (This method is required for torch.nn.Module)

        Args:
            graph (Data): The graph data object from torch_geometric.

        Returns:
            torch.Tensor: The model's output.
        """
        raise NotImplementedError("Forward pass not implemented in the base adapter.")

    def save(self, path: str):
        """Save the model to a file."""
        # ensure the model is on the CPU
        self.cpu()

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
            "state_dict": self.state_dict(),
            **self.kwargs
        }
        # save the model data
        torch.save(model_data, path)

    def load(self, path: str):
        """Load the model from a file."""
        # load the model data
        model_data = torch.load(path)

        # set the model data
        self.name = model_data["name"]
        self.guid = model_data["guid"]
        self.stations = model_data["stations"]
        self.features = model_data["features"]
        self.targets = model_data["targets"]
        self.num_samples_in_node_feature = model_data["num_samples_in_node_feature"]
        self.num_samples_in_node_target = model_data["num_samples_in_node_target"]
        self.num_features_in_node_feature = len(self.features)
        self.num_features_in_node_target = len(self.targets)
        self.is_iterative = model_data.get("is_iterative", False)  # for backwards compatibility

        self.load_state_dict(model_data["state_dict"])

        # set the kwargs
        for key, value in model_data.items():
            if key not in ["name", "guid", "stations", "features", "targets", "num_samples_in_node_feature", "num_samples_in_node_target", "num_features_in_node_feature", "num_features_in_node_target", "is_iterative", "state_dict"]:
                setattr(self, key, value)

    def fit(
        self,
        train_set: TorchGeometricDatasetAdapter,
        val_set: Optional[TorchGeometricDatasetAdapter],
        batch_size: int = 32,
        n_epoch: int = 20,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[torch.optim.lr_scheduler.ReduceLROnPlateau] = None,
        loss_fn: Optional[torch.nn.Module] = None,
        **kwargs
    ) -> None:
        """
        Trains or fine-tunes the model, handling either Dataset objects or iterators.
        
        Args:
            train_set (TorchGeometricDatasetAdapter): Training data.
            val_set (Optional[TorchGeometricDatasetAdapter]): Validation data.
            batch_size (int): Batch size for training.
            n_epoch (int): Number of training epochs.
            **kwargs: Additional training parameters (overrides defaults).
        """
        raise NotImplementedError("Training not implemented for the base model.")

    def predict(
        self,
        graph: Data,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Predicts target values for the given dataset using the trained model.

        Args:
            graph (torch_geometric.data.Data): The input graph for prediction.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing the h3_indices and the predictions.
        """
        raise NotImplementedError(
            "Prediction not implemented for the base model.")

    def evaluate(
        self,
        dataset: TorchGeometricDatasetAdapter,
        metrics: List[str] = ["rmse", "mae"],
    ) -> Dict[str, float]:
        """Evaluates the model on the given dataset.

        Args:
            dataset (Union[AqGeometricInMemoryDataset, AqGeometricDataset]): Dataset for evaluation.
            metrics (List[str]): List of evaluation metrics to compute (the names of functions from the aq_geometric.metrics.metrics module).

        Returns:
            Dict[str, float]: A dictionary containing the computed evaluation metrics.
        """
        raise NotImplementedError(
            "Evaluation not implemented for the base model.")

    def generate_forecasts(
        self,
        graph: Data,
        n_forecast_timesteps: int = 12,
        targets: Union[List[str], None] = None,
        verbose: Union[List[str], None] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate forecasts using the loaded model.
        
        Args:
            graph (torch_geometric.data.Data): The graph data dictionary.
            n_forecast_timesteps (int, optional): Number of timesteps to forecast.
            targets (List[str], optional): List of targets to predict. If None, uses self.targets.
            verbose (List[str], optional): Verbosity levels. If None, uses self.verbose.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing the forecasts for each target.
        """
        raise NotImplementedError(
            "generate_forecasts not implemented for the base model.")

    def transform_graph(self, graph: Data, *args, **kwargs) -> Data:
        """
        Transform the input graph data for the model.

        Args:
            graph (Data): The input graph data.

        Returns:
            Data: The transformed graph data.
        """
        for fn in self.transform_graph_fn:
            graph = fn(graph, *args, **kwargs)
        return graph

    def inverse_transform_graph(self, graph: Data, *args, **kwargs) -> Data:
        """
        Inverse transform the input graph data for the model.

        Args:
            graph (Data): The input graph data.

        Returns:
            Data: The inverse transformed graph data.
        """
        for fn in self.inverse_transform_graph_fn:
            graph = fn(graph, *args, **kwargs)
        return graph

    def inverse_transform_predictions(self, predictions: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Inverse transform the predictions.

        Args:
            predictions (torch.Tensor): The predictions to inverse transform.

        Returns:
            torch.Tensor: The inverse transformed predictions.
        """
        for fn in self.inverse_transform_predictions_fn:
            predictions = fn(predictions, *args, **kwargs)
        return predictions

    def shuffle_in_batches(self, iterable, batch_size=5):
        """This function batch-shuffles the iterable and returns it in batches of size batch_size."""
        batches = [[i for i in range(v, min(v+batch_size, len(iterable)))] for v in range(0, len(iterable), batch_size)]

        flattened_batches = [item for sublist in batches for item in sublist]
        random.shuffle(flattened_batches)

        # yield the shuffled elements in batches
        for i in range(0, len(flattened_batches), batch_size):
            yield flattened_batches[i:i+batch_size]
    