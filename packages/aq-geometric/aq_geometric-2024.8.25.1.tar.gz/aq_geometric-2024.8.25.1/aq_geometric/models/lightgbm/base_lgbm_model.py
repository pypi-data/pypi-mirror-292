import uuid
from typing import Callable, Dict, List, Tuple, Union, Optional

import lightgbm as lgb
import numpy as np
import pandas as pd

from aq_geometric.models.base_model import BaseModel
from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset
from aq_geometric.datasets.in_memory.aq_geometric_dataset import AqGeometricInMemoryDataset
from aq_geometric.datasets.adapters.numpy.aq_geometric_dataset import NumpyDatasetAdapter


class BaseAqGeometricLGBMModel(BaseModel):
    def __init__(
        self,
        name: str = "BaseAqGeometricLGBMModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        num_samples_in_node_feature: int = 48,
        num_samples_in_node_target: int = 12,
        is_iterative: bool = True,
        include_masks_in_features: bool = False,
        include_masks_in_targets: bool = False,
        sample_graph: Optional[dict] = None,
        node_id_to_h3_index_map: Union[dict, None] = None,
        h3_index_to_node_id_map: Union[dict, None] = None,
        finest_resolution: int = 6,
        coarsest_resolution: int = -1,
        reshape_order: str = "F",
        adapter_transform: Optional[Callable] = None,
        lgbm_model: Optional[Dict[str, Optional[lgb.Booster]]] = None,
        lgbm_num_leaves: int = 31,
        lgbm_max_depth: int = -1,
        lgbm_learning_rate: float = 0.1,
        lgbm_n_estimators: int = 100,
        lgbm_objective: str = "regression",
        lgbm_metric: str = "rmse",
        lgbm_num_boost_round: int = 100,
        lgbm_early_stopping_rounds: int = 10,
        lgbm_model_filename: str = "lgbm_model.txt",
        lgbm_kwargs: Dict = {},           # Additional parameters for LightGBM
        verbose: bool = False,
    ):
        assert reshape_order in ["C", "F",
                                 "A"], "reshape_order must be 'C', 'F', or 'A'"
        assert sample_graph is not None or (
            h3_index_to_node_id_map is not None
            and node_id_to_h3_index_map is not None
        ), "either `sample_graph` or `h3_index_to_node_id_map` and `node_id_to_h3_index_map` must be provided"

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
        self.finest_resolution = finest_resolution
        self.coarsest_resolution = coarsest_resolution
        self.num_features_in_node_feature = len(features)
        self.num_features_in_node_target = len(targets)
        self.include_masks_in_features = include_masks_in_features
        self.include_masks_in_targets = include_masks_in_targets
        self.reshape_order = reshape_order
        self.adapter_transform = adapter_transform
        self.verbose = verbose

        # process the sample graph to determine structure
        if sample_graph is not None:
            self.node_id_to_h3_index_map = {
                i: v
                for i, v in enumerate(sample_graph["h3_index"])
            }  # map node id to h3 index
            self.h3_index_to_node_id_map = {
                v: i
                for i, v in enumerate(sample_graph["h3_index"])
            }  # map h3 index to node id
        else:
            self.node_id_to_h3_index_map = node_id_to_h3_index_map
            self.h3_index_to_node_id_map = h3_index_to_node_id_map
        self.h3_indices = self.node_id_to_h3_index_map.values()
        if self.include_masks_in_features:
            self.feature_vector_shape = (-1, 2 * self.num_samples_in_node_feature *
                                         self.num_features_in_node_feature
                                         )  # account for mask
        else:
            self.feature_vector_shape = (-1, self.num_samples_in_node_feature *
                                         self.num_features_in_node_feature)
        if self.include_masks_in_targets:
            self.target_vector_shape = (-1, 2 * self.num_samples_in_node_target *
                                        self.num_features_in_node_target)
        else:
            self.target_vector_shape = (-1, self.num_samples_in_node_target *
                                        self.num_features_in_node_target)

        self.model = lgbm_model
        self.lgbm_kwargs = lgbm_kwargs
        self.lgbm_model_filename = lgbm_model_filename
        self.lgbm_early_stopping_rounds = lgbm_early_stopping_rounds
        self.lgbm_metric = lgbm_metric
        self.lgbm_num_boost_round = lgbm_num_boost_round


        # Set default LightGBM parameters (customize as needed)
        lgbm_kwargs["num_leaves"] = lgbm_num_leaves
        lgbm_kwargs["max_depth"] = lgbm_max_depth
        lgbm_kwargs["learning_rate"] = lgbm_learning_rate
        lgbm_kwargs["n_estimators"] = lgbm_n_estimators
        lgbm_kwargs["objective"] = lgbm_objective

    def fit(
        self, 
        train_set: Union[AqGeometricInMemoryDataset, AqGeometricDataset], 
        val_set: Union[AqGeometricInMemoryDataset, AqGeometricDataset], 
        batch_size: int = 32,
        num_boost_round: int = 100,
        **kwargs
    ) -> None:
        """
        Trains or fine-tunes the LightGBM model, handling either Dataset objects or iterators.

        Args:
            train_set Union[AqGeometricInMemoryDataset, AqGeometricDataset]: Training data.
            val_set Union[AqGeometricInMemoryDataset, AqGeometricDataset]: Validation data.
            num_boost_round (int): Maximum number of boosting iterations.
            early_stopping_rounds (int): Early stopping rounds.
            eval_metric (str): Evaluation metric for early stopping.
            verbose_eval (bool): Whether to print evaluation results.
            **kwargs: Additional LightGBM parameters (overrides defaults).
        """
        self.lgbm_kwargs.update(kwargs)

        if self.model is None:
            self.model = {t: None for t in self.targets}
        
        dataset_target_to_index_map = {v: i for i, v in enumerate(self.targets)}
        
        val_adapter = NumpyDatasetAdapter(val_set, batch_size=batch_size, transform=self.adapter_transform, verbose=self.verbose)
        val_iterator = val_adapter.get_dataset_iterator()
        train_adapter = NumpyDatasetAdapter(train_set, batch_size=batch_size, transform=self.adapter_transform, verbose=self.verbose)
        train_iterator = train_adapter.get_dataset_iterator()

        X_val, y_val = next(val_iterator, (None, None))

        for i, (X, y) in enumerate(train_iterator):

            X_data = X.reshape(X.shape[0], -1)  # ensure the input Data is 2-D with the correct number of rows
            X_val_data = X_val.reshape(X_val.shape[0], -1)

            for t in self.targets:
                y_data = y[:, :, dataset_target_to_index_map[t]].reshape(-1)
                y_val_data = y_val[:, :, dataset_target_to_index_map[t]].reshape(-1)

                print(f"for target {t} at iteration {i}, X has shape {X_data.shape}, y has shape {y_data.shape} X_val has shape {X_val_data.shape}, y_val has shape {y_val_data.shape}")

                train_set_lgb = lgb.Dataset(X_data, label=y_data)
                val_set_lgb = lgb.Dataset(X_val_data, label=y_val_data)

                # train or fine-tune model for target 't'
                self.model[t] = lgb.train(
                    params=self.lgbm_kwargs,
                    train_set=train_set_lgb,
                    num_boost_round=num_boost_round,
                    valid_sets=val_set_lgb,
                    init_model=self.model[t] if self.model[t] is not None else None,
                    keep_training_booster=True,
                )
            try:
                X_val, y_val = next(val_iterator)
            except (StopIteration, AssertionError):
                val_iterator = val_adapter.get_dataset_iterator()
                X_val, y_val = next(val_iterator, (None, None))
        
    def predict(
        self,
        dataset: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
        batch_size: int = 32
    ) -> dict:
        """Predicts target values for the given dataset using the trained model.

        Args:
            dataset (Union[AqGeometricInMemoryDataset, AqGeometricDataset]): Dataset for prediction.
            batch_size (int): Batch size for prediction.

        Returns:
            dict: A dictionary containing predictions for each target variable,
                where keys are target names and values are NumPy arrays of predictions.
        """
        predictions = {t: [] for t in self.targets}  # Initialize empty prediction dict
        data_generator = NumpyDatasetAdapter(
            dataset, batch_size=batch_size, transform=self.adapter_transform, verbose=self.verbose
        ).get_dataset_iterator()

        for X, _ in data_generator:
            X = X.reshape(X.shape[0], -1)  # enforce 2D with correct number of rows
            for t in self.targets:
                if self.model[t] is not None:
                    y_pred = self.model[t].predict(X)
                    predictions[t].extend(y_pred)

        # post-process predictions (e.g., reshaping) if needed
        for t in self.targets:
            predictions[t] = np.array(predictions[t]).reshape(
                -1, self.num_samples_in_node_target
            )

        return predictions

    def export_to_onnx(self, path: str):
        """Exports the trained LightGBM model to ONNX format.

        Args:
            path (str): The path to save the ONNX model to.
        
        Returns:
            None
        """
        pass

    def save_model(self, filename_prefix="models/model_"):
        """Saves the trained LightGBM models for each feature to separate files."""
        assert self.model is not None, "Model must be trained before saving"
        for feature, booster in self.model.items():
            booster.save_model(f"{filename_prefix}{feature}.txt")

    def load_model(self, filename_prefix="models/model_"):
        """Loads the trained LightGBM models for each feature from separate files."""
        self.model = {}  # Initialize an empty dictionary
        for feature in self.targets:
            try:
                self.model[feature] = lgb.Booster(model_file=f"{filename_prefix}{feature}.txt")
            except lgb.basic.LightGBMError:
                raise ValueError(f"feature '{feature}' must have a model file with prefix '{filename_prefix}' to load from path.")

    def get_feature_importance(self) -> pd.DataFrame:
        """Returns a DataFrame of feature importance."""
        assert self.lgbm_model is not None, "model must be trained before getting feature importance"
        return pd.DataFrame(
            self.lgbm_model.feature_importance(importance_type="gain"),
            columns=["importance"],
            index=self.features,
        )

    def generate_forecasts(
        self,
        graph: dict,
        targets: Union[List[str], None] = None,
        include_history: bool = False,
        verbose: Union[List[str], None] = None,
    ) -> Tuple[Dict[str, pd.DataFrame], np.ndarray, List[np.ndarray]]:
        """
        Generate forecasts using the model provided
        """
        raise NotImplementedError

    def _generate_forecasts_iterative(
        self,
        graph: dict,
        targets: Union[List[str], None] = None,
        include_history: bool = False,
        num_iterations: Union[
            int, None] = None,  # number of iterative forecasting rounds
        sample_freq: str = "1H",
        verbose: Union[List[str], None] = None,
    ) -> Tuple[Dict[str, pd.DataFrame], np.ndarray, List[np.ndarray]]:
        """
        Generate forecasts iteratively using the model provided
        """
        raise NotImplementedError

    def _generate_forecasts_direct(
        self,
        graph: dict,
        targets: Union[List[str], None] = None,
        include_history: bool = False,
        verbose: Union[List[str], None] = None,
    ) -> Tuple[Dict[str, pd.DataFrame], np.ndarray, List[np.ndarray]]:
        """
        Generate forecasts directly using the model provided
        """
        raise NotImplementedError