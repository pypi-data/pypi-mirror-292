from datetime import datetime
from typing import Callable, Optional, Iterator, Tuple

import numpy as np

from aq_geometric.datasets.on_disk.aq_geometric_dataset import AqGeometricDataset


class NumpyDatasetAdapter:
    def __init__(
        self,
        base_dataset: AqGeometricDataset,
        batch_size: int = 32,
        transform: Optional[Callable] = None,
        verbose: bool = False,
    ):
        self.base_dataset = base_dataset
        self.batch_size = min(batch_size, len(self.base_dataset))
        self.transform = transform
        self.verbose = verbose
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

    def __len__(self):
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

        if self.transform:
            if self.verbose:
                print(f"[{datetime.now()}] Transforming graph {idx} of {self.base_dataset.indices[-1]}")
            data = self.transform(data)

        X = data["x"]
        y = data["y"]

        if self.verbose:
            print(
                f"[{datetime.now()}] Getting graph {idx} of {self.base_dataset.indices[-1]}")

        return X, y

    def get_dataset_iterator(
        self,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """Creates an iterator that yields LightGBM datasets in batches."""
        for i in range(0, len(self.base_dataset), self.batch_size):
            X, y = None, None
            batch_indices = self.base_dataset.indices[i : i + self.batch_size]

            if self.verbose:
                print(f"[{datetime.now()}] Developing batch {i}")

            for idx in batch_indices:
                X_part, y_part = self.__indexed_getitem__(idx)
                if X is None:
                    X = X_part
                    y = y_part
                else:
                    X = np.concatenate((X, X_part), axis=0)
                    y = np.concatenate((y, y_part), axis=0)
            
            if self.verbose:
                print(f"[{datetime.now()}] Yielding batch {i} with X ({np.shape(X)}) and Y ({np.shape(y)})")

            yield X, y
