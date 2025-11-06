"""Tests for orbital module."""

import pytest
import pandas as pd
from datetime import datetime
from quantum_gnss_guard.orbital import Orbital


def test_orbital_init(sample_tle, tmp_path):
    """Test orbital initialization."""
    tle_file = tmp_path / "tle.txt"
    tle_file.write_text(sample_tle)

    orb = Orbital(str(tle_file), 40, -74, 0)
    assert orb.station.latitude.degrees == 40
    assert orb.station.longitude.degrees == -74


def test_compute_passes(sample_tle, tmp_path):
    """Test pass computation."""
    tle_file = tmp_path / "tle.txt"
    tle_file.write_text(sample_tle)

    orb = Orbital(str(tle_file), 40, -74, 0)
    start = datetime(2023, 1, 1)
    passes = orb.compute_passes(start, duration_hours=1)

    assert isinstance(passes, pd.DataFrame)
    # Note: Actual passes depend on TLE and may be empty for test TLE


def test_link_budget():
    """Test link budget calculation."""
    from quantum_gnss_guard.utils import link_budget

    rx_power = link_budget(10, 500, 375)  # 500 km, 375 GHz
    assert rx_power < 10  # Should be attenuated
    assert rx_power > -100  # Not completely lost