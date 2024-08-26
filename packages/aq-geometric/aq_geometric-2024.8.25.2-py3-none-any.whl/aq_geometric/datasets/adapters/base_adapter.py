from datetime import datetime
from typing import Union

from aq_geometric.datasets.in_memory.aq_geometric_dataset import AqGeometricInMemoryDataset
from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset


class BaseDatasetAdapter:
    def __init__(
        self,
        base_dataset: Union[AqGeometricInMemoryDataset, AqGeometricDataset],
    ):
        self.base_dataset = base_dataset

        self.__getitem__ = self.__indexed_getitem__

    @property
    def raw_file_names(self) -> list:
        return self.base_dataset.raw_file_names

    @property
    def processed_file_names(self) -> list:
        return self.base_dataset.processed_file_names

    def len(self):
        return len(self.base_dataset.indices)

    def clear(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.clear()

    def download(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.download()

    def process(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return self.base_dataset.process()

    def get(self, idx):
        """Obtain a graph from the dataset."""
        # ensure we have the graph index ranges
        assert idx < self.base_dataset.num_graphs, f"Index {idx} is out of range for the number of graphs {self.base_dataset.num_graphs-1}."

        if self.base_dataset.verbose:
            print(
                f"[{datetime.now()}] Getting graph {idx} of {self.base_dataset.indices[-1]}")
        return self.__indexed_getitem__(idx)

    def __indexed_getitem__(self, idx):
        """Compute the graph for index idx using data from disk."""
        raise NotImplementedError("subsclases must implement an `__indexed_getitem__` method")
