from abc import ABC, abstractmethod

from ...data import Split


class LogWriter(ABC):
    """
    Abstract base class to standardize api for different logging methods.
    """

    @staticmethod
    def get_prefix(split: Split, category: str | None = None) -> str:
        """Prefix for string path logging i.e. prefix=split(/category)"""
        prefix = split.name.lower()
        if category is not None:
            prefix += f"/{category}"
        return prefix

    @abstractmethod
    def __call__(
        self,
        split: Split,
        iteration: int,
        data: dict[str, float],
        category: str | None = None,
    ) -> None:
        """Add basic keyword-value data to logs"""

    @abstractmethod
    def flush(self):
        """Flush logger data to disk if applicable"""

    @abstractmethod
    def add_topic(self, category: str, column_names: list[str]):
        """
        Pre-declare categories with column names.
        Required for backends that can't dynamically add more columns
        if not all columns are logged on the first iteration.
        """


class MultiWriter(LogWriter):
    """Forwards write to multple backends"""

    def __init__(self, writers: list[LogWriter]) -> None:
        self.writers = writers

    def __call__(
        self,
        split: Split,
        iteration: int,
        data: dict[str, float],
        category: str | None = None,
    ) -> None:
        for writer in self.writers:
            writer(split, iteration, data, category)

    def add_topic(self, category: str, column_names: list[str]):
        for writer in self.writers:
            writer.add_topic(category, column_names)

    def flush(self):
        for writer in self.writers:
            writer.flush()
