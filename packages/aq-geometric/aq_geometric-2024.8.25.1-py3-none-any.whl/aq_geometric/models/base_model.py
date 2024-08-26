from datetime import datetime
from typing import Tuple, Dict, Union, List, Optional

import numpy as np
import pandas as pd

from aq_utilities.data import hourly_predictions_to_postgres

from aq_geometric.datasets.in_memory.aq_geometric_dataset import AqGeometricInMemoryDataset
from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset


class BaseModel:
    """
    Base class for all models.
    
    This class handles model metadata, saving/loading, and prediction result 
    processing. It's designed to be framework-agnostic.
    """
    def __init__(self, name: str = "BaseModel",
                 guid: str = "00000000-0000-0000-0000-000000000000",
                 stations: Union[List, None] = None, features: List[str] = [],
                 targets: List[str] = [],
                 num_samples_in_node_feature: int = -1,
                 num_samples_in_node_target: int = -1,
                 is_iterative: bool = False, **kwargs):
        self.name = name
        self.guid = guid
        self.stations = stations
        self.features = features
        self.targets = targets
        self.num_samples_in_node_feature = num_samples_in_node_feature
        self.num_samples_in_node_target = num_samples_in_node_target
        self.num_features_in_node_feature = len(self.features)
        self.num_features_in_node_target = len(self.targets)
        self.is_iterative = is_iterative
        self.kwargs = kwargs

    def save(self, path: str):
        """Save model metadata to a file. (Implementation will depend on the specific model type.)"""
        raise NotImplementedError("Saving not implemented for the base model.")

    def load(self, path: str):
        """Load model metadata from a file. (Implementation will depend on the specific model type.)"""
        raise NotImplementedError(
            "Loading not implemented for the base model.")

    def export_to_onnx(self, path: str):
        """Export the model to ONNX format. (Implementation will depend on the specific model type.)"""
        raise NotImplementedError(
            "Exporting to ONNX not implemented for the base model.")

    def __repr__(self):
        """Use the torch default representation, add new attrs."""
        representation = super().__repr__()

        # add new lines with the name, guid, and stations
        representation += f"\nName: {self.name}"
        representation += f"\nGUID: {self.guid}"
        representation += f"\nStations: {self.stations}"
        representation += f"\nFeatures: {self.features}"
        representation += f"\nTargets: {self.targets}"
        representation += f"\nIs iterative: {self.is_iterative}"
        representation += f"\nNum samples in node feature: {self.num_samples_in_node_feature}"
        representation += f"\nNum samples in node target: {self.num_samples_in_node_target}"
        representation += f"\nNum features in node feature: {self.num_features_in_node_feature}"
        representation += f"\nNum features in node target: {self.num_features_in_node_target}"

        return representation

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
        raise NotImplementedError("Training not implemented for the base model.")

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
        raise NotImplementedError(
            "Prediction not implemented for the base model.")

    def evaluate(
        self,
        dataset: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
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
        raise NotImplementedError(
            "generate_forecasts not implemented for the base model.")

    def forecasts_to_db(
        self,
        engine: "sqlalchemy.engine.Engine",
        target_dfs: Dict[str, pd.DataFrame],
        run_id: Optional[str] = None,
        predicted_at_timestamp_override: Optional[datetime] = None,
        chunksize: int = 1000,
        continue_on_error: bool = False,
        verbose: bool = False,
    ) -> int:
        """Write the forecasts to the database.

        Args:
            engine (sqlalchemy.engine.Engine): The database engine.
            target_dfs (Dict[str, pd.DataFrame]): A dictionary of forecasts for each target.
            run_id (str, optional): The run ID for the forecasts.
            predicted_at_timestamp_override (datetime, optional): The predicted at timestamp for the forecasts.
            chunksize (int, optional): The chunk size for writing to the database.
            continue_on_error (bool, optional): Whether to continue writing to the database if an error occurs.
            verbose (bool, optional): Whether to print verbose output.

        Returns:
            int: 0 if successful, 1 if an error occurred.
        """
        # generate a random run id if none is provided
        if run_id is None:
            import uuid
            run_id = str(uuid.uuid4())

        # obtain model attributes
        model_id = self.guid
        model_name = self.name

        for target, forecast_df in target_dfs.items():
            if verbose:
                print(
                    f"[{datetime.now()}] writing forecast for {target} to database"
                )

            # obtain the timestamps
            timestamps = forecast_df.columns.to_list()
            data = forecast_df.values
            h3_indices = forecast_df.index
            predicted_at_timestamp = datetime.utcnow().replace(minute=0, second=0, microsecond=0) if not predicted_at_timestamp_override else predicted_at_timestamp_override

            # prepare the data
            for i, timestamp in enumerate(timestamps):
                df = pd.DataFrame()
                df["h3_index"] = h3_indices
                df["value"] = data[:, i]
                df["timestamp"] = timestamp
                df["predicted_at_timestamp"] = predicted_at_timestamp
                df["model_id"] = model_id
                df["model_name"] = model_name
                df["run_id"] = run_id
                df["measurement"] = target

                if verbose:
                    print(
                        f"[{datetime.now()}] prepared forecast df of shape {df.shape} for timestamp {timestamp} [{i+1} of {len(timestamps)}]"
                    )
                
                df.dropna(inplace=True)

                if verbose:
                    print(
                        f"[{datetime.now()}] after removing missing measurements df has shape {df.shape} for timestamp {timestamp} [{i+1} of {len(timestamps)}]"
                    )

                # write the predictions to postgres
                err = hourly_predictions_to_postgres(
                    predictions=df, engine=engine,
                    chunksize=chunksize, verbose=self.verbose if hasattr(
                        self, "verbose") else verbose)

                if verbose:
                    print(
                        f"[{datetime.now()}] write operation obtained status {err} [{i+1} of {len(timestamps)}]"
                    )

                if err == 1:
                    print(f"failed to write predictions to postgres: {err}")
                    if continue_on_error: continue
                    else: return 1

        return 0
