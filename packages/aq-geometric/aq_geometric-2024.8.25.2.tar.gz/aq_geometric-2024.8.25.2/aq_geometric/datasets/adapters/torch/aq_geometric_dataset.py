from datetime import datetime
from typing import Callable, Optional

import torch
from torch_geometric.data import Dataset, Data

from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset


class TorchGeometricDatasetAdapter(Dataset):
    def __init__(
        self,
        root: str,
        base_dataset: AqGeometricDataset,
        transform: Optional[Callable] = None,
        pre_transform: Optional[Callable] = None,
        pre_filter: Optional[Callable] = None,
    ):
        self.base_dataset = base_dataset

        super().__init__(root, transform, pre_transform, pre_filter)

        self.__getitem__ = self.__indexed_getitem__
    
    @property
    def raw_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.raw_file_names

    @property
    def processed_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.processed_file_names

    def clear(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.clear()

    def download(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.download()

    def process(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.process()

    def len(self):
        return len(self.base_dataset.indices)

    def get(self, idx):
        """Obtain a graph from the dataset."""
        # ensure we have the graph index ranges
        assert idx in self.base_dataset.indices, f"Index {idx} is not in dataset indices."
        if self.base_dataset.verbose:
            print(
                f"[{datetime.now()}] Getting graph {idx} of {self.base_dataset.indices[-1]}")
        return self.__indexed_getitem__(idx)

    def __indexed_getitem__(self, idx):
        """Compute the graph for index idx using data from disk."""
        # obtain the data from the underlying dataset
        data = self.base_dataset.get(idx)
        # we need to case `x`, `y`, `edge_index`, `edge_attr`, and `...mask` to torch.Tensor
        data["x"] = torch.from_numpy(data["x"])
        data["y"] = torch.from_numpy(data["y"])
        data["edge_index"] = torch.from_numpy(data["edge_index"])
        data["edge_attr"] = torch.from_numpy(data["edge_attr"]) if "edge_attr" in data and data["edge_attr"] is not None else None
        for k in data:
            if "mask" in k:
                data[k] = torch.from_numpy(data[k])
        
        pyg_data = Data(**data)
        pyg_data.validate()

        if self.transform is not None:
            pyg_data = self.transform(pyg_data)
        return pyg_data
