"""Tests for detector module."""

import numpy as np
from quantum_gnss_guard.detector import Detector


def test_detector_init():
    """Test detector initialization."""
    det = Detector()
    assert det.latent_dim == 16
    assert det.bins == 100


def test_classical_detect():
    """Test classical detection."""
    det = Detector()

    # Legit data
    dt_true = np.random.normal(0, 50e-12, 1000)
    # Spoofed data
    dt_spoof = np.random.normal(10e-9, 50e-12, 1000)

    score = det.classical_detect(dt_true, dt_spoof)
    assert 0 <= score <= 1


def test_build_vae():
    """Test VAE building."""
    det = Detector()
    det.build_vae(100)
    assert det.vae is not None


def test_compute_roc():
    """Test ROC computation."""
    det = Detector()

    # Fake data
    true_labels = np.random.randint(0, 2, 100)
    scores = np.random.random(100)

    roc_metrics = det.compute_roc(true_labels, scores)
    assert 'auc' in roc_metrics
    assert 0 <= roc_metrics['auc'] <= 1