import os
import pickle
import copy
import os.path as osp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import List, Union, Callable, Optional, Tuple

import h5py
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
from aq_utilities.engine.psql import get_engine
from aq_utilities.data import load_hourly_data, load_hourly_feature, load_hourly_features, load_stations_info, load_daily_stations
from aq_utilities.data import apply_filters, filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon
from aq_utilities.data import measurements_to_aqsid, determine_leaf_h3_resolution

from aq_geometric.data.remote import load_node_feature, load_node_features, load_nodes_info
from aq_geometric.data.file.local import load_hourly_data_from_fp, load_stations_info_from_fp, load_hourly_feature_from_fp, load_hourly_features_from_fp
from aq_geometric.data.graph.edges.compute_edges import get_edges_from_df
from aq_geometric.data.graph.nodes.compute_nodes import get_nodes_from_df
from aq_geometric.data.graph.nodes.compute_node_features import data_to_feature, get_node_feature, get_node_features, stack_node_features
from aq_geometric.data.graph.compute_graph import make_graph_data


class AqGeometricDataset:
    def __init__(
            self,
            root: str,
            pre_transform: Optional[Callable] = None,
            features: List[str] = ["PM2.5"], targets: List[str] = [
                "OZONE"
            ], start_time: str = "2023-01-01", end_time: str = "2023-01-15",
            freq: str = "1H", samples_in_node_features: int = 24,
            samples_in_node_targets: int = 24,
            max_samples_in_graph_on_disk: int = 380,
            time_closed_interval: bool = False,
            engine: Union["sqlalchemy.engine.Engine", None] = None,
            engine_kwargs: dict = {}, selected_aqsids: Union[List[str],
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
            node_missing_value: float = np.nan, verbose: bool = False,
            filetype: str = "pickle",
            max_workers: int = 4):
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
        self.max_samples_in_graph_on_disk = max_samples_in_graph_on_disk
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
        self.filetype = filetype
        self.max_workers = max_workers
        self.verbose = verbose

        # obtain the timestamps for the features and targets
        self.timestamps = pd.date_range(
            start=self.start_time, end=self.end_time, freq=self.freq,
            inclusive="left" if self.time_closed_interval == False else "both")
        # save the length as the number of time steps minus the number of samples in the node feature minus the number of samples in the node target
        self.num_graphs = 1 + len(
            self.timestamps
        ) - self.num_samples_in_node_features - self.num_samples_in_node_targets
        self.indices = list(range(self.num_graphs))

        # determine the number of graphs based on start_time, end_time and max_samples_in_graph_on_disk
        q_start_time, q_end_time = self.timestamps[
            0], self.timestamps[-1] + pd.Timedelta(
                self.freq)  # add one more sample to the end time
        query_start_times = [q_start_time]
        query_end_times = [q_end_time]

        if self.max_samples_in_graph_on_disk < len(self.timestamps):
            query_start_times = self.timestamps[::self.
                                                max_samples_in_graph_on_disk].tolist(
                                                )
            query_end_times = self.timestamps[
                self.max_samples_in_graph_on_disk::self.
                max_samples_in_graph_on_disk].tolist()
            query_start_times.append(query_end_times[-1])
            query_end_times.append(
                pd.to_datetime(self.timestamps[-1]) + pd.Timedelta(self.freq))
        # persist the start and end times
        self.query_start_times = query_start_times
        self.query_end_times = query_end_times

        self.graph_index_ranges = []
        self.current_graph_index = None
        self.current_graph = None
        self.stations_info_df = None
        self.nodes = None
        self.edges = None
        self.edge_attr = None
        self.num_graphs_on_disk = 0
        self._loaded_graph_indices = set()
        self._graph = None

        # this matches the PyG Dataset implementation and acts as the root for raw files shared by both
        self.root = root
        self.pre_transform = pre_transform

        # download and process are called but check if we've already cached the data under root
        self.download()
        self.process()
    
    @property
    def processed_dir(self) -> os.PathLike:
        """Return the processed_dir based on the root"""
        return osp.join(self.root, "processed")

    @property
    def raw_dir(self) -> os.PathLike:
        """Return the raw_dir based on the root"""
        return osp.join(self.root, "raw")

    @property
    def _graph_data(self) -> dict:
        """Return the graph data from memory."""
        return self._graph

    @property
    def transform(self) -> Optional[Callable]:
        """Return the transform."""
        return self.pre_transform

    @property
    def raw_file_names(self) -> List[str]:
        """Return the raw file name of the data and stations info."""
        from glob import glob
        raw_fps = ["stations_info.csv"]
        # extend the raw file names with the hourly features and targets
        raw_fps.extend([
            osp.basename(f) for f in list(
                glob(osp.join(self.raw_dir, f"{f}_data_[0-9]*.csv"))
                for f in self.features) for f in f
        ])
        raw_fps.extend([
            osp.basename(f) for f in list(
                glob(osp.join(self.raw_dir, f"{f}_data_[0-9]*.csv"))
                for f in self.targets if f not in self.features) for f in f
        ])
        return raw_fps

    @property
    def processed_file_names(self):
        """Return the processed file names."""
        from glob import glob
        return sorted([osp.basename(f) for f in glob(osp.join(self.processed_dir, f"data_[0-9]*.{self.filetype}"))])
    
    def __len__(self):
        return self.num_graphs

    def clear(self):
        """Clear the raw and processed directories."""
        import shutil
        shutil.rmtree(self.raw_dir)
        shutil.rmtree(self.processed_dir)
        return None

    def download(self):
        """Query remote database for the data and stations info, saving to csv files."""
        # ensure the processed directory exists
        if not osp.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
        # check if the there are already raw files
        if len(os.listdir(self.raw_dir)) > 0:
            print(f"Raw files already exist in {self.raw_dir}")
            return

        timestamps = self.timestamps
        # assert that the number of samples in the node feature and target is less than the total number of samples
        assert self.num_samples_in_node_features + self.num_samples_in_node_targets <= len(
            timestamps
        ), "The number of samples in the node feature and target must be less than the total number of samples."
        start_time, end_time = timestamps[0], timestamps[-1] + pd.Timedelta(
            self.freq)  # add one more sample to the end time

        if self.verbose:
            print(f"timestamps: {self.timestamps}")
            print(f"start times: {self.query_start_times}")
            print(f"end times: {self.query_end_times}")

        stations_info: pd.DataFrame
        if self.stations_info_fp is not None:
            stations_info = load_stations_info_from_fp(
                self.stations_info_fp)
        else:
            stations_info = load_daily_stations(
                engine=self.engine,
                query_date=start_time.strftime("%Y-%m-%d"),
                selected_aqsids=self.selected_aqsids,
                verbose=self.verbose,
            )
        # apply filters
        stations_info = apply_filters(
            stations_info,
            self.stations_info_filters,
            verbose=self.verbose,
        )
        # determine leaf resolution if none is provided
        if self.leaf_h3_resolution is None:
            leaf_resolution = determine_leaf_h3_resolution(
                df=stations_info,
                min_h3_resolution=self.min_h3_resolution,
                max_h3_resolution=self.max_h3_resolution,
                verbose=self.verbose,
            )
            if self.verbose:
                print(f"[{datetime.now()}] leaf resolution: {leaf_resolution}")
            self.leaf_h3_resolution = leaf_resolution

        # save the stations info
        stations_info.to_csv(osp.join(self.raw_dir, "stations_info.csv"),
                             index=False)

        # determine the set of features and targets
        features_and_targets = set(self.features + self.targets)
        # load the hourly features and targets
        for f in features_and_targets:
            for i, (q_start_time, q_end_time) in enumerate(
                    zip(self.query_start_times, self.query_end_times)):
                data_df = load_node_feature(
                    engine=self.engine,
                    table="hourly_data",
                    start_time=q_start_time,
                    end_time=q_end_time,
                    feature=f,
                    selected_aqsids=self.selected_aqsids,
                    verbose=self.verbose,
                )
                # save the hourly data
                data_df.to_csv(osp.join(self.raw_dir, f"{f}_data_{i}.csv"),
                                  index=False)
        return None

    def process(self):
        """Process the data and stations info into individual graphs."""
        # ensure the processed directory exists
        if not osp.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        
        existing_files = self.processed_file_names
        file_ids = [f.split("_")[-1].split(".")[0] for f in self.raw_file_names if "stations" not in f]
        expected_files = [f"data_{i}.{self.filetype}" for i in file_ids]
        if set(existing_files) == set(expected_files):
            print(f"Processed files already exist in {self.processed_dir}")
            self.num_graphs_on_disk = len(existing_files)
            return
        else:
            print(f"Processed files do not match expected files in {self.processed_dir}, generating...")
            if self.verbose:
                print(f"[{datetime.now()}] raw file indicators: {file_ids} do not match existing files {existing_files}"
            )

        # obtain the timestamps for the features and targets
        q_start_times, q_end_times = self.query_start_times, self.query_end_times

        if self.verbose:
            print(
                f"[{datetime.now()}] start and end times: {[(start_time, end_time) for start_time, end_time in zip(q_start_times, q_end_times)]}"
            )

        num_graphs_on_disk = len(q_start_times)

        if self.verbose:
            print(f"[{datetime.now()}] processing {num_graphs_on_disk} graphs")

        if self.stations_info_df is None:
            stations_info_df = pd.read_csv(
                osp.join(self.raw_dir, "stations_info.csv"))
            self.stations_info_df = stations_info_df
        if self.leaf_h3_resolution is None:
            # determine leaf resolution if none is provide
            leaf_resolution = determine_leaf_h3_resolution(
                df=self.stations_info_df,
                min_h3_resolution=self.min_h3_resolution,
                max_h3_resolution=self.max_h3_resolution,
                verbose=self.verbose,
            )
            if self.verbose:
                print(
                    f"[{datetime.now()}] leaf resolution: {leaf_resolution}"
                )
            self.leaf_h3_resolution = leaf_resolution
        if self.nodes is None:
            # get the h3_index_to_node_id_map and h3_index_to_aqsid_map
            nodes = get_nodes_from_df(
                stations_info_df=self.stations_info_df,
                min_h3_resolution=self.min_h3_resolution,
                leaf_h3_resolution=self.leaf_h3_resolution,
                include_root_node=self.include_root_node,
                verbose=self.verbose,
            )
            self.nodes = nodes
        if self.edges is None:
            # get the edges and edge attributes
            edges = get_edges_from_df(
                stations_info_df=self.stations_info_df,
                selected_h3_indices=self.selected_h3_indices,
                min_h3_resolution=self.min_h3_resolution,
                leaf_h3_resolution=self.leaf_h3_resolution,
                with_edge_features=self.with_edge_features,
                include_root_node=self.include_root_node,
                make_undirected=self.make_undirected,
                include_self_loops=self.include_self_loops,
                min_to_root_edge_distance=self.min_to_root_edge_distance,
                verbose=self.verbose,
            )
            if self.with_edge_features:
                self.edges, self.edge_attr = edges
            else:
                self.edges = edges

        # create a partial function to process a single graph
        edge_attr = self.edge_attr if self.with_edge_features else None
        process_graph_partial = partial(
            self._process_single_graph,
            self.features,
            self.targets,
            self.stations_info_df,
            self.nodes,
            self.edges,
            edge_attr,
            self.min_h3_resolution,
            self.leaf_h3_resolution,
            self.node_missing_value,
        )

        # use ProcessPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i, (start_time, end_time) in enumerate(zip(self.query_start_times, self.query_end_times)):
                futures.append(executor.submit(process_graph_partial, i, start_time, end_time))

            with tqdm(total=len(futures), desc="Processing graphs") as pbar:
                for future in as_completed(futures):
                    try:
                        i, graph = future.result()
                        if self.verbose:
                            print(f"[{datetime.now()}] Processed graph {i} ({type(graph)}).")
                        filename = osp.join(self.processed_dir, f"data_{i}.{self.filetype}")
                        if self.verbose:
                            print(f"[{datetime.now()}] Saving graph {i} to {filename}.")
                        getattr(self, f"save_graph_to_{self.filetype}")(graph, filename)
                        self.graph_index_ranges.append((graph["feature_timestamps"][0], graph["feature_timestamps"][-1]))
                        self.num_graphs_on_disk += 1
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing graph: {e}")

        if self.verbose:
            print(f"[{datetime.now()}] Processed {self.num_graphs_on_disk} graphs.")

    def _process_single_graph(self,
                              features: List[str],
                              targets: List[str],
                              stations_info_df: pd.DataFrame,
                              nodes: pd.DataFrame,
                              edges: pd.DataFrame,
                              edge_attr: pd.DataFrame,
                              min_h3_resolution: int,
                              leaf_h3_resolution: int,
                              node_missing_value: float,
                              i: int,
                              start_time: pd.Timestamp,
                              end_time: pd.Timestamp,
                              ) -> Tuple[int, dict]:
        """Process a single graph, returing the index of the processed graph file and its contents."""
        # make the timestamps between start_time and end_time
        graph_timestamps = pd.date_range(start=start_time, end=end_time,
                                            freq=self.freq, inclusive="left")
        # load node features from disk
        node_features = []
        # load the node features from the local file
        measurement_names = list(set(features + targets))
        for feature in measurement_names:
            feature_fp = osp.join(self.raw_dir, f"{feature}_data_{i}.csv")
            data_df = load_hourly_data_from_fp(feature_fp)
            feature_df = data_to_feature(
                df=data_df,
                stations_info_df=stations_info_df,
                min_h3_resolution=min_h3_resolution,
                leaf_h3_resolution=leaf_h3_resolution,
                verbose=self.verbose,
            )
            node_feature = get_node_feature(
                feature_df=feature_df,
                timestamps=graph_timestamps,
                nodes=nodes,
                verbose=self.verbose,
            )
            node_features.append(node_feature)
        # stack the features and targets
        node_features = stack_node_features(nodes, node_features)
        # make the graph
        graph = make_graph_data(
            nodes=nodes,
            edges=edges[["from", "to"]].to_numpy().T,
            edge_attr=edge_attr.drop(
                columns=["from", "to"]).to_numpy()
            if edge_attr is not None else None,
            node_data=node_features,
            measurement_names=measurement_names,
            timestamps=graph_timestamps,
            node_missing_value=node_missing_value,
            verbose=self.verbose,
        )
        if self.pre_transform is not None:
            if self.verbose:
                print(
                    f"Pre-transforming graph {i} of {self.num_graphs_on_disk}")
            graph = self.pre_transform(graph)
        return i, graph

    def get(self, idx: int):
        # ensure we have the graph index ranges
        # get the processed file names
        if self.num_graphs_on_disk == 0:
            self.num_graphs_on_disk = len(self.processed_file_names)
        # map idx to the graph on disk
        i = idx // self.max_samples_in_graph_on_disk
        if self.verbose:
            print(
                f"[{datetime.now()}] Getting graph {i+1} of {self.num_graphs_on_disk+1}"
            )

        self._load_graph_from_disk(i)
        return self.__getitem__(idx)

    def __getitem__(self, idx: Union[int, slice]):
        """Compute the graph for index idx using data from disk."""
        if isinstance(idx, int):
            # get the data for this range
            relative_idx = idx % self.max_samples_in_graph_on_disk  # determine the start index relative to the graph
            data = self._load_data_from_memory(relative_idx)
            if self.transform is not None:
                data = self.transform(data)
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

    def _load_graph_from_disk(self, i):
        """Load the graph from disk."""
        if i not in self._loaded_graph_indices:
            # remove the existing graph from memory
            self._graph = None
            # remove the existing graph index
            self._loaded_graph_indices = set()

            # load the graph from disk and next graph if available
            graph = getattr(self, f"load_graph_from_{self.filetype}")(osp.join(self.processed_dir, f"data_{i}.{self.filetype}"))

            self._loaded_graph_indices.add(i)
            if self.verbose:
                print(f"Loaded graph {i+1} of {self.num_graphs_on_disk}")
            if i < self.num_graphs_on_disk - 1:
                # obtain the next graph
                next_graph = getattr(self, f"load_graph_from_{self.filetype}")(osp.join(self.processed_dir, f"data_{i+1}.{self.filetype}"))
                
                if self.verbose:
                    print(f"Loaded graph {i+2} of {self.num_graphs_on_disk}")
                
                # ensure the h3_index and aqsid are the same
                assert all(h1 == h2 for h1, h2 in zip(
                    graph["h3_index"].tolist(), next_graph["h3_index"].tolist())
                           ), "The h3_index must be the same for both graphs."
                assert all(h1 == h2 for h1, h2 in zip(
                    graph["aqsid"].tolist(), next_graph["aqsid"].tolist())
                           ), "The aqsid must be the same for both graphs."
                assert all(h1 == h2 for h1, h2 in zip(graph["measurement_names"], next_graph["measurement_names"])), "The measurement_names must be the same for both graphs."
                
                # concatenate the graphs
                node_data = np.concatenate((graph["data"], next_graph["data"]), axis=1)
                timestamps = np.concatenate((graph["timestamps"], next_graph["timestamps"]), axis=0)

                # invariant
                h3_index = graph["h3_index"]
                aqsid = graph["aqsid"]

                # combine the masks
                data_mask = np.concatenate((graph["data_mask"], next_graph["data_mask"]), axis=1)

                graph = {
                    "data": node_data,
                    "data_mask": data_mask,
                    "edge_index": graph["edge_index"],
                    "edge_attr": graph["edge_attr"],
                    "h3_index": h3_index,
                    "aqsid": aqsid,
                    "timestamps": timestamps,
                    "measurement_names": next_graph["measurement_names"],
                }

                self._loaded_graph_indices.add(i + 1)

                if self.verbose:
                    print(f"Combined graph {i+1} and {i+2}")
                    print(f"Current loaded graph indices (0 based, subtract one): {self._loaded_graph_indices}")

            # Store the current graph data
            self._graph = graph
        else:
            if self.verbose:
                print(f"Graph {i+1} already loaded.")
                print(
                    f"Current loaded graph indices (0 based, subtract one): {self._loaded_graph_indices}"
                )

    def _load_data_from_memory(self, idx: int) -> dict:
        """Load the graph for the given index from memory."""
        time_index_start = idx
        time_index_end = idx + self.num_samples_in_node_features + self.num_samples_in_node_targets

        # Calculate timestamps
        feature_start_time = pd.to_datetime(self._graph_data["timestamps"][0]) + pd.Timedelta(self.freq) * time_index_start
        feature_timestamps = pd.date_range(start=feature_start_time, periods=self.num_samples_in_node_features, freq=self.freq).to_numpy()
        
        target_start_time = feature_timestamps[-1] + pd.Timedelta(self.freq)  
        target_timestamps = pd.date_range(start=target_start_time, periods=self.num_samples_in_node_targets, freq=self.freq).to_numpy()
        
        target_end_time = target_timestamps[-1]
        feature_end_time = feature_timestamps[-1]

        measurement_names = self._graph_data["measurement_names"]
        feature_names = self.features
        target_names = self.targets

        # extract the feature indices and target indices based on the feature names and target names
        feature_indices = [i for i, n in enumerate(measurement_names) if n in feature_names]
        target_indices = [i for i, n in enumerate(measurement_names) if n in feature_names]

        data = {
            "edge_index": self._graph_data["edge_index"],
            "edge_attr": self._graph_data["edge_attr"],
            "h3_index": self._graph_data["h3_index"],
            "aqsid": self._graph_data["aqsid"],
            "feature_names": feature_names,
            "target_names": target_names,
        }

        data["x"] = self._graph_data["data"][:, time_index_start:time_index_start + self.num_samples_in_node_features, feature_indices]
        data["y"] = self._graph_data["data"][:, time_index_start + self.num_samples_in_node_features:time_index_end, target_indices]
        data["x_mask"] = self._graph_data["data_mask"][:, time_index_start:time_index_start + self.num_samples_in_node_features, feature_indices]
        data["y_mask"] = self._graph_data["data_mask"][:, time_index_start + self.num_samples_in_node_features:time_index_end, target_indices]

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

    def save_graph_to_pickle(self, graph: dict, filename: str) -> None:
        """Save the graph data dictionary to a pickle file."""
        if self.verbose:
            print(f"[{datetime.now()}] Saving graph to pickle: {filename}")

        with open(filename, "wb") as f:
            pickle.dump(graph, f)

        if self.verbose:
            print(f"[{datetime.now()}] Graph saved successfully to: {filename}")
    
    def load_graph_from_pickle(self, filename: str) -> dict:
        """Loads the graph data dictionary from a pickle file."""

        if self.verbose:
            print(f"[{datetime.now()}] Loading graph from pickle: {filename}")

        graph = {}
        with open(filename, "rb") as f:
            graph = pickle.load(f)

        if self.verbose:
            print(f"[{datetime.now()}] Graph loaded successfully from: {filename}")

        return graph

    def save_graph_to_hdf5(self, graph: dict, filename: str) -> None:
        """Saves the graph data dictionary to an HDF5 file."""
        if self.verbose:
            print(f"[{datetime.now()}] Saving graph to HDF5: {filename}")

        with h5py.File(filename, "w") as hf:
            for key, value in graph.items():
                if isinstance(value, np.ndarray):
                    if value.dtype == np.object_:
                        hf.create_dataset(key, data=value, dtype=h5py.special_dtype(vlen=str)) 
                    elif value.dtype.kind == 'M':
                        # timestamps: Store as seconds since epoch
                        hf.create_dataset(key, data=value.astype('datetime64[s]').view(np.int64), dtype=np.int64)
                    elif value.dtype == np.bool_:
                        hf.create_dataset(key, data=value, dtype=np.bool_)
                    else:
                        # store other NumPy arrays directly
                        hf.create_dataset(key, data=value)
                elif isinstance(value, (list, tuple)):
                    if np.issubdtype(np.array(value).dtype, np.number):
                        hf.create_dataset(key, data=np.array(value, dtype=np.float32))
                else:
                    # handle scalars
                    hf.create_dataset(key, data=np.array(value, dtype=np.object_), dtype=h5py.special_dtype(vlen=str))
        if self.verbose:
            print(f"[{datetime.now()}] Graph saved successfully to: {filename}")

    def load_graph_from_hdf5(self, filename: str) -> dict:
        """Loads the graph data dictionary from an HDF5 file."""

        if self.verbose:
            print(f"[{datetime.now()}] Loading graph from HDF5: {filename}")

        graph = {}
        with h5py.File(filename, "r") as hf:
            for key in hf.keys():
                value = hf[key][()]
                if isinstance(value, bytes):
                    graph[key] = value.decode('utf-8')
                elif value.dtype == np.int64:
                    graph[key] = value.astype('datetime64[s]')
                else:
                    graph[key] = value

        if self.verbose:
            print(f"[{datetime.now()}] Graph loaded successfully from: {filename}")

        return graph
