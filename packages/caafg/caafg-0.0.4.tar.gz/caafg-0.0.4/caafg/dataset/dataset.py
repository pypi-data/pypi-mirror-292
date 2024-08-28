import pandas as pd
from dataclasses import dataclass


@dataclass
class Dataset:
    """
    A simple class to represent a dataset.
    """
    X: pd.DataFrame
    y: pd.Series | None
    dataset_name: str | None
    dataset_description: str | None
    feature_names: list[str] | None

    def __init__(self,
                 X: pd.DataFrame,
                 y: pd.Series = None,
                 dataset_name: str = None,
                 dataset_description: str = None) -> None:
        """
        Initialize the dataset object. This object holds all relevant (meta-)
        data representing the dataset.

        Parameters
        ----------
        X : pd.DataFrame
            The input features of the dataset.
        y: pd.Series
            The target values of the dataset.
        dataset_name : str
            The name of the dataset.
        dataset_description : str
            A short description of the dataset.
        """
        self.X = X
        self.y = y
        self.dataset_name = dataset_name
        self.dataset_description = dataset_description
