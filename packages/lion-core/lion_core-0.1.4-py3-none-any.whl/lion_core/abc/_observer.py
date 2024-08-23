from abc import abstractmethod

from lion_core.abc._concept import AbstractObserver


class BaseManager(AbstractObserver):
    """
    High-level observers coordinating other observers and system
    components. Embodies emergent control in complex systems, where global
    behaviors arise from local interactions and observations.
    """

    pass


class BaseExecutor(AbstractObserver):
    """
    Active observers performing tasks based on observations. Inspired by
    measurement-induced state changes in quantum mechanics, where observation
    directly influences system state.
    """

    @abstractmethod
    async def forward(self, *args, **kwargs):
        """
        Asynchronously executes the observer's task, potentially altering
        system state. Models concurrent operations and parallel processing
        in complex, distributed systems.
        """
        pass


class BaseProcessor(AbstractObserver):
    """
    Specialized observers for information transformation and analysis.
    Embodies information processing in complex systems, paralleling quantum
    information theory and cognitive processing models.
    """

    @abstractmethod
    async def process(self, *args, **kwargs):
        """
        Asynchronously processes information based on observations.
        Encapsulates core information processing functionality, supporting
        continuous, real-time processing in dynamic systems.
        """
        pass

    # engine must have processor or executor


class BaseEngine(AbstractObserver):
    @abstractmethod
    async def run(self, *args, **kwargs):
        """Asynchronously runs the engine's core functionality."""
        pass


# Subclass must have access to intelligent model
class BaseiModel(AbstractObserver):
    """Base class for intelligent models in the framework."""

    @abstractmethod
    async def call(self, *args, **kwargs):
        """Asynchronously calls the model's core functionality."""
        pass


__all__ = [
    "BaseManager",
    "BaseExecutor",
    "BaseProcessor",
    "BaseiModel",
    "BaseEngine",
]

# File: lion_core/abc/observer.py
