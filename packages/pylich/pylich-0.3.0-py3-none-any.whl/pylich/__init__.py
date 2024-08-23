import importlib.metadata

__version__ = importlib.metadata.version("pylich")

from .checker import LinkChecker

__all__ = ["pylich", "LinkChecker"]
