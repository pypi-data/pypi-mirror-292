from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray

def make_graph(
    nodes: NDArray[np.object_], 
    edges: Union[NDArray[np.int_], None],
    edge_attr: Union[NDArray[np.float_], None],
    node_features: NDArray[np.float_],
    targets: NDArray[np.float_],
    timestamps: Union[NDArray[np.datetime64], pd.DatetimeIndex],
    feature_names: List[str],
    target_names: List[str],
    node_missing_value: Union[int, float] = np.nan,
    verbose: bool = False,
) -> dict:
    """Make a graph from the nodes and edges."""

    if isinstance(timestamps, pd.DatetimeIndex):
        timestamps = timestamps.to_numpy()
    if isinstance(nodes, pd.DataFrame):
        nodes = nodes[["h3_index", "aqsid", "node_id"]].to_numpy()

    assert nodes.shape[0] == node_features.shape[
        0], "nodes and node_features must have the same number of rows"
    assert nodes.shape[0] == targets.shape[
        0], "nodes and targets must have the same number of rows"
    assert node_features.shape[1] == len(
        timestamps
    ), "node_features must have the same number of columns as timestamps"
    assert targets.shape[1] == len(
        timestamps
    ), "targets must have the same number of columns as timestamps"
    assert len(feature_names) == node_features.shape[
        2], "feature_names must have the same number of elements as node_features columns"
    assert len(target_names) == targets.shape[
        2], "target_names must have the same number of elements as targets columns"
    if edges is not None:
        assert edges.shape[0] == 2, "edges must have shape (2, num_edges)"
    if edge_attr is not None:
        assert edge_attr.shape[0] == edges.shape[
            1], "edge_attr must have the same number of rows as edge_index columns"
        assert isinstance(edge_attr,
                          np.ndarray), "edge_attr must be a numpy array"

    if verbose:
        print(
            f"[{datetime.now()}] Making graph from nodes of shape {nodes.shape} with features of shape {node_features.shape} and targets of shape {targets.shape}"
        )

    # Map h3 indices to node IDs
    h3_index_to_id_map = {v[0]: v[2] for v in nodes}

    # Create edge_index
    if edges is not None:
        edge_index = np.array([
            (h3_index_to_id_map[e[0]], h3_index_to_id_map[e[1]])
            for e in edges.T
            if e[0] in h3_index_to_id_map and e[1] in h3_index_to_id_map
        ]).T
    else:
        edge_index = None

    # Create mask for missing values
    x_mask = node_features >= 0
    y_mask = targets >= 0
    node_features_mask = np.all(np.all(x_mask, axis=1), axis=1)  
    node_targets_mask = np.all(np.all(y_mask, axis=1), axis=1)
    node_all_valid_measurements_mask = np.all(
        np.stack((node_features_mask, node_targets_mask), axis=1), axis=1
    )
    node_features = np.nan_to_num(node_features, nan=node_missing_value)
    targets = np.nan_to_num(targets, nan=node_missing_value)

    if verbose:
        print(f"[{datetime.now()}] x_mask has shape {x_mask.shape}")
    if verbose:
        print(f"[{datetime.now()}] y_mask has shape {y_mask.shape}")
    if verbose:
        print(
            f"[{datetime.now()}] node_all_valid_measurements_mask has shape {node_all_valid_measurements_mask.shape}"
        )

    edge_node_all_valid_measurements_mask = np.logical_and(
        node_all_valid_measurements_mask[edge_index[0]], 
        node_all_valid_measurements_mask[edge_index[1]]
    )

    if verbose:
        print(
            f"[{datetime.now()}] edge_node_all_valid_measurements_mask has shape {edge_node_all_valid_measurements_mask.shape}"
        )

    if verbose: print(f"[{datetime.now()}] processed masks")

    # Create the graph dictionary (replacement for torch_geometric.data.Data)
    graph = {
        "x": np.nan_to_num(node_features, nan=node_missing_value),
        "y": np.nan_to_num(targets, nan=node_missing_value),
        "x_mask": x_mask,
        "y_mask": y_mask,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
        "h3_index": nodes[:, 0],
        "aqsid": nodes[:, 1],
        "timestamps": timestamps,
        "feature_timestamps": timestamps,
        "target_timestamps": timestamps,
        "node_all_valid_measurements_mask": node_all_valid_measurements_mask,
        "edge_node_all_valid_measurements_mask": edge_node_all_valid_measurements_mask,
        "node_features_mask": node_features_mask,
        "node_targets_mask": node_targets_mask,
    }

    return graph


def make_graph_data(
    nodes: NDArray[np.object_], 
    edges: Union[NDArray[np.int_], None],
    edge_attr: Union[NDArray[np.float_], None],
    node_data: NDArray[np.float_],
    timestamps: Union[NDArray[np.datetime64], pd.DatetimeIndex],
    measurement_names: List[str],
    node_missing_value: Union[int, float] = np.nan,
    verbose: bool = False,
) -> dict:
    """Make a graph from the nodes and edges."""

    if isinstance(timestamps, pd.DatetimeIndex):
        timestamps = timestamps.to_numpy()
    if isinstance(nodes, pd.DataFrame):
        nodes = nodes[["h3_index", "aqsid", "node_id"]].to_numpy()

    assert nodes.shape[0] == node_data.shape[
        0], "nodes and node_data must have the same number of rows"
    assert node_data.shape[1] == len(
        timestamps
    ), "node_data must have the same number of columns as timestamps"
    assert len(measurement_names) == node_data.shape[
        2], "measurement_names must have the same number of elements as node_data columns"
    if edges is not None:
        assert edges.shape[0] == 2, "edges must have shape (2, num_edges)"
    if edge_attr is not None:
        assert edge_attr.shape[0] == edges.shape[
            1], "edge_attr must have the same number of rows as edge_index columns"
        assert isinstance(edge_attr,
                          np.ndarray), "edge_attr must be a numpy array"

    if verbose:
        print(
            f"[{datetime.now()}] Making graph data from nodes of shape {nodes.shape} with features of shape {node_data.shape}"
        )

    # Map h3 indices to node IDs
    h3_index_to_id_map = {v[0]: v[2] for v in nodes}

    # Create edge_index
    if edges is not None:
        edge_index = np.array([
            (h3_index_to_id_map[e[0]], h3_index_to_id_map[e[1]])
            for e in edges.T
            if e[0] in h3_index_to_id_map and e[1] in h3_index_to_id_map
        ]).T
    else:
        edge_index = None

    # Create mask for missing values
    data_mask = node_data >= 0
    node_measurements_mask = np.all(np.all(data_mask, axis=1), axis=1)  

    node_data = np.nan_to_num(node_data, nan=node_missing_value)

    if verbose:
        print(f"[{datetime.now()}] data_mask has shape {data_mask.shape}")
    if verbose:
        print(
            f"[{datetime.now()}] node_measurements_mask has shape {node_measurements_mask.shape}"
        )

    edge_node_all_valid_measurements_mask = np.logical_and(
        node_measurements_mask[edge_index[0]], 
        node_measurements_mask[edge_index[1]]
    )

    if verbose:
        print(
            f"[{datetime.now()}] edge_node_all_valid_measurements_mask has shape {edge_node_all_valid_measurements_mask.shape}"
        )

    if verbose: print(f"[{datetime.now()}] processed masks")

    # Create the graph dictionary (replacement for torch_geometric.data.Data)
    graph = {
        "data": np.nan_to_num(node_data, nan=node_missing_value),
        "data_mask": data_mask,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
        "h3_index": nodes[:, 0],
        "aqsid": nodes[:, 1],
        "measurement_names": measurement_names,
        "timestamps": timestamps,
        "node_measurements_mask": node_measurements_mask,
        "edge_node_all_valid_measurements_mask": edge_node_all_valid_measurements_mask,
    }

    return graph
