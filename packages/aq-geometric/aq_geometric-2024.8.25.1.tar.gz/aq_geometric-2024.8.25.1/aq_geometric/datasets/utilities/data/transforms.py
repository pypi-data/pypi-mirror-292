from datetime import datetime
from typing import  Tuple, Union

import h3
import numpy as np


def load_from_graph(
    graph: dict,
    include_target: bool = True,
    verbose: bool = False,
    include_masks_in_targets: bool = False,
    include_masks_in_features: bool = False,
    reshape_order: str = "F",
    num_samples_in_node_feature: int = 48,
    num_features_in_node_feature: int = 3,
    num_samples_in_node_target: int = 24,
    num_features_in_node_target: int = 3,
) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray,
                                                np.ndarray]]:
    """Loads data from a graph in the feature vector for training or inference.

    Processes graph data into features (X) and targets (y), if included. Handles missing values and
    mask incorporation based on specified options.

    Args:
        graph (Data): The graph data.
        include_target (bool): Whether to include target values (y).
        verbose (bool): Whether to print debugging messages.
        include_masks_in_targets (bool): Whether to include masks in the target array.
        include_masks_in_features (bool): Whether to include masks in the feature array.
        reshape_order (str): Reshape order ('C', 'F', or 'A').
        num_samples_in_node_feature (int): Number of samples per node feature.
        num_features_in_node_feature (int): Number of node features.
        num_samples_in_node_target (int): Number of samples per node target.
        num_features_in_node_target (int): Number of node targets.

    Returns:
        Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]: 
            - If `include_target` is False: Tuple of (h3_indices, X)
            - If `include_target` is True: Tuple of (h3_indices, X, y)
    """
    feature_vector_shape = (
        -1, 2  * num_samples_in_node_feature * num_features_in_node_feature
        if include_masks_in_features
        else num_samples_in_node_feature * num_features_in_node_feature
    )
    target_vector_shape = (
        -1, 2 * num_samples_in_node_target * num_features_in_node_target if include_masks_in_targets
        else num_samples_in_node_target * num_features_in_node_target
    )

    graph_data = graph["x"]
    graph_data_masks = graph["x_mask"]
    graph_target = graph["y"]
    graph_target_masks = graph["y_mask"]

    h3_index_to_node_id_map = {v: i for i, v in enumerate(graph["h3_index"])}

    X_samples = []
    y_samples = []
    sample_h3_indices = []

    # iterate through each h3 index
    for h3_index in graph["h3_index"]:

        node_id = h3_index_to_node_id_map[h3_index]

        node_data_target = graph_target[node_id, :, :]
        node_data_target_mask = graph_target_masks[node_id, :, :]

        if include_target and (np.any(node_data_target_mask == 0) or np.any(graph_data_masks[node_id, -1, :] == 0)):
            if verbose:
                print(f"[{datetime.now()}] skipping {h3_index} (node id {node_id}) due to NaN values in target.")
            continue
        
        # reshape target data
        y = np.concatenate(
            [
                node_data_target.reshape(1, -1, order=reshape_order),
                node_data_target_mask.reshape(1, -1, order=reshape_order),
            ],
            axis=1,
        ) if include_masks_in_targets else node_data_target.reshape(1, -1, order=reshape_order)

        # feature data (X)
        node_data = graph_data[node_id, :, :]
        node_data_masks = graph_data_masks[node_id, :, :]

        # reshape feature data
        X = np.concatenate(
            [
                node_data.reshape(1, -1, order=reshape_order),
                node_data_masks.reshape(1, -1, order=reshape_order),
            ],
            axis=1,
        ) if include_masks_in_features else node_data.reshape(1, -1, order=reshape_order)
        
        if verbose:
            print(f"[{datetime.now()}] after obtaining node values, X shape: {np.shape(X)}")

        # update the model for this example
        X_samples.append(X)
        y_samples.append(y)
        sample_h3_indices.append(h3_index)

    # transform the samples to numpy arrays
    X_samples = np.reshape(np.array(X_samples), feature_vector_shape,
                            reshape_order)
    y_samples = np.reshape(np.array(y_samples), target_vector_shape,
                            reshape_order)
    sample_h3_indices = np.array(sample_h3_indices)

    if include_target:
        if verbose:
            print(f"[{datetime.now()}] ")
        return sample_h3_indices, X_samples, y_samples
    else:
        return sample_h3_indices, X_samples


def load_from_graph_hierarchical(
    graph: dict,
    include_target: bool = True,
    verbose: bool = False,
    include_masks_in_targets: bool = False,
    include_masks_in_features: bool = False,
    reshape_order: str = "F",
    num_samples_in_node_feature: int = 48,
    num_features_in_node_feature: int = 3,
    num_samples_in_node_target: int = 24,
    num_features_in_node_target: int = 3,
) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray,
                                                np.ndarray]]:
    """Loads data from a graph including its local topology in the feature vector for training or inference.

    Processes graph data into features (X) and targets (y), if included. Handles missing values and
    mask incorporation based on specified options.

    Args:
        graph (Data): The graph data.
        include_target (bool): Whether to include target values (y).
        verbose (bool): Whether to print debugging messages.
        include_masks_in_targets (bool): Whether to include masks in the target array.
        include_masks_in_features (bool): Whether to include masks in the feature array.
        reshape_order (str): Reshape order ('C', 'F', or 'A').
        num_samples_in_node_feature (int): Number of samples per node feature.
        num_features_in_node_feature (int): Number of node features.
        num_samples_in_node_target (int): Number of samples per node target.
        num_features_in_node_target (int): Number of node targets.

    Returns:
        Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]: 
            - If `include_target` is False: Tuple of (h3_indices, X)
            - If `include_target` is True: Tuple of (h3_indices, X, y)
    """
    num_edges_for_each_node = 15  # self + neighbors + children + parent

    feature_vector_shape = (
        -1,
        2 * num_edges_for_each_node * num_samples_in_node_feature * num_features_in_node_feature
        if include_masks_in_features
        else num_edges_for_each_node * num_samples_in_node_feature * num_features_in_node_feature,
    )
    target_vector_shape = (
        -1,
        2 * num_samples_in_node_target * num_features_in_node_target
        if include_masks_in_targets
        else num_samples_in_node_target * num_features_in_node_target,
    )

    graph_data = graph["x"]
    graph_data_masks = graph["x_mask"]
    graph_target = graph["y"]
    graph_target_masks = graph["y_mask"]

    h3_index_to_node_id_map = {v: i for i, v in enumerate(graph["h3_index"])}

    # each "row" in our data represents a (single?) observation of a single station
    # we have structure imposed by our graph such that each "row" has:
    # * a value for each training feature (may be missing) (1, n_train_features)
    # * a mask for whether each above feature was missing (1, n_train_features)
    # * a value for each target feature (may be missing) (1, n_target_features)
    # * a mask for whether each above feature was missing (1, n_target_features)
    # * a value for each connected node at the same resolution (1, n_same_connected_nodes, n_train_features)
    # * a mask for whether each above feature was missing (1, n_same_connected_nodes, n_train_features)
    # * a value for each connected node at a coarser resolution (1, n_coarse_connected_nodes, n_target_features)
    # * a mask for whether each above feature was missing (1, n_coarse_connected_nodes, n_target_features)
    # * a value for each connected node at a finer resolution (1, n_fine_connected_nodes, n_target_features)
    # * a mask for whether each above feature was missing (1, n_fine_connected_nodes, n_target_features)
    # given the fact that we can handle missing values, we can enforce structure that:
    # * there are 6 nodes connected at the same resolution
    # * there is one node (the parent) at a coarser resolution
    # * there are 7 nodes (the children) at a finer resolution
    # we can enforce this structure by reshaping the data
    # get the x and y components of the data

    X_samples = []
    y_samples = []
    sample_h3_indices = []

    # iterate through each h3 index
    for h3_index in graph["h3_index"]:

        node_id = h3_index_to_node_id_map[h3_index]

        # target Data (y)
        node_data_target = graph_target[node_id, :, :]
        node_data_target_mask = graph_target_masks[node_id, :, :]

        if include_target and (np.any(node_data_target_mask == 0) or np.any(graph_data_masks[node_id, -1, :] == 0)):
            if verbose:
                print(f"[{datetime.now()}] Skipping {h3_index} (node id {node_id}) due to NaN values in target.")
            continue
        
        # reshape target data
        y = np.concatenate(
            [
                node_data_target.reshape(1, -1, order=reshape_order),
                node_data_target_mask.reshape(1, -1, order=reshape_order),
            ],
            axis=1,
        ) if include_masks_in_targets else node_data_target.reshape(1, -1, order=reshape_order)

        # feature data (X)
        node_data = graph_data[node_id, :, :]
        node_data_masks = graph_data_masks[node_id, :, :]

        # reshape feature data
        X = np.concatenate(
            [
                node_data.reshape(1, -1, order=reshape_order),
                node_data_masks.reshape(1, -1, order=reshape_order),
            ],
            axis=1,
        ) if include_masks_in_features else node_data.reshape(1, -1, order=reshape_order)
        
        if verbose:
            print(f"[{datetime.now()}] after obtaining node values, X shape: {np.shape(X)}")

        # we need to handle the special case "root" h3 index
        # when h3_index is root we do not have any neighbors or parents
        if h3_index != "root":
            # handle child nodes, if any (otherwise we assign missing values)
            child_h3_indices = h3.h3_to_children(h3_index)
            for child_h3_index in child_h3_indices:
                # get the node id
                if child_h3_index in h3_index_to_node_id_map:
                    child_node_id = h3_index_to_node_id_map[child_h3_index]
                    # get the data
                    child_node_data = graph_data[child_node_id, :, :]
                    child_node_data_masks = graph_data_masks[
                        child_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    child_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    child_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))

                # update the X values
                if include_masks_in_features:
                    X = np.concatenate([
                        X,
                        np.reshape(child_node_data,
                                    (1, -1), reshape_order),
                        np.reshape(child_node_data_masks,
                                    (1, -1), reshape_order)
                    ], axis=1)
                else:
                    X = np.concatenate([
                        X,
                        np.reshape(child_node_data, (1, -1), reshape_order)
                    ], axis=1)

            if verbose:
                print(
                    f"after obtaining child values, X shape: {np.shape(X)}"
                )

            # handle neighbors
            neighbor_h3_indices = [
                h3_id for h3_id in h3.k_ring(h3_index, 1)
                if h3_id != h3_index
            ]
            for neighbor_h3_index in neighbor_h3_indices:
                # get the node id
                if neighbor_h3_index in h3_index_to_node_id_map:
                    neighbor_node_id = h3_index_to_node_id_map[
                        neighbor_h3_index]
                    # get the data
                    neighbor_node_data = graph_data[neighbor_node_id, :, :]
                    neighbor_node_data_masks = graph_data_masks[
                        neighbor_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    neighbor_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    neighbor_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))
                # update the X values
                if include_masks_in_features:
                    X = np.concatenate([
                        X,
                        np.reshape(neighbor_node_data,
                                    (1, -1), reshape_order),
                        np.reshape(neighbor_node_data_masks,
                                    (1, -1), reshape_order)
                    ], axis=1)
                else:
                    X = np.concatenate([
                        X,
                        np.reshape(neighbor_node_data,
                                    (1, -1), reshape_order)
                    ], axis=1)

            if verbose:
                print(
                    f"after obtaining neighbor values, X shape: {np.shape(X)}"
                )

            # handle parent if possible
            if h3.h3_get_resolution(h3_index) > 0:
                parent_h3_index = h3.h3_to_parent(h3_index)
                # get the node id
                if parent_h3_index in h3_index_to_node_id_map:
                    parent_node_id = h3_index_to_node_id_map[
                        parent_h3_index]
                    # get the data
                    parent_node_data = graph_data[parent_node_id, :, :]
                    parent_node_data_masks = graph_data_masks[
                        parent_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    parent_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    parent_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))
            else:
                # the parent is the root node
                parent_node_data = graph_data[-1, :, :]
                parent_node_data_masks = graph_data_masks[-1, :, :]
            # update the X values
            if include_masks_in_features:
                X = np.concatenate([
                    X,
                    np.reshape(parent_node_data, (1, -1), reshape_order),
                    np.reshape(parent_node_data_masks,
                                (1, -1), reshape_order)
                ], axis=1)
            else:
                X = np.concatenate([
                    X,
                    np.reshape(parent_node_data, (1, -1), reshape_order)
                ], axis=1)
        else:
            # make NaNs of the appropriate shape
            parent_node_data = np.full(
                (num_edges_for_each_node, num_samples_in_node_feature,
                  num_features_in_node_feature), np.nan)
            parent_node_data_masks = np.zeros(
                (num_edges_for_each_node, num_samples_in_node_feature,
                  num_features_in_node_feature))
            # update the X values
            if include_masks_in_features:
                X = np.concatenate([
                    X,
                    np.reshape(parent_node_data, (1, -1), reshape_order),
                    np.reshape(parent_node_data_masks,
                                (1, -1), reshape_order)
                ], axis=1)
            else:
                X = np.concatenate([
                    X,
                    np.reshape(parent_node_data, (1, -1), reshape_order)
                ], axis=1)

            if verbose: print(f"[{datetime.now()}] root node: X shape: {np.shape(X)}")

        if verbose:
            print(f"[{datetime.now()}] after obtaining parent values, X shape: {np.shape(X)}")

        if verbose:
            print(
                f"final X shape: {np.shape(X)}, final y shape: {np.shape(y)}"
            )

        if X.shape[1] != feature_vector_shape[1]:
            # this is the case for the 12 pentagons in the graph
            # we can check that the shape is correct and pad, otherwise skip
            x_shape = X.shape
            # check that X has 2 items in the shape
            if len(x_shape) != 2:
                if verbose:
                    print(
                        f"skipping {h3_index} (node id {node_id}) due to incorrect shape {x_shape}"
                    )
                continue

            if include_masks_in_features and x_shape[1] + (
                    2 * num_features_in_node_feature *
                    num_samples_in_node_feature
            ) == feature_vector_shape[1]:
                # pad with NaNs
                # make NaNs of the appropriate shape
                pad_node_data = np.full(
                    (num_edges_for_each_node, num_samples_in_node_feature,
                      num_features_in_node_feature), np.nan)
                pad_node_data_masks = np.zeros(
                    (num_edges_for_each_node, num_samples_in_node_feature,
                      num_features_in_node_feature))
                # update the X values
                X = np.concatenate([
                    X,
                    np.reshape(pad_node_data, (1, -1), reshape_order),
                    np.reshape(pad_node_data_masks, (1, -1), reshape_order)
                ], axis=1)
            elif include_masks_in_features is False and x_shape[1] + (
                    num_features_in_node_feature *
                    num_samples_in_node_feature
            ) == feature_vector_shape[1]:
                X = np.concatenate(
                    [X,
                      np.reshape(pad_node_data,
                                (1, -1), reshape_order)], axis=1)
            else:
                if verbose:
                    print(
                        f"skipping {h3_index} (node id {node_id}) due to incorrect shape {x_shape}"
                    )
                continue

        # update the model for this example
        X_samples.append(X)
        y_samples.append(y)
        sample_h3_indices.append(h3_index)

    # transform the samples to numpy arrays
    X_samples = np.reshape(np.array(X_samples), feature_vector_shape,
                            reshape_order)
    y_samples = np.reshape(np.array(y_samples), target_vector_shape,
                            reshape_order)
    sample_h3_indices = np.array(sample_h3_indices)

    if include_target:
        return sample_h3_indices, X_samples, y_samples
    else:
        return sample_h3_indices, X_samples

def transform_graph_hierarchical(
    graph: dict,
) -> dict:
    """Loads and modifies graph data in-place for hierarchical model training/inference.

    This function modifies the input `graph` dictionary directly by adding neighboring node
    information to the feature and target matrices for each node. It handles missing values and
    mask incorporation based on the provided options.

    Args:
        graph (dict): The graph data dictionary.
    Returns:
        dict: The modified graph data dictionary.
    """
    # these are no longer named arguments
    reshape_order: str = "F"

    num_edges_for_each_node = 15  # self + neighbors + children + parent
    num_samples_in_node_feature = np.shape(graph["x"])[1]
    num_features_in_node_feature = np.shape(graph["x"])[2]

    new_x = np.zeros(
        (len(graph["h3_index"]), num_samples_in_node_feature, num_features_in_node_feature, num_edges_for_each_node)
    )
    new_x_mask = np.zeros(
        (len(graph["h3_index"]), num_samples_in_node_feature, num_features_in_node_feature, num_edges_for_each_node)
    )

    h3_index_to_node_id_map = {v: i for i, v in enumerate(graph["h3_index"])}

    for h3_index in graph["h3_index"]:
        node_id = h3_index_to_node_id_map[h3_index]
        node_data = graph["x"][node_id, :, :]
        node_data_masks = graph["x_mask"][node_id, :, :]

        x = node_data.reshape(1, -1, order=reshape_order)
        x_mask =  node_data_masks.reshape(1, -1, order=reshape_order)

        # we need to handle the special case "root" h3 index
        # when h3_index is root we do not have any neighbors or parents
        if h3_index != "root":
            # handle child nodes, if any (otherwise we assign missing values)
            child_h3_indices = h3.h3_to_children(h3_index)
            for child_h3_index in child_h3_indices:
                # get the node id
                if child_h3_index in h3_index_to_node_id_map:
                    child_node_id = h3_index_to_node_id_map[child_h3_index]
                    # get the data
                    child_node_data = graph["x"][child_node_id, :, :]
                    child_node_data_masks = graph["x_mask"][
                        child_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    child_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    child_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))

                # update the X values
                x = np.concatenate([
                    x,
                    np.reshape(child_node_data, (1, -1), reshape_order)
                ], axis=1)
                x_mask = np.concatenate([
                    x_mask,
                    np.reshape(child_node_data_masks, (1, -1), reshape_order)
                ], axis=1)

            # handle neighbors
            neighbor_h3_indices = [
                h3_id for h3_id in h3.k_ring(h3_index, 1)
                if h3_id != h3_index
            ]
            for neighbor_h3_index in neighbor_h3_indices:
                # get the node id
                if neighbor_h3_index in h3_index_to_node_id_map:
                    neighbor_node_id = h3_index_to_node_id_map[
                        neighbor_h3_index]
                    # get the data
                    neighbor_node_data = graph["x"][neighbor_node_id, :, :]
                    neighbor_node_data_masks = graph["x_mask"][
                        neighbor_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    neighbor_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    neighbor_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))
                # update the X values
                x = np.concatenate([
                    x,
                    np.reshape(neighbor_node_data,
                                (1, -1), reshape_order)
                ], axis=1)
                x_mask = np.concatenate([
                    x_mask,
                    np.reshape(neighbor_node_data_masks,
                                (1, -1), reshape_order)
                ], axis=1)

            # handle parent if possible
            if h3.h3_get_resolution(h3_index) > 0:
                parent_h3_index = h3.h3_to_parent(h3_index)
                # get the node id
                if parent_h3_index in h3_index_to_node_id_map:
                    parent_node_id = h3_index_to_node_id_map[
                        parent_h3_index]
                    # get the data
                    parent_node_data = graph["x"][parent_node_id, :, :]
                    parent_node_data_masks = graph["x_mask"][
                        parent_node_id, :, :]
                else:
                    # make NaNs of the appropriate shape
                    parent_node_data = np.full(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature), np.nan)
                    parent_node_data_masks = np.zeros(
                        (1, num_samples_in_node_feature,
                          num_features_in_node_feature))
            else:
                # the parent is the root node
                parent_node_data = graph["x_mask"][-1, :, :]
                parent_node_data_masks = graph["x_mask"][-1, :, :]
            x = np.concatenate([
                x,
                np.reshape(parent_node_data, (1, -1), reshape_order)
            ], axis=1)
            x_mask = np.concatenate([
                x_mask,
                np.reshape(parent_node_data_masks, (1, -1), reshape_order)
            ], axis=1)

        else:
            # make NaNs of the appropriate shape
            parent_node_data = np.full(
                (num_edges_for_each_node, num_samples_in_node_feature,
                  num_features_in_node_feature), np.nan)
            parent_node_data_masks = np.zeros(
                (num_edges_for_each_node, num_samples_in_node_feature,
                  num_features_in_node_feature))
            # update the X values
            x = np.concatenate([
                x,
                np.reshape(parent_node_data, (1, -1), reshape_order)
            ], axis=1)

        if x.shape[1] != num_edges_for_each_node * num_samples_in_node_feature * num_features_in_node_feature:
            # this is the case for the 12 pentagons in the graph
            # we can check that the shape is correct and pad, otherwise skip
            x_shape = x.shape
            # check that X has 2 items in the shape
            if len(x_shape) != 2:
                continue

            if x_shape[1] + (
                    num_features_in_node_feature *
                    num_samples_in_node_feature
            ) == num_edges_for_each_node * num_samples_in_node_feature * num_features_in_node_feature:
                # pad with NaNs
                # make NaNs of the appropriate shape
                pad_node_data = np.full(
                    (1, num_samples_in_node_feature,
                      num_features_in_node_feature), np.nan)
                pad_node_data_masks = np.zeros(
                    (1, num_samples_in_node_feature,
                      num_features_in_node_feature))

                x = np.concatenate([
                    x,
                    np.reshape(pad_node_data, (1, -1), reshape_order)
                ], axis=1)
                x_mask = np.concatenate([
                    x_mask,
                    np.reshape(pad_node_data_masks, (1, -1), reshape_order)
                ], axis=1)
            else:
                continue
        
        new_x[node_id, :, :, :] = np.reshape(x, (num_samples_in_node_feature, num_features_in_node_feature, num_edges_for_each_node), order=reshape_order)
        new_x_mask[node_id, :, :, :] = np.reshape(x_mask, (num_samples_in_node_feature, num_features_in_node_feature, num_edges_for_each_node), order=reshape_order)

    graph["x"] = new_x
    graph["x_mask"] = new_x_mask

    assert len(graph["x"]) == len(graph["y"]), "after transform, x and y have different lengths"
    assert len(graph["x"]) == len(graph["x_mask"]), "after transform, x and x_mask have different lengths"

    # ensure all shapes are the same for graph["x"] and graph["x_mask"]
    for i in range(1, len(graph["x"])):
        assert np.shape(graph["x"][i, :, :, :]) == np.shape(graph["x_mask"][i, :, :, :]), f"x and x_mask shapes are different for node {i}"
        assert np.shape(graph["x"][i, :, :, :]) == np.shape(graph["x"][i-1, :, :, :]), f"x shapes are different between node {i} and {i-1}"

    return graph

def transform_graph_negative_to_nan(
    graph: dict,
) -> dict:
    """Loads and modifies graph data in-place for model training/inference.

    This function modifies the input `graph` dictionary directly by setting
    values in `x` and `y` to `np.nan` if they are less than 0, modifying the
    `x_mask` and `y_mask` arrays accordingly.

    Args:
        graph (dict): The graph data dictionary.
    Returns:
        dict: The modified graph data dictionary.
    """
    graph["x"][graph["x"] < 0] = np.nan
    graph["x_mask"][graph["x"] < 0] = 0
    graph["y"][graph["y"] < 0] = np.nan
    graph["y_mask"][graph["y"] < 0] = 0
    return graph


def transform_graph_negative_to_nan(
    graph: dict,
) -> dict:
    """Loads and modifies graph data in-place for model training/inference.

    This function modifies the input `graph` dictionary directly by removing
    rows from `x`, `y`, `x_mask`, `y_mask`, `h3_index` and `aqsid` in which
    any of the values in `y` are NaN or in which `y_mask` is 0.

    Args:
        graph (dict): The graph data dictionary.
    Returns:
        dict: The modified graph data dictionary.
    """
    # find indices of rows where y is NaN or y_mask is 0
    nan_indices = np.where(np.isnan(graph["y"]) | (graph["y_mask"] == 0))[0]

    # remove rows from x, y, x_mask, y_mask, h3_index, and aqsid
    graph["x"] = np.delete(graph["x"], nan_indices, axis=0)
    graph["y"] = np.delete(graph["y"], nan_indices, axis=0)
    graph["x_mask"] = np.delete(graph["x_mask"], nan_indices, axis=0)
    graph["y_mask"] = np.delete(graph["y_mask"], nan_indices, axis=0)
    graph["h3_index"] = np.delete(graph["h3_index"], nan_indices, axis=0)
    graph["aqsid"] = np.delete(graph["aqsid"], nan_indices, axis=0)

    return graph

def transform_graph_remove_nan_targets(
    graph: dict,
) -> dict:
    """Loads and modifies graph data in-place for model training/inference.

    This function modifies the input `graph` dictionary directly by removing
    rows from `x`, `y`, `x_mask`, `y_mask`, `h3_index` and `aqsid` in which
    any of the values in `y` are NaN or in which `y_mask` is 0.

    Args:
        graph (dict): The graph data dictionary.
    Returns:
        dict: The modified graph data dictionary.
    """
    # find indices of rows where y is NaN or y_mask is 0
    nan_indices = np.where(np.isnan(graph["y"]) | (graph["y_mask"] == 0))[0]

    # remove rows from x, y, x_mask, y_mask, h3_index, and aqsid
    graph["x"] = np.delete(graph["x"], nan_indices, axis=0)
    graph["y"] = np.delete(graph["y"], nan_indices, axis=0)
    graph["x_mask"] = np.delete(graph["x_mask"], nan_indices, axis=0)
    graph["y_mask"] = np.delete(graph["y_mask"], nan_indices, axis=0)
    graph["h3_index"] = np.delete(graph["h3_index"], nan_indices, axis=0)
    graph["aqsid"] = np.delete(graph["aqsid"], nan_indices, axis=0)

    # we also need to modify the edges and edge_attrs if present
    if "edges" in graph:
        graph["edges"] = np.delete(graph["edges"], nan_indices, axis=0)
        graph["edge_attrs"] = np.delete(graph["edge_attrs"], nan_indices, axis=0)

    return graph
    