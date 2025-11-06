"""Script to generate and export simulation dataset."""

import numpy as np
import pandas as pd
import h5py
from quantum_gnss_guard.simulator import Simulator
from pathlib import Path


def generate_dataset(config: dict, n_samples: int = 10000, output_file: str = 'dataset.h5'):
    """Generate dataset of simulation results.

    Args:
        config: Simulator config
        n_samples: Number of samples
        output_file: Output HDF5 file
    """
    sim = Simulator(config)
    results = sim.run(mc_runs=n_samples // 100)  # Adjust for passes

    # Create features and labels
    features = []
    labels = []

    for _, row in results.iterrows():
        # Simplified feature extraction
        feature = {
            'n_pairs': row['n_pairs'],
            'detection_score': row['detection_score']
        }
        features.append(feature)
        labels.append(1 if row['attack_type'] != 'none' else 0)

    features_df = pd.DataFrame(features)
    labels_df = pd.DataFrame({'label': labels})

    # Export to HDF5
    with h5py.File(output_file, 'w') as f:
        f.create_dataset('features', data=features_df.values)
        f.create_dataset('labels', data=labels_df.values)
        f.create_dataset('feature_names', data=np.array(features_df.columns, dtype='S'))

    # Also CSV
    combined = pd.concat([features_df, labels_df], axis=1)
    combined.to_csv(output_file.replace('.h5', '.csv'), index=False)

    print(f"Dataset saved to {output_file}")


if __name__ == '__main__':
    config = {
        'tle_file': 'data/tle_sample.txt',
        'station_loc': [40, -74, 0],
        'pair_rate': 5000,
        'attacks': [
            {'attack_type': 'none'},  # Legit
            {'attack_type': 'time-push'},
            {'attack_type': 'hybrid'}
        ]
    }
    generate_dataset(config)