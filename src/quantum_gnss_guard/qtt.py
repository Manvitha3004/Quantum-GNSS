"""Quantum Time Transfer (QTT) module for sub-picosecond clock synchronization."""

import numpy as np
from qutip import *
from scipy.optimize import minimize_scalar
from typing import Tuple, Dict, List
import pandas as pd
from .utils import gaussian_jitter


class QuantumTimeTransfer:
    """Implements quantum time transfer protocols using entangled photons."""

    def __init__(self, sync_rate: float = 1000, precision_ps: float = 0.1):
        """Initialize QTT system.
        
        Args:
            sync_rate: Synchronization rate (Hz)
            precision_ps: Target precision (ps)
        """
        self.sync_rate = sync_rate
        self.precision = precision_ps * 1e-12  # Convert to seconds
        
        # Create maximally entangled Bell state |Ψ⁺⟩ = (|00⟩ + |11⟩)/√2
        self.bell_state = (tensor(basis(2, 0), basis(2, 0)) + 
                          tensor(basis(2, 1), basis(2, 1))).unit()
        
        # Phase estimation parameters
        self.phase_resolution = 2 * np.pi / 1000  # mrad resolution

    def generate_sync_pulses(self, duration: float, gnss_times: np.ndarray) -> pd.DataFrame:
        """Generate quantum sync pulses correlated with GNSS timing.
        
        Args:
            duration: Simulation duration (s)
            gnss_times: GNSS timestamp array
            
        Returns:
            DataFrame with sync events
        """
        # Generate sync pulse times
        n_pulses = int(duration * self.sync_rate)
        pulse_times = np.sort(np.random.uniform(0, duration, n_pulses))
        
        events = []
        for i, t_pulse in enumerate(pulse_times):
            # Find closest GNSS time for correlation
            gnss_idx = np.argmin(np.abs(gnss_times - t_pulse))
            gnss_ref = gnss_times[gnss_idx]
            
            # Quantum phase measurement with Bell pairs
            phase = self._measure_phase(t_pulse)
            
            # Convert phase to time offset with sub-ps precision
            time_offset = self._phase_to_time(phase)
            
            events.append({
                'pulse_time': t_pulse,
                'gnss_ref': gnss_ref,
                'quantum_phase': phase,
                'time_offset': time_offset,
                'sync_error': time_offset - (t_pulse - gnss_ref)
            })
            
        return pd.DataFrame(events)

    def _measure_phase(self, t: float) -> float:
        """Simulate quantum phase measurement using Bell state interferometry.
        
        Args:
            t: Measurement time
            
        Returns:
            Measured phase (rad)
        """
        # Simulate phase evolution with environmental noise
        ideal_phase = 2 * np.pi * t * self.sync_rate / 100  # Arbitrary frequency
        
        # Add quantum shot noise and decoherence
        shot_noise = np.random.normal(0, self.phase_resolution)
        decoherence = np.random.exponential(0.1) * 1e-3  # Weak decoherence
        
        return (ideal_phase + shot_noise + decoherence) % (2 * np.pi)

    def _phase_to_time(self, phase: float) -> float:
        """Convert quantum phase to time offset using phase estimation.
        
        Args:
            phase: Measured phase (rad)
            
        Returns:
            Time offset (s)
        """
        # Quantum Fourier transform estimation
        # Simplified: phase ~ 2π * Δt * frequency
        frequency = 1e12  # 1 THz reference (optical frequency)
        time_offset = phase / (2 * np.pi * frequency)
        
        # Add measurement uncertainty
        uncertainty = np.random.normal(0, self.precision)
        return time_offset + uncertainty

    def detect_sync_anomalies(self, sync_events: pd.DataFrame, threshold_ps: float = 1.0) -> Dict:
        """Detect timing anomalies in quantum sync data.
        
        Args:
            sync_events: DataFrame of sync measurements
            threshold_ps: Detection threshold (ps)
            
        Returns:
            Detection results
        """
        threshold = threshold_ps * 1e-12
        sync_errors = sync_events['sync_error'].values
        
        # Statistical analysis of sync errors
        mean_error = np.mean(sync_errors)
        std_error = np.std(sync_errors)
        
        # Detect outliers using 3-sigma rule
        outliers = np.abs(sync_errors - mean_error) > 3 * std_error
        
        # Chi-squared test for drift
        chi2_stat = np.sum((sync_errors - mean_error)**2) / (std_error**2 + 1e-20)
        
        # Anomaly score based on deviation from expected distribution
        anomaly_score = min(1.0, chi2_stat / len(sync_errors))
        
        return {
            'mean_error_ps': mean_error * 1e12,
            'std_error_ps': std_error * 1e12,
            'n_outliers': np.sum(outliers),
            'outlier_fraction': np.mean(outliers),
            'chi2_statistic': chi2_stat,
            'anomaly_score': anomaly_score,
            'detection': anomaly_score > 0.5
        }

    def simulate_decoherence(self, t_list: np.ndarray, T1: float = 1e-3, T2: float = 5e-4) -> np.ndarray:
        """Simulate quantum decoherence effects on entangled states.
        
        Args:
            t_list: Time array
            T1: Amplitude damping time (s)
            T2: Dephasing time (s)
            
        Returns:
            Fidelity array
        """
        # Exponential decay model
        amplitude_decay = np.exp(-t_list / T1)
        phase_decay = np.exp(-t_list / T2)
        
        # Combined fidelity loss
        fidelity = amplitude_decay * phase_decay * 0.5 + 0.5  # Bell state fidelity
        
        return np.clip(fidelity, 0, 1)

    def estimate_clock_drift(self, sync_events: pd.DataFrame, window_size: int = 100) -> np.ndarray:
        """Estimate clock drift using sliding window analysis.
        
        Args:
            sync_events: Sync measurement data
            window_size: Analysis window size
            
        Returns:
            Drift estimate array (s/s)
        """
        errors = sync_events['sync_error'].values
        times = sync_events['pulse_time'].values
        
        drift_estimates = []
        
        for i in range(len(errors) - window_size):
            window_times = times[i:i+window_size]
            window_errors = errors[i:i+window_size]
            
            # Linear regression for drift estimation
            coeffs = np.polyfit(window_times, window_errors, 1)
            drift_estimates.append(coeffs[0])  # Slope = drift rate
            
        return np.array(drift_estimates)