"""Utility functions for Quantum GNSS Guard."""

import numpy as np
from scipy import stats
from typing import Tuple, List


def poisson_arrivals(rate: float, duration: float) -> np.ndarray:
    """Generate Poisson arrival times.

    Args:
        rate: Arrival rate (Hz)
        duration: Time duration (s)

    Returns:
        Array of arrival times
    """
    n_events = np.random.poisson(rate * duration)
    return np.sort(np.random.uniform(0, duration, n_events))


def gaussian_jitter(times: np.ndarray, sigma: float) -> np.ndarray:
    """Add Gaussian jitter to timestamps.

    Args:
        times: Original timestamps
        sigma: Jitter standard deviation (s)

    Returns:
        Jittered timestamps
    """
    return times + np.random.normal(0, sigma, len(times))


def hellinger_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Compute Hellinger distance between two distributions.

    Args:
        p, q: Probability distributions (same length)

    Returns:
        Hellinger distance
    """
    return np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q))**2)) / np.sqrt(2)


def coincidence_histogram(dt: np.ndarray, bins: int = 100, range_ns: Tuple[float, float] = (-5, 5)) -> Tuple[np.ndarray, np.ndarray]:
    """Compute coincidence histogram of time differences.

    Args:
        dt: Time differences (s)
        bins: Number of bins
        range_ns: Range in nanoseconds

    Returns:
        Bin edges and counts
    """
    range_s = (range_ns[0] * 1e-9, range_ns[1] * 1e-9)
    counts, edges = np.histogram(dt, bins=bins, range=range_s)
    return edges, counts


def link_budget(tx_power_dbm: float, distance_km: float, frequency_ghz: float,
                atm_loss_db_per_km: float = 0.2, scintillation_db: float = 0.5) -> float:
    """Compute link budget in dB.

    Args:
        tx_power_dbm: Transmit power (dBm)
        distance_km: Distance (km)
        frequency_ghz: Frequency (GHz)
        atm_loss_db_per_km: Atmospheric loss (dB/km)
        scintillation_db: Scintillation loss (dB)

    Returns:
        Received power (dBm)
    """
    fspl = 20 * np.log10(distance_km) + 20 * np.log10(frequency_ghz) + 92.45
    atm_loss = atm_loss_db_per_km * distance_km
    return tx_power_dbm - fspl - atm_loss - scintillation_db


def rayleigh_fade(loss_db: float) -> float:
    """Apply Rayleigh fading to loss.

    Args:
        loss_db: Base loss (dB)

    Returns:
        Faded loss (dB)
    """
    fade = np.random.rayleigh(1)  # Scale parameter
    return loss_db + 20 * np.log10(fade)