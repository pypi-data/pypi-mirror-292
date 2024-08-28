from abc import ABC, abstractmethod
from caafg.dataset import Dataset


class AbstractGenerator(ABC):
    """
    An abstract interface class providing functionalities for generating new
    features using a given method.
    """

    def __init__(self) -> None:
        """
        Initialize the generator object.
        """
        raise NotImplementedError

    @abstractmethod
    def ask(self,
            dataset: Dataset,
            n_features: int):
        """
        Ask the generator to generate a new sample.
        """
        raise NotImplementedError

    @abstractmethod
    def tell(self):
        """
        Update the feedback states of the generator based on the feedback.
        """
        raise NotImplementedError

    @abstractmethod
    def transform(self):
        """
        Transform the dataset by applying the generated feature
        transformations.
        """
        raise NotImplementedError

    @abstractmethod
    def _generate(self):
        """
        Generate a new features by interfering the generator.
        """
        raise NotImplementedError
