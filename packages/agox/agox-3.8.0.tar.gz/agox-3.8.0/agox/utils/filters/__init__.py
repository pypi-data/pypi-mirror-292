"""
This module contains the filters that can be used to filter candidate (or ase.Atoms) objects. 
This is useful for filtering out candidates that are not interesting, e.g. if the energy is too high.
"""


from .ABC_filter import FilterBaseClass
from .all import AllFilter
from .none import NoneFilter
from .energy import EnergyFilter
from .ABC_filter import FilterBaseClass, SumFilter
from .kmeans_energy import KMeansEnergyFilter
from .sparse_filter import SparsifierFilter
from .random import RandomFilter
from .voronoi import VoronoiFilter

__all__ = ['FilterBaseClass',
            'AllFilter',
            'NoneFilter',
            'EnergyFilter',
            'SumFilter',
            'KMeansEnergyFilter',
            'SparsifierFilter',
            'RandomFilter',
            'VoronoiFilter',
        ]