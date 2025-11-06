"""Tests for spoofing module."""

import numpy as np
from quantum_gnss_guard.gnss_spoof import GNSSSpoof


def test_spoof_init():
    """Test spoof initialization."""
    config = {'attack_type': 'time-push', 'delta_ns': 10}
    spoof = GNSSSpoof(config)
    assert spoof.attack_type == 'time-push'
    assert spoof.delta_ns == 10


def test_apply_spoof_time_push():
    """Test time-push spoofing."""
    config = {'attack_type': 'time-push', 'delta_ns': 10, 'spoof_rate': 1.0}
    spoof = GNSSSpoof(config)

    gnss_times = np.array([0.0, 1.0, 2.0])
    quantum_dt = np.array([0.0, 0.0, 0.0])

    spoofed_gnss, spoofed_dt = spoof.apply_spoof(gnss_times, quantum_dt)

    # All should be shifted
    assert np.allclose(spoofed_gnss, gnss_times + 10e-9)
    assert np.allclose(spoofed_dt, quantum_dt + 10e-9, atol=1e-10)


def test_apply_spoof_replica():
    """Test replica spoofing."""
    config = {'attack_type': 'replica', 'spoof_rate': 1.0}
    spoof = GNSSSpoof(config)

    gnss_times = np.array([0.0, 1.0])
    quantum_dt = np.array([0.0, 0.0])

    spoofed_gnss, spoofed_dt = spoof.apply_spoof(gnss_times, quantum_dt)

    # Should have some offset
    assert not np.allclose(spoofed_gnss, gnss_times)


def test_nmea_spoof():
    """Test NMEA spoofing."""
    config = {'attack_type': 'time-push', 'delta_ns': 1}
    spoof = GNSSSpoof(config)

    original = ['$GPGGA,123456,40.0,N,74.0,W,1,1,1,0,M,0,M,,*00']
    spoofed = spoof.generate_nmea_spoofed(original)

    assert len(spoofed) == 1
    # Time should be modified
    assert spoofed[0] != original[0]