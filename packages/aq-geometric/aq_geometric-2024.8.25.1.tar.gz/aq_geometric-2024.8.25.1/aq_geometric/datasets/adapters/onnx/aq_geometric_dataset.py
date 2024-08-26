from datetime import datetime
from typing import Callable, Optional, Iterator, Union, Tuple

import numpy as np

from aq_geometric.datasets.in_memory.aq_geometric_dataset import AqGeometricInMemoryDataset
from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset
from aq_geometric.datasets.adapters.base_adapter import BaseDatasetAdapter
from aq_geometric.datasets.utilities.data.transforms import load_from_graph


class OnnxDatasetAdapter(BaseDatasetAdapter):
    def __init__(
        self,
        base_dataset: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
        transform: Optional[Callable] = None,
        batch_size: int = 32,
        verbose: bool = False,
    ):
        self.base_dataset = base_dataset
        self.transform = transform
        self.batch_size = batch_size
        self.verbose = verbose

        self.__getitem__ = self.__indexed_getitem__

    def __indexed_getitem__(self, idx):
        """Compute the graph for index idx using data from disk."""
        # obtain the data from the underlying dataset
        data = self.base_dataset.get(idx)

        # we need to case `x`, `y`, `edge_index`, `edge_attr`, and `...mask` to torch.Tensor
        data["x"] = data["x"].astype(np.float32)
        data["y"] = data["y"].astype(np.float32)
        data["edge_index"] = data["edge_index"].astype(np.float32)
        data["edge_attr"] = data["edge_attr"].astype(np.float32) if "edge_attr" in data and data["edge_attr"] is not None else None
        for k in data:
            if "mask" in k:
                data[k] = data[k].astype(np.float32)
        
        pyg_data = Data(**data)
        pyg_data.validate()

        if self.transform is not None:
            pyg_data = self.transform(pyg_data)

        return pyg_data

    def get_dataset_iterator(
        self,
        include_masks_in_features: bool,
        include_masks_in_targets: bool,
        reshape_order: str,
        num_samples_in_node_feature: int,
        num_features_in_node_feature: int,
        num_samples_in_node_target: int,
        num_features_in_node_target: int,
        onnx_input_name: Optional[str],
        verbose: bool = False,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """Creates an iterator that yields LightGBM datasets in batches."""
        for i in range(0, len(self.base_dataset), self.batch_size):
            X, y = None, None
            batch_indices = self.base_dataset.indices[i : i + self.batch_size]

            if self.verbose:
                print(f"[{datetime.now()}] Developing batch {i}")

            for idx in batch_indices:
                _, X_part, y_part = load_from_graph(
                    graph=self.base_dataset.get(idx),
                    include_target=True,
                    verbose=verbose,
                    include_masks_in_targets=include_masks_in_features,
                    include_masks_in_features=include_masks_in_targets,
                    reshape_order=reshape_order,
                    num_samples_in_node_feature=num_samples_in_node_feature,
                    num_features_in_node_feature=num_features_in_node_feature,
                    num_samples_in_node_target=num_samples_in_node_target,
                    num_features_in_node_target=num_features_in_node_target,
                )
                if X is None:
                    X = X_part
                    y = y_part
                else:
                    X = np.concatenate((X, X_part), axis=0)
                    y = np.concatenate((y, y_part), axis=0)
            
            if self.verbose:
                print(f"[{datetime.now()}] Yeilding batch {i} with X {np.shape(X)}) and Y ({np.shape(y)})")

            if onnx_input_name is not None:
                yield {onnx_input_name: X.astype(np.float32)}
            else:
                yield X, y
