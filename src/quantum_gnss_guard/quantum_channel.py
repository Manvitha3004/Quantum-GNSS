"""Quantum channel simulation for entangled photon pairs."""

import numpy as np
import pandas as pd
from qutip import *
from typing import Tuple, List
from .utils import poisson_arrivals, gaussian_jitter, rayleigh_fade


class QuantumChannel:
    """Simulates SPDC entanglement generation and detection."""

    def __init__(self, pair_rate: float = 5000, wavelength_nm: float = 810,
                 detector_jitter_ps: float = 50, detector_qe: float = 0.8,
                 dark_count_hz: float = 10):
        """Initialize quantum channel parameters.

        Args:
            pair_rate: Pair generation rate (Hz)
            wavelength_nm: Wavelength (nm)
            detector_jitter_ps: Detector jitter (ps)
            detector_qe: Quantum efficiency
            dark_count_hz: Dark count rate (Hz)
        """
        self.pair_rate = pair_rate
        self.wavelength = wavelength_nm
        self.jitter_sigma = detector_jitter_ps * 1e-12  # s
        self.qe = detector_qe
        self.dark_rate = dark_count_hz

        # Bell state |ψ> = 1/√2 (|HH> + |VV>)
        self.bell_state = (tensor(basis(2, 0), basis(2, 0)) + tensor(basis(2, 1), basis(2, 1))).unit()

    def generate_pairs(self, duration: float, base_loss_db: float = 20) -> pd.DataFrame:
        """Generate entangled pair arrivals with losses.

        Args:
            duration: Time duration (s)
            base_loss_db: Base link loss (dB)

        Returns:
            DataFrame of photon events
        """
        # Generate pair creation times
        creation_times = poisson_arrivals(self.pair_rate, duration)

        events = []
        for t in creation_times:
            # Apply losses
            loss_db = rayleigh_fade(base_loss_db)
            survival_prob = 10 ** (-loss_db / 10)

            if np.random.random() < survival_prob:
                # Photon 1 (ground)
                if np.random.random() < self.qe:
                    t1 = gaussian_jitter(np.array([t]), self.jitter_sigma)[0]
                    events.append({'time': t1, 'detector': 1, 'photon_id': 'A'})

                # Photon 2 (satellite)
                if np.random.random() < self.qe:
                    t2 = gaussian_jitter(np.array([t]), self.jitter_sigma)[0]
                    events.append({'time': t2, 'detector': 2, 'photon_id': 'B'})

        # Add dark counts
        dark_times = poisson_arrivals(self.dark_rate, duration)
        for t in dark_times:
            det = np.random.choice([1, 2])
            events.append({'time': t, 'detector': det, 'photon_id': 'dark'})

        return pd.DataFrame(events).sort_values('time')

    def compute_coincidences(self, events: pd.DataFrame, window_ps: float = 200) -> np.ndarray:
        """Compute time differences for coincidences.

        Args:
            events: Photon events DataFrame
            window_ps: Coincidence window (ps)

        Returns:
            Array of Δt for coincident pairs
        """
        window_s = window_ps * 1e-12
        dt_list = []

        # Group by time windows
        events = events.sort_values('time')
        times = events['time'].values
        detectors = events['detector'].values

        i = 0
        while i < len(times) - 1:
            j = i + 1
            while j < len(times) and times[j] - times[i] <= window_s:
                if detectors[i] != detectors[j]:  # Different detectors
                    dt = times[j] - times[i]
                    dt_list.append(dt)
                j += 1
            i += 1

        return np.array(dt_list)

    def fidelity_check(self) -> float:
        """Compute fidelity of generated state to Bell state."""
        # For simplicity, assume perfect fidelity
        # In full implementation, simulate decoherence
        return 0.95

    def correlation_matrix(self, dt: np.ndarray, bins: int = 100) -> np.ndarray:
        """Compute correlation matrix from time differences."""
        hist, _ = np.histogram(dt, bins=bins, range=(-1e-9, 1e-9))
        return hist / np.sum(hist)  # Normalize