import uuid
from typing import Dict, List, Tuple, Union, Optional

import lightgbm as lgb
import numpy as np
import pandas as pd

from aq_geometric.models.base_model import BaseModel
from aq_geometric.datasets.utilities.data.transforms import load_from_graph


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
        is_iterative: bool = False,
        include_masks_in_features: bool = False,
        include_masks_in_targets: bool = False,
        sample_graph: Optional[dict] = None,
        node_id_to_h3_index_map: Union[dict, None] = None,
        h3_index_to_node_id_map: Union[dict, None] = None,
        finest_resolution: int = 6,
        coarsest_resolution: int = -1,
        reshape_order: str = "F",
        lgbm_num_leaves: int = 31,
        lgbm_max_depth: int = -1,
        lgbm_learning_rate: float = 0.1,
        lgbm_n_estimators: int = 100,
        lgbm_objective: str = "regression",
        lgbm_model_filename: str = "lgbm_model.txt",
        lgbm_kwargs: Dict = {},           # Additional parameters for LightGBM
        lgbm_early_stopping_rounds: int = 10,
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
        self.num_edges_for_each_node = 1 + 6 + 1 + 7  # 1 self, 6 same resolution, 1 coarser resolution, 7 finer resolution
        self.reshape_order = reshape_order
        self.include_masks_in_features = include_masks_in_features
        self.include_masks_in_targets = include_masks_in_targets
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
        if self.include_masks_in_features:
            self.feature_vector_shape = (-1, 2 * self.num_edges_for_each_node *
                                         self.num_samples_in_node_feature *
                                         self.num_features_in_node_feature
                                         )  # account for mask
        else:
            self.feature_vector_shape = (-1, self.num_edges_for_each_node *
                                         self.num_samples_in_node_feature *
                                         self.num_features_in_node_feature)
        if self.include_masks_in_targets:
            self.target_vector_shape = (-1,
                                        2 * self.num_samples_in_node_target *
                                        self.num_features_in_node_target)
        else:
            self.target_vector_shape = (-1, self.num_samples_in_node_target *
                                        self.num_features_in_node_target)

        self.lgbm_kwargs = lgbm_kwargs
        self.lgbm_model = None
        self.lgbm_model_filename = lgbm_model_filename
        self.lgbm_early_stopping_rounds = lgbm_early_stopping_rounds

        # Set default LightGBM parameters (customize as needed)
        lgbm_kwargs["num_leaves"] = lgbm_num_leaves
        lgbm_kwargs["max_depth"] = lgbm_max_depth
        lgbm_kwargs["learning_rate"] = lgbm_learning_rate
        lgbm_kwargs["n_estimators"] = lgbm_n_estimators
        lgbm_kwargs["objective"] = lgbm_objective

    def fit(self, g: dict, val_data: Tuple[np.ndarray, np.ndarray], init_model=None):
        """Trains or fine-tunes the LightGBM model.

        Args:
            g (dict): The graph data for training.
            val_data (Tuple[np.ndarray, np.ndarray]): Validation data (X, y).
            init_model: An optional pre-trained LightGBM model for fine-tuning.
        """
        _, X, y = load_from_graph(
            graph=g,
            include_target=True,
            verbose=self.verbose,
            include_masks_in_targets=self.include_masks_in_targets,
            include_masks_in_features=self.include_masks_in_features,
            reshape_order=self.reshape_order,
            num_samples_in_node_feature=self.num_samples_in_node_feature,
            num_features_in_node_feature=self.num_features_in_node_feature,
            num_samples_in_node_target=self.num_samples_in_node_target,
            num_features_in_node_target=self.num_features_in_node_target,
        )

        if self.verbose:
            print(f"X_samples shape: {np.shape(X)}, y_samples shape: {np.shape(y)}")

        train_data = lgb.Dataset(X, label=y)
        val_data = lgb.Dataset(val_data[0], label=val_data[1])

        if init_model:
            self.lgbm_model = lgb.train(
                params=self.lgbm_kwargs,
                train_set=train_data,
                valid_sets=[train_data, val_data],
                early_stopping_rounds=self.lgbm_early_stopping_rounds,
                init_model=init_model,
                keep_training_booster=True,
            )
        else:
            self.lgbm_model = lgb.train(
                params=self.lgbm_kwargs,
                train_set=train_data,
                valid_sets=[train_data, val_data],
                early_stopping_rounds=self.lgbm_early_stopping_rounds,
            )

    def predict(self, g: dict) -> Tuple[np.ndarray, np.ndarray]:
        """Use the trained boosters to predict the target values for each feature in `g`."""
        assert self.lgbm_model is not None, "model must be trained before predicting"
        # obtain the inference data from `g`
        h3_indices, X = load_from_graph(
            graph=g,
            include_target=False,
            verbose=self.verbose,
            include_masks_in_targets=self.include_masks_in_targets,
            include_masks_in_features=self.include_masks_in_features,
            reshape_order=self.reshape_order,
            num_samples_in_node_feature=self.num_samples_in_node_feature,
            num_features_in_node_feature=self.num_features_in_node_feature,
            num_samples_in_node_target=self.num_samples_in_node_target,
            num_features_in_node_target=self.num_features_in_node_target,
            num_edges_for_each_node=self.num_edges_for_each_node,
        )

        if self.verbose:
            print(f"final X shape: {np.shape(X)}")

        prediction = self.lgbm_model.predict(X)

        # we need to reshape this prediction to n_h3_index, n_timestamps, n_targets
        prediction = np.reshape(prediction,
                                (-1, self.num_samples_in_node_target,
                                 self.num_features_in_node_target),
                                self.reshape_order)

        return h3_indices, prediction
    
    def save(self, path: str):
        """Saves the trained LightGBM model to a file.

        Args:
            path (str): The path to save the model to.
        
        Returns:
            None
        """
        assert self.lgbm_model is not None, "model must be trained before saving"
        self.lgbm_model.save_model(path)

    def export_to_onnx(self, path: str):
        """Exports the trained LightGBM model to ONNX format.

        Args:
            path (str): The path to save the ONNX model to.
        
        Returns:
            None
        """
        pass

    def load(self, path: str):
        """Loads a trained LightGBM model from a file.

        Args:
            path (str): The path to load the model from.

        Returns:
            None
        """
        self.lgbm_model = lgb.Booster(model_file=path)

    def get_feature_importances(self) -> pd.DataFrame:
        """Returns a DataFrame of feature importances."""
        assert self.lgbm_model is not None, "model must be trained before getting feature importances"
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