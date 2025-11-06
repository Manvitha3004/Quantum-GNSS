# API Documentation

## Simulator

```python
from quantum_gnss_guard import Simulator

sim = Simulator(config)
results = sim.run(mc_runs=100)
```

### Parameters
- `config`: Dict with tle_file, station_loc, pair_rate, attacks

### Methods
- `run(mc_runs)`: Run Monte Carlo simulation
- `export_results(results, output_dir)`: Save to CSV/JSON

## Orbital

```python
from quantum_gnss_guard.orbital import Orbital

orb = Orbital(tle_file, lat, lon, alt)
passes = orb.compute_passes(start_time, hours=24)
```

### Methods
- `compute_passes()`: Returns DataFrame of satellite passes
- `link_budget_over_pass()`: Time-series link budget

## QuantumChannel

```python
from quantum_gnss_guard.quantum_channel import QuantumChannel

qc = QuantumChannel(pair_rate=5000)
events = qc.generate_pairs(duration=600)
dt = qc.compute_coincidences(events)
```

### Methods
- `generate_pairs()`: Simulate photon arrivals
- `compute_coincidences()`: Extract time differences

## Detector

```python
from quantum_gnss_guard.detector import Detector

det = Detector()
det.train_vae(legit_histograms)
result = det.detect(dt)
```

### Methods
- `train_vae()`: Train on legitimate data
- `detect()`: Return anomaly scores
- `compute_roc()`: ROC curve metrics