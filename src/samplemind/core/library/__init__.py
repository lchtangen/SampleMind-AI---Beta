"""
SampleMind AI — Library Management Module

Favorites collections and sample pack creation tools.
"""

from .favorites import Collection, CollectionType, FavoritesManager
from .pack_creator import PackTemplate, SamplePack, SamplePackCreator

__all__ = [
    "FavoritesManager",
    "Collection",
    "CollectionType",
    "SamplePackCreator",
    "SamplePack",
    "PackTemplate",
]
