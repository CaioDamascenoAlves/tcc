"""
Core module - Módulos reutilizáveis do projeto.
"""

from .data_loader import DataLoader
from .metrics import MetricsCalculator

__all__ = [
    'DataLoader',
    'MetricsCalculator',
]
