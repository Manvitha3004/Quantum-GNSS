"""CLI script for running simulations."""

import click
from quantum_gnss_guard.simulator import Simulator
from pathlib import Path


@click.command()
@click.option('--tle', 'tle_file', required=True, help='TLE file path')
@click.option('--station', 'station_coords', nargs=3, type=float, required=True, help='Station lat lon alt')
@click.option('--pairs', 'pair_rate', type=int, default=10000, help='Entangled pair rate')
@click.option('--attack', 'attack_type', default='time-push', help='Attack type')
@click.option('--mc_runs', type=int, default=50, help='Monte Carlo runs')
@click.option('--output', 'output_dir', default='results', help='Output directory')
def main(tle_file, station_coords, pair_rate, attack_type, mc_runs, output_dir):
    """Run GNSS spoofing detection simulation."""
    config = {
        'tle_file': tle_file,
        'station_loc': station_coords,
        'pair_rate': pair_rate,
        'attacks': [{'attack_type': attack_type}]
    }

    sim = Simulator(config)
    results = sim.run(mc_runs=mc_runs)

    # Create output dir
    Path(output_dir).mkdir(exist_ok=True)
    sim.export_results(results, output_dir)

    # Print summary
    print(f"Simulation complete. Results saved to {output_dir}")
    print(results.describe())


if __name__ == '__main__':
    main()