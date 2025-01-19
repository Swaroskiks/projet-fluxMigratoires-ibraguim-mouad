"""Module for the application's utilities."""

from .get_data import download_all_species_data
from .clean_data import clean_all_species_data
from .data_manager import load_species_metadata, load_species_data_from_csv
from .stats_utils import (
    calculate_average_speed,
    calculate_max_amplitude,
    calculate_monthly_distances,
    calculate_total_distance,
    haversine_distance,
    calculate_migration_stats
)

__all__ = [
    'download_all_species_data',
    'clean_all_species_data',
    'load_species_metadata',
    'load_species_data_from_csv',
    'calculate_average_speed',
    'calculate_max_amplitude',
    'calculate_monthly_distances',
    'calculate_total_distance',
    'haversine_distance',
    'calculate_migration_stats'
]