import copy
from datetime import datetime
from typing import List, Union, Callable, Dict

import numpy as np
import pandas as pd

from aq_utilities.engine.psql import get_engine
from aq_utilities.data import filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon
from aq_geometric.data.graph.graphs_builder import GraphsBuilder

class AqGeometricInMemoryDataset:
    def __init__(
            self,
            features: List[str] = ["PM2.5"], targets: List[str] = [
                "OZONE"
            ], start_time: str = "2023-01-01", end_time: str = "2023-01-15",
            freq: str = "1H", samples_in_node_features: int = 24,
            samples_in_node_targets: int = 24,
            time_closed_interval: bool = False,
            engine: Union["sqlalchemy.engine.Engine", None] = None,
            engine_kwargs: Dict = {}, selected_aqsids: Union[List[str],
                                                             None] = None,
            stations_info_fp: Union[str, None] = None,
            selected_h3_indices: Union[List[str], None] = None,
            stations_info_filters: List[Callable] = [
                filter_aqsids,
                round_station_lat_lon,
                filter_lat_lon,
                remove_duplicate_aqsid,
                remove_duplicate_lat_lon,
            ], min_h3_resolution: int = 0, leaf_h3_resolution: Union[int,
                                                                     None] = 6,
            max_h3_resolution: int = 12, include_root_node: bool = True,
            compute_edges: bool = True, make_undirected: bool = True,
            include_self_loops: bool = True, with_edge_features: bool = True,
            min_to_root_edge_distance: float = 0.0,
            node_missing_value: float = np.nan, verbose: bool = False):
        self.engine = engine if engine is not None else get_engine(
            **engine_kwargs)
        self.features = features
        self.targets = targets
        self.start_time = start_time
        self.end_time = end_time
        self.freq = freq
        self.time_closed_interval = time_closed_interval
        self.num_samples_in_node_features = samples_in_node_features
        self.num_samples_in_node_targets = samples_in_node_targets
        self.stations_info_fp = stations_info_fp
        self.selected_aqsids = selected_aqsids
        self.stations_info_filters = stations_info_filters
        self.selected_h3_indices = selected_h3_indices
        self.min_h3_resolution = min_h3_resolution
        self.leaf_h3_resolution = leaf_h3_resolution
        self.max_h3_resolution = max_h3_resolution
        self.include_root_node = include_root_node
        self.compute_edges = compute_edges
        self.make_undirected = make_undirected
        self.include_self_loops = include_self_loops
        self.with_edge_features = with_edge_features
        self.min_to_root_edge_distance = min_to_root_edge_distance
        self.node_missing_value = node_missing_value
        self.verbose = verbose

        # prepare graph data in memory
        self._graph_data = GraphsBuilder(
            engine=self.engine, stations_info_fp=self.stations_info_fp,
            features=self.features, targets=self.targets,
            start_time=self.start_time, end_time=self.end_time, freq=self.freq,
            time_closed_interval=self.time_closed_interval,
            selected_aqsids=self.selected_aqsids,
            stations_info_filters=self.stations_info_filters,
            selected_h3_indices=self.selected_h3_indices,
            min_h3_resolution=self.min_h3_resolution,
            leaf_h3_resolution=self.leaf_h3_resolution,
            max_h3_resolution=self.max_h3_resolution,
            include_root_node=self.include_root_node,
            compute_edges=self.compute_edges,
            make_undirected=self.make_undirected,
            include_self_loops=self.include_self_loops,
            with_edge_features=self.with_edge_features,
            min_to_root_edge_distance=self.min_to_root_edge_distance,
            node_missing_value=self.node_missing_value,
            verbose=self.verbose
        ).export_as_graph()

        # obtain the timestamps for the features and targets
        self.timestamps = self._graph_data["timestamps"]
        # determine the start and end times and index ranges for the graph
        self.graph_feature_start_timestamps = self.timestamps[
            0:-self.num_samples_in_node_targets]
        self.graph_target_start_timestamps = self.timestamps[
            self.num_samples_in_node_features:]

        # save the length as the number of time steps minus the number of samples in the node feature minus the number of samples in the node target
        self.num_graphs = 1 + len(
            self.timestamps
        ) - self.num_samples_in_node_features - self.num_samples_in_node_targets
        self.indices = list(range(self.num_graphs))

    @property
    def raw_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return []

    @property
    def processed_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return []

    def clear(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def download(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def process(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def get(self, idx):
        """Obtain a graph from the dataset."""
        # ensure we have the graph index ranges
        assert idx in self.indices, f"Index {idx} is not in dataset indices."

        if self.verbose:
            print(
                f"[{datetime.now()}] Getting graph {idx} of {self.indices[-1]}")
        return self.__getitem__(idx)

    def __len__(self):
        return self.num_graphs

    def __getitem__(self, idx: Union[int, slice]):
        """Obtain a graph from the dataset."""
        if isinstance(idx, int):
            assert idx in self.indices, f"Index {idx} is not in dataset indices."

            if self.verbose:
                print(f"[{datetime.now()}] Getting graph {idx} of {self.indices[-1]}")
            
            data = self._load_data_from_memory(idx)
            return data
        elif isinstance(idx, slice):
            start, stop, step = idx.indices(self.num_graphs)
            # create a shallow copy and override its indices
            ds = copy.copy(self)
            ds.indices = ds.indices[start:stop:step]
            ds.num_graphs = len(ds.indices)
            return ds
        else:
            raise ValueError("Invalid index type.")


    def _load_data_from_memory(self, idx: int) -> dict:
        """Load the graph for the given index from memory."""
        time_index_start = idx
        time_index_end = idx + self.num_samples_in_node_features + self.num_samples_in_node_targets

        # Calculate timestamps
        feature_start_time = pd.to_datetime(self._graph_data["feature_timestamps"][0]) + pd.Timedelta(self.freq) * time_index_start
        feature_timestamps = pd.date_range(start=feature_start_time, periods=self.num_samples_in_node_features, freq=self.freq).to_numpy()
        
        target_start_time = feature_timestamps[-1] + pd.Timedelta(self.freq)  
        target_timestamps = pd.date_range(start=target_start_time, periods=self.num_samples_in_node_targets, freq=self.freq).to_numpy()
        
        target_end_time = target_timestamps[-1]
        feature_end_time = feature_timestamps[-1]
        
        data = {**self._graph_data}
        data["x"] = data["x"][:, time_index_start:time_index_start + self.num_samples_in_node_features]
        data["y"] = data["y"][:, time_index_start + self.num_samples_in_node_features:time_index_end]
        data["x_mask"] = data["x_mask"][:, time_index_start:time_index_start + self.num_samples_in_node_features]
        data["y_mask"] = data["y_mask"][:, time_index_start + self.num_samples_in_node_features:time_index_end]

        # Compute the rest of the masks
        node_features_mask = np.all(np.all(data["x_mask"], axis=1), axis=1)
        node_targets_mask = np.all(np.all(data["y_mask"], axis=1), axis=1)
        node_all_valid_measurements_mask = np.all(np.stack((node_features_mask, node_targets_mask), axis=1), axis=1)
        edge_node_all_valid_measurements_mask = np.logical_and(
            node_all_valid_measurements_mask[data["edge_index"][0]],
            node_all_valid_measurements_mask[data["edge_index"][1]]
        )

        data["node_features_mask"] = node_features_mask
        data["node_targets_mask"] = node_targets_mask
        data["node_all_valid_measurements_mask"] = node_all_valid_measurements_mask
        data["edge_node_all_valid_measurements_mask"] = edge_node_all_valid_measurements_mask

        # determine the aggregate time range
        data["feature_start_time"] = feature_start_time
        data["feature_end_time"] = feature_end_time
        data["target_start_time"] = target_start_time
        data["target_end_time"] = target_end_time
        data["feature_timestamps"] = feature_timestamps
        data["target_timestamps"] = target_timestamps

        if self.verbose:
            print(f"feature_start_time: {feature_start_time}")
            print(f"feature_end_time: {feature_end_time}")
            print(f"target_start_time: {target_start_time}")
            print(f"target_end_time: {target_end_time}")
            print(f"time index start: {time_index_start}")
            print(f"time index end: {time_index_end}")

        # handle missing values
        data["node_features"] = np.nan_to_num(data["x"], nan=self.node_missing_value)
        data["node_targets"] = np.nan_to_num(data["y"], nan=self.node_missing_value)

        if self.verbose:
            # print shapes
            print(f"node_features shape: {data['node_features'].shape}")
            print(f"node_targets shape: {data['node_targets'].shape}")
            print(f"x_mask shape: {data['x_mask'].shape}")
            print(f"y_mask shape: {data['y_mask'].shape}")
            print(f"edge_index shape: {data['edge_index'].shape}")

        return data
