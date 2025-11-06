# System Specification

## Threat Model
The system detects GNSS spoofing attacks where adversaries attempt to manipulate timing signals. Key threats:
- **Time-push attacks**: Shift GNSS timestamps by δt (1-100 ns)
- **Replica attacks**: Replay authentic signals with phase offsets
- **Hybrid attacks**: Combine time-push with classical mimics of quantum correlations

Detection threshold: δt > 5 ps detectable with >95% TPR at <5% FPR.

## System Metrics
- **Range**: Up to 500 km LEO passes
- **Latency**: <1 s per pass detection
- **FDR**: <1% false detection rate
- **Breakthrough**: >10x spoof resilience vs. classical correlation tests
- **QTT Precision**: Sub-picosecond (0.1 ps) timing accuracy
- **QTT Enhancement**: 10-15% detection improvement for advanced spoofs

## Components
- Orbital: SGP4 propagation for pass prediction
- Quantum Channel: SPDC entanglement at 810 nm, 1-10 kHz rates
- Detector: Hybrid classical (Hellinger distance) + VAE anomaly detection
- GNSS Spoof: Configurable attack models
- QTT: Quantum Time Transfer with Bell-pair synchronization

## Physics Models
- Franson interferometer correlations for entanglement verification
- Rayleigh fading for atmospheric scintillation
- Poisson statistics for photon arrivals
- Gaussian jitter for detector timing (50 ps σ)
- Bell-state phase estimation for quantum clock sync
- Lindblad decoherence for realistic quantum noise