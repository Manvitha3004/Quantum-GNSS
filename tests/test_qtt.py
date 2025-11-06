"""Tests for QTT module."""

import numpy as np
import pandas as pd
from quantum_gnss_guard.qtt import QuantumTimeTransfer


def test_qtt_init():
    """Test QTT initialization."""
    qtt = QuantumTimeTransfer(sync_rate=1000, precision_ps=0.1)
    assert qtt.sync_rate == 1000
    assert qtt.precision == 0.1e-12


def test_generate_sync_pulses():
    """Test sync pulse generation."""
    qtt = QuantumTimeTransfer()
    
    duration = 1.0
    gnss_times = np.linspace(0, duration, 100)
    
    sync_events = qtt.generate_sync_pulses(duration, gnss_times)
    
    assert isinstance(sync_events, pd.DataFrame)
    assert len(sync_events) > 0
    assert 'pulse_time' in sync_events.columns
    assert 'quantum_phase' in sync_events.columns
    assert 'time_offset' in sync_events.columns


def test_detect_sync_anomalies():
    """Test sync anomaly detection."""
    qtt = QuantumTimeTransfer()
    
    # Create test data
    sync_events = pd.DataFrame({
        'pulse_time': np.linspace(0, 1, 100),
        'gnss_ref': np.linspace(0, 1, 100),
        'quantum_phase': np.random.uniform(0, 2*np.pi, 100),
        'time_offset': np.random.normal(0, 1e-12, 100),
        'sync_error': np.random.normal(0, 0.5e-12, 100)
    })
    
    results = qtt.detect_sync_anomalies(sync_events)
    
    assert 'anomaly_score' in results
    assert 'detection' in results
    assert 0 <= results['anomaly_score'] <= 1


def test_simulate_decoherence():
    """Test decoherence simulation."""
    qtt = QuantumTimeTransfer()
    
    t_list = np.linspace(0, 1e-3, 100)
    fidelity = qtt.simulate_decoherence(t_list)
    
    assert len(fidelity) == len(t_list)
    assert np.all(fidelity >= 0)
    assert np.all(fidelity <= 1)
    assert fidelity[0] > fidelity[-1]  # Decay over time


def test_clock_drift_estimation():
    """Test clock drift estimation."""
    qtt = QuantumTimeTransfer()
    
    # Create test data with linear drift
    times = np.linspace(0, 10, 1000)
    drift_rate = 1e-12  # 1 ps/s
    errors = drift_rate * times + np.random.normal(0, 0.1e-12, 1000)
    
    sync_events = pd.DataFrame({
        'pulse_time': times,
        'sync_error': errors
    })
    
    drift_estimates = qtt.estimate_clock_drift(sync_events)
    
    # Should detect the injected drift
    mean_drift = np.mean(drift_estimates)
    assert abs(mean_drift - drift_rate) < 0.5e-12