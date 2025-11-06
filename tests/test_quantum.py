"""Tests for quantum channel module."""

import numpy as np
import pandas as pd
from quantum_gnss_guard.quantum_channel import QuantumChannel


def test_quantum_init():
    """Test quantum channel initialization."""
    qc = QuantumChannel(pair_rate=1000)
    assert qc.pair_rate == 1000
    assert qc.wavelength == 810


def test_generate_pairs():
    """Test pair generation."""
    qc = QuantumChannel(pair_rate=1000)
    events = qc.generate_pairs(duration=1.0)  # 1 second

    assert isinstance(events, pd.DataFrame)
    assert 'time' in events.columns
    assert 'detector' in events.columns
    # Should have some events
    assert len(events) > 0


def test_compute_coincidences():
    """Test coincidence computation."""
    qc = QuantumChannel()

    # Create fake events
    events = pd.DataFrame({
        'time': [0.0, 0.1e-9, 0.5, 0.5001e-9],  # Two pairs
        'detector': [1, 2, 1, 2],
        'photon_id': ['A', 'B', 'A', 'B']
    })

    dt = qc.compute_coincidences(events, window_ps=200)
    assert len(dt) >= 1  # At least one coincidence


def test_fidelity():
    """Test fidelity check."""
    qc = QuantumChannel()
    fid = qc.fidelity_check()
    assert 0.9 <= fid <= 1.0