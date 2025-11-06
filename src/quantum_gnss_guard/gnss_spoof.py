"""GNSS spoofing attack models."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from .utils import gaussian_jitter


class GNSSSpoof:
    """Models various GNSS spoofing attacks."""

    def __init__(self, config: Dict):
        """Initialize spoof parameters.

        Args:
            config: Spoof configuration
        """
        self.attack_type = config.get('attack_type', 'time-push')
        self.delta_ns = config.get('delta_ns', 10)  # ns
        self.noise_ps = config.get('noise_ps', 5)   # ps
        self.spoof_rate = config.get('spoof_rate', 0.5)  # Fraction of time spoofed

    def apply_spoof(self, gnss_times: np.ndarray, quantum_dt: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply spoofing to GNSS and quantum signals.

        Args:
            gnss_times: GNSS timestamps
            quantum_dt: Quantum time differences

        Returns:
            Spoofed GNSS times, spoofed quantum dt
        """
        n = len(gnss_times)
        spoof_mask = np.random.random(n) < self.spoof_rate

        spoofed_gnss = gnss_times.copy()
        spoofed_dt = quantum_dt.copy()

        if self.attack_type == 'time-push':
            # Shift GNSS times
            spoofed_gnss[spoof_mask] += self.delta_ns * 1e-9
            # For quantum, mimic the shift with noise
            spoofed_dt[spoof_mask] += (self.delta_ns * 1e-9 + np.random.normal(0, self.noise_ps * 1e-12, np.sum(spoof_mask)))

        elif self.attack_type == 'replica':
            # Replay authentic signals with phase offset
            offset = np.random.uniform(-100e-9, 100e-9)  # Random offset
            spoofed_gnss[spoof_mask] = gnss_times[spoof_mask] + offset
            spoofed_dt[spoof_mask] = quantum_dt[spoof_mask] + offset

        elif self.attack_type == 'hybrid':
            # Combine time-push and replica
            push_delta = self.delta_ns * 1e-9
            replica_offset = np.random.uniform(-50e-9, 50e-9)
            spoofed_gnss[spoof_mask] += push_delta + replica_offset
            spoofed_dt[spoof_mask] += push_delta + replica_offset + np.random.normal(0, self.noise_ps * 1e-12, np.sum(spoof_mask))

        return spoofed_gnss, spoofed_dt

    def generate_nmea_spoofed(self, original_nmea: List[str]) -> List[str]:
        """Generate spoofed NMEA messages.

        Args:
            original_nmea: Original NMEA sentences

        Returns:
            Spoofed NMEA sentences
        """
        # Simplified: modify TOW in GPGGA sentences
        spoofed = []
        for sentence in original_nmea:
            if sentence.startswith('$GPGGA'):
                parts = sentence.split(',')
                if len(parts) > 1:
                    # Modify time field (assuming HHMMSS format)
                    time_str = parts[1]
                    if len(time_str) == 6:
                        hours = int(time_str[:2])
                        mins = int(time_str[2:4])
                        secs = int(time_str[4:6])
                        total_secs = hours * 3600 + mins * 60 + secs
                        spoofed_secs = total_secs + self.delta_ns * 1e-9
                        spoofed_time = f"{int(spoofed_secs // 3600):02d}{int((spoofed_secs % 3600) // 60):02d}{int(spoofed_secs % 60):02d}"
                        parts[1] = spoofed_time
                        sentence = ','.join(parts)
            spoofed.append(sentence)
        return spoofed