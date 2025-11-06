"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from quantum_gnss_guard.simulator import Simulator


@pytest.fixture
def sample_config():
    """Sample simulator configuration."""
    return {
        'tle_file': 'data/tle_sample.txt',
        'station_loc': [40.0, -74.0, 0.0],
        'pair_rate': 1000,
        'attacks': [{'attack_type': 'time-push'}]
    }


@pytest.fixture
def sample_simulator(sample_config):
    """Sample simulator instance."""
    return Simulator(sample_config)


@pytest.fixture
def sample_tle():
    """Sample TLE data."""
    return """ISS (ZARYA)
1 25544U 98067A   23165.12345678  .00000000  00000-0  00000-0 0  9999
2 25544  51.6400  12.3456 0001000  90.0000 270.0000 15.50000000  9999"""


@pytest.fixture
def sample_quantum_events():
    """Sample quantum photon events."""
    return np.random.exponential(0.001, 1000)  # Times in seconds