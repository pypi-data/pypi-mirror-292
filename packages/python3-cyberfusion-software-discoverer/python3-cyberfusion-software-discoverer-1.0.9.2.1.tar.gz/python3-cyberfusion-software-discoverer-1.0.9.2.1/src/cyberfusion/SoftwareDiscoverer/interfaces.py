"""Interfaces."""

from abc import ABCMeta, abstractmethod, abstractproperty
from typing import List


class TraitInterface(metaclass=ABCMeta):  # noqa: B024
    """Interface for traits."""

    def __init__(self) -> None:  # noqa: B027
        """Do nothing."""
        pass


class DiscovererInterface(metaclass=ABCMeta):
    """Interface for discoverers."""

    def __init__(self) -> None:  # noqa: B027
        """Do nothing."""
        pass

    @abstractmethod
    def discover(self) -> bool:
        """Discover."""
        pass

    @abstractproperty
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        pass


class ConfigParserInterface(metaclass=ABCMeta):
    """Interface for config parsers."""

    def __init__(self) -> None:  # noqa: B027
        """Do nothing."""
        pass

    @staticmethod
    @abstractmethod
    def parse() -> dict:
        """Parse config."""
        pass
