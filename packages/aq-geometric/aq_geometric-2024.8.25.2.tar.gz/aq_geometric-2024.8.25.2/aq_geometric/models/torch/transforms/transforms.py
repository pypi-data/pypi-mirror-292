from typing import Optional

import torch


def to_float32(graph: "torch_geometric.data.Data") -> "torch_geometric.data.Data":
    """Convert x and y to float32, and edge_index to long."""
    graph.x = graph.x.to(torch.float32)
    graph.y = graph.y.to(torch.float32)
    graph.edge_index = graph.edge_index.to(torch.long)
    return graph


def update_masks(graph: "torch_geometric.data.Data") -> "torch_geometric.data.Data":
    """Update x_mask and y_mask to handle zero values."""
    graph.x_mask = torch.where(graph.x <= 0, torch.tensor(False), graph.x_mask)
    graph.y_mask = torch.where(graph.y <= 0, torch.tensor(False), graph.y_mask)
    return graph


def slice_graph(graph: "torch_geometric.data.Data", x_samples: Optional[int], y_samples: Optional[int]) -> "torch_geometric.data.Data":
    """Downsample y by a factor of downsample_rate."""
    if x_samples is not None:
        graph.x = graph.x[:, :x_samples, :]
        graph.x_mask = graph.x_mask[:, :x_samples, :]
    if y_samples is not None:
        graph.y = graph.y[:, :y_samples, :]
        graph.y_mask = graph.y_mask[:, :y_samples, :]   

    return graph


def append_predictions_to_graph(graph: "torch_geometric.data.Data", predictions: "torch.Tensor") -> "torch_geometric.data.Data":
    """Append the predictions to the graph."""
    assert graph.x.size(0) == predictions.size(0), "Number of samples in graph and predictions do not match along the node dimension."
    assert graph.x.size(2) == predictions.size(2), "Number of samples in graph and predictions do not match along the feature dimension."

    num_timestamps = predictions.size(1)

    # remove the first num_timestamps from the graph's x data
    graph.x = graph.x[:, num_timestamps:, :]
    graph.x_mask = graph.x_mask[:, num_timestamps:, :]
    # append the predictions to the graph's x data
    graph.x = torch.cat([graph.x, predictions], dim=1)
    # for masking we need to propagate the mask from the last timestep
    graph.x_mask = torch.cat([graph.x_mask, graph.x_mask[:, -1:, :].repeat(1, num_timestamps, 1)], dim=1)

    return graph


def min_max_scale(graph: "torch_geometric.data.Data") -> "torch_geometric.data.Data":
    """Perform min-max scaling on x and y per feature."""
    x = graph.x
    y = graph.y
    x_mask = graph.x_mask
    y_mask = graph.y_mask
    
    num_features = graph.x.size(2)
    x_scaled = torch.zeros_like(graph.x) 
    y_scaled = torch.zeros_like(graph.y)

    # Save the min and max values for each feature
    # x_min and x_mask have shape (num_features,)
    x_min = torch.zeros(x.size(2))
    x_max = torch.zeros(x.size(2))

    # Min-Max Scaling (Normalization) per feature
    num_features = x.size(2)  # Get the number of features
    x_scaled = torch.zeros_like(x) 
    y_scaled = torch.zeros_like(y)

    for feature_idx in range(num_features):
        # Extract the feature slice and its corresponding mask
        feature_slice = x[:, :, feature_idx]
        feature_mask = x_mask[:, :, feature_idx]

        # Calculate min and max for the feature, considering the mask
        min_val = torch.min(feature_slice[feature_mask])
        max_val = torch.max(feature_slice[feature_mask])

        # Update the min and max values in x_min and x_max
        x_min[feature_idx] = min_val
        x_max[feature_idx] = max_val

        # Scale the feature, handling potential division by zero
        denominator = max_val - min_val
        if denominator == 0:
            # If all values are the same, set the scaled feature to 0
            x_scaled[:, :, feature_idx] = 0
        else:
            x_scaled[:, :, feature_idx] = (feature_slice - min_val) / denominator

    # Repeat the same scaling for y
    for feature_idx in range(num_features):
        feature_slice = y[:, :, feature_idx]
        
        if denominator == 0:
            y_scaled[:, :, feature_idx] = 0
        else:
            y_scaled[:, :, feature_idx] = (feature_slice - min_val) / denominator

    # Apply mask after scaling
    x_scaled_masked = x_scaled * x_mask
    y_scaled_masked = y_scaled * y_mask

    # Save the scaled data and masks
    graph.x = x_scaled_masked
    graph.y = y_scaled_masked
    graph.x_min = x_min
    graph.x_max = x_max

    return graph


def quantile_scale(graph: "torch_geometric.data.Data", lower_bound: float = 0.05, upper_bound: float = 0.95) -> "torch_geometric.data.Data":
    """Perform quantile scaling on x and y per feature."""
    num_features = graph.x.size(2) 
    x_scaled = torch.zeros_like(graph.x) 
    y_scaled = torch.zeros_like(graph.y)

    # Save the min and max values for each feature in x
    x_min = torch.zeros(num_features)
    x_max = torch.zeros(num_features)

    for feature_idx in range(num_features):
        # Extract the feature slice and its corresponding mask from x
        feature_slice_x = graph.x[:, :, feature_idx]
        feature_mask_x = graph.x_mask[:, :, feature_idx]

        # Calculate 5th and 95th percentiles for the feature in x, considering the mask
        min_val = torch.quantile(feature_slice_x[feature_mask_x], lower_bound)  
        max_val = torch.quantile(feature_slice_x[feature_mask_x], upper_bound)

        # Update the min and max values in x_min and x_max
        x_min[feature_idx] = min_val
        x_max[feature_idx] = max_val

        # Scale the feature in x, handling potential division by zero
        denominator = max_val - min_val
        if denominator == 0:
            x_scaled[:, :, feature_idx] = 0
        else:
            x_scaled[:, :, feature_idx] = (feature_slice_x - min_val) / denominator

        # Scale the corresponding feature in y using the same min and max from x
        if feature_idx < graph.y.size(2):
            feature_slice_y = graph.y[:, :, feature_idx]
            if denominator == 0:
                y_scaled[:, :, feature_idx] = 0
            else:
                y_scaled[:, :, feature_idx] = (feature_slice_y - min_val) / denominator
    
    # Save the scaled data, masks, and min/max values
    graph.x = x_scaled
    graph.y = y_scaled
    graph.x_min = x_min
    graph.x_max = x_max

    return graph


def celcius_to_kelvin(graph: "torch_geometric.data.Data", feature_idx: int = 7) -> "torch_geometric.data.Data":
    """Convert temperature from Celsius to Kelvin."""
    graph.x[:, :, feature_idx] += 273.15
    return graph


def kelvin_to_celcius(graph: "torch_geometric.data.Data", feature_idx: int = 7) -> "torch_geometric.data.Data":
    """Convert temperature from Kelvin to Celsius."""
    graph.x[:, :, feature_idx] -= 273.15
    return graph


def apply_masks(graph: "torch_geometric.data.Data") -> "torch_geometric.data.Data":
    """Apply masks to the features."""
    graph.x = graph.x * graph.x_mask
    graph.y = graph.y * graph.y_mask
    return graph


def nan_to_zero(graph: "torch_geometric.data.Data") -> "torch_geometric.data.Data":
    """Replace NaN values with zero."""
    graph.x = torch.where(torch.isnan(graph.x), 0, graph.x)
    graph.y = torch.where(torch.isnan(graph.y), 0, graph.y)
    return graph


def preprocess_graph_for_autoencoder(graph: "torch_geometric.Data", scale: str = "quantile", handle_temperature: bool = True) -> "torch_geometric.Data":
    """Preprocess the input graph data for the autoencoder model."""

    assert scale in ["quantile", "min_max"], f"Invalid scaling method: {scale}"

    # For the GCN autoencoder, we need the edge index to be in the format (2, num_edges)
    graph = to_float32(graph)

    # We have zero or negative values which are non-phyiscal, only temperature may be negative
    # as a result we need to map from celcius to kelvin before updaging the mask
    if handle_temperature: graph = celcius_to_kelvin(graph)
    
    graph = update_masks(graph)
    
    if handle_temperature: graph = kelvin_to_celcius(graph)

    graph = apply_masks(graph)

    if scale == "quantile":
        graph = quantile_scale(graph)
    elif scale == "min_max":
        graph = min_max_scale(graph)
    
    graph = nan_to_zero(graph)

    return graph


def inverse_scale(graph: "torch_geometric.Data") -> "torch_geometric.Data":
    """Inverse transform the scaled graph data back to its original form."""

    # Retrieve the min and max values per feature from the graph
    x_min = graph.x_min  # Shape: (num_features,)
    x_max = graph.x_max  # Shape: (num_features,)

    x = graph.x
    y = graph.y

    num_features = graph.x.size(2)
    num_targets = graph.y.size(2)

    # Inverse scale x (in-place)
    for feature_idx in range(num_features):
        # Extract the feature slice and its corresponding mask
        feature_slice = x[:, :, feature_idx]
        # apply scaling using the same min and max values from x
        x[:, :, feature_idx] = feature_slice * (x_max[feature_idx] - x_min[feature_idx]) + x_min[feature_idx]

    # Inverse scale y (in-place) using the same min and max values from x
    for feature_idx in range(num_targets):
        # Extract the feature slice and its corresponding mask
        feature_slice = y[:, :, feature_idx]
        # apply scaling using the same min and max values from x
        y[:, :, feature_idx] = feature_slice * (x_max[feature_idx] - x_min[feature_idx]) + x_min[feature_idx]

    graph.x = x
    graph.y = y

    return graph

def inverse_scale_predictions(predictions: "torch.Tensor", graph: "torch_geometric.Data") -> "torch_geometric.Data":
    """Inverse transform the scaled graph data back to its original form."""

    # Retrieve the min and max values per feature from the graph
    x_min = graph.x_min  # Shape: (num_features,)
    x_max = graph.x_max  # Shape: (num_features,)

    num_targets = graph.y.size(2)

    # Inverse scale y using the same min and max values from x
    for feature_idx in range(num_targets):
        # Extract the feature slice (we do not have a mask for the predictions)
        feature_slice = predictions[:, :, feature_idx]
        # Scale using the same min and max values from x
        predictions[:, :, feature_idx] = feature_slice * (x_max[feature_idx] - x_min[feature_idx]) + x_min[feature_idx]

    return predictions
