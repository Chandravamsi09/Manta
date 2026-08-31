"""
Manta: High-Performance Distributed Machine Learning Systems & MLOps Platform
"""

__version__ = "1.0.0"
__author__ = "Chandra Vamsi"
__email__ = "avvaruchandravamsi30@gmail.com"

from manta.core.config import MantaConfig, load_config
from manta.core.logging import get_logger
from manta.core.context import ExecutionContext
from manta.sdk.client import Client

__all__ = [
    "__version__",
    "__author__",
    "MantaConfig",
    "load_config",
    "get_logger",
    "ExecutionContext",
    "Client",
]
