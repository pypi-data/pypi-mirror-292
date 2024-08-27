"""Registries."""

from typing import List

from cyberfusion.SoftwareDiscoverer.exceptions import DiscovererNotFoundError
from cyberfusion.SoftwareDiscoverer.interfaces import DiscovererInterface


class DiscovererRegistry:
    """Registry of discoverers."""

    def __init__(self) -> None:
        """Set attributes."""
        self.discoverers: List[DiscovererInterface] = []

    def add(self, discoverers: List[DiscovererInterface]) -> None:
        """Add discoverers."""
        for discoverer in discoverers:
            self.discoverers.append(discoverer())

    def get(self, discoverer: DiscovererInterface) -> DiscovererInterface:
        """Get single discoverer."""
        for d in self.discoverers:
            if not isinstance(d, discoverer):
                continue

            return d

        raise DiscovererNotFoundError


discoverer_registry = DiscovererRegistry()
