"""Main simulator orchestrating all components."""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List
from .orbital import Orbital
from .quantum_channel import QuantumChannel
from .gnss_spoof import GNSSSpoof
from .detector import Detector
from .utils import coincidence_histogram


class Simulator:
    """End-to-end GNSS spoofing detection simulator."""

    def __init__(self, config: Dict):
        """Initialize simulator with configuration.

        Args:
            config: Simulation parameters
        """
        self.config = config
        self.orbital = Orbital(
            config['tle_file'],
            config['station_loc'][0],
            config['station_loc'][1],
            config['station_loc'][2]
        )
        self.quantum = QuantumChannel(
            pair_rate=config.get('pair_rate', 5000),
            wavelength_nm=config.get('wavelength_nm', 810),
            detector_jitter_ps=config.get('detector_jitter_ps', 50),
            detector_qe=config.get('detector_qe', 0.8)
        )
        self.spoof_configs = config.get('attacks', [{'attack_type': 'time-push'}])
        self.detector = Detector()

    def run_single_pass(self, pass_info: pd.Series, attack_config: Dict) -> Dict:
        """Run simulation for a single pass.

        Args:
            pass_info: Pass information
            attack_config: Attack parameters

        Returns:
            Results dictionary
        """
        # Generate quantum events
        duration = pass_info['duration_min'] * 60
        events = self.quantum.generate_pairs(duration)

        # Extract coincidences
        dt = self.quantum.compute_coincidences(events)

        # Simulate GNSS times (simplified)
        gnss_times = np.linspace(0, duration, len(dt))

        # Apply spoofing
        spoof = GNSSSpoof(attack_config)
        spoofed_gnss, spoofed_dt = spoof.apply_spoof(gnss_times, dt)

        # Detect
        detection_result = self.detector.detect(spoofed_dt)

        return {
            'pass_id': f"{pass_info['satellite']}_{pass_info['rise_time'].isoformat()}",
            'attack_type': attack_config['attack_type'],
            'n_pairs': len(dt),
            'detection_score': detection_result['combined_score'],
            'decision': detection_result['decision'],
            'tpr': detection_result['combined_score'],  # Simplified
            'fpr': 1 - detection_result['combined_score']  # Simplified
        }

    def run(self, mc_runs: int = 100) -> pd.DataFrame:
        """Run Monte Carlo simulation.

        Args:
            mc_runs: Number of Monte Carlo runs

        Returns:
            Results DataFrame
        """
        # Get passes
        start_time = datetime.now()
        passes = self.orbital.compute_passes(start_time)

        results = []
        for _ in range(mc_runs):
            for _, pass_info in passes.iterrows():
                for attack_config in self.spoof_configs:
                    result = self.run_single_pass(pass_info, attack_config)
                    results.append(result)

        return pd.DataFrame(results)

    def plot_roc(self, results: pd.DataFrame):
        """Generate ROC plot (placeholder)."""
        # Use matplotlib/plotly for actual plotting
        print("ROC plotting not implemented in this stub")

    def export_results(self, results: pd.DataFrame, output_dir: str):
        """Export results to files.

        Args:
            results: Results DataFrame
            output_dir: Output directory
        """
        results.to_csv(f"{output_dir}/simulation_results.csv", index=False)
        results.to_json(f"{output_dir}/simulation_results.json", orient='records')