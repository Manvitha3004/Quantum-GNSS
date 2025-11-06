"""Detection algorithms: classical correlation + ML VAE."""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from typing import Tuple, Dict
from .utils import hellinger_distance, coincidence_histogram


class Detector:
    """Hybrid detector for spoofing detection."""

    def __init__(self, vae_latent_dim: int = 16, coincidence_bins: int = 100):
        """Initialize detector.

        Args:
            vae_latent_dim: Latent dimension for VAE
            coincidence_bins: Bins for histogram
        """
        self.latent_dim = vae_latent_dim
        self.bins = coincidence_bins
        self.vae = None
        self.threshold = 0.1  # Hellinger threshold

    def build_vae(self, input_shape: int):
        """Build VAE model.

        Args:
            input_shape: Input dimension
        """
        # Encoder
        encoder_inputs = keras.Input(shape=(input_shape,))
        x = layers.Reshape((input_shape, 1))(encoder_inputs)
        x = layers.Conv1D(32, 3, activation='relu', padding='same')(x)
        x = layers.Flatten()(x)
        z_mean = layers.Dense(self.latent_dim)(x)
        z_log_var = layers.Dense(self.latent_dim)(x)

        # Sampling layer
        def sampling(args):
            z_mean, z_log_var = args
            epsilon = tf.random.normal(shape=tf.shape(z_mean))
            return z_mean + tf.exp(0.5 * z_log_var) * epsilon

        z = layers.Lambda(sampling)([z_mean, z_log_var])

        # Decoder
        decoder_inputs = keras.Input(shape=(self.latent_dim,))
        x = layers.Dense(input_shape)(decoder_inputs)
        x = layers.Reshape((input_shape, 1))(x)
        x = layers.Conv1DTranspose(32, 3, activation='relu', padding='same')(x)
        decoder_outputs = layers.Conv1D(1, 3, activation='sigmoid', padding='same')(x)
        decoder_outputs = layers.Flatten()(decoder_outputs)

        # Models
        encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name='encoder')
        decoder = keras.Model(decoder_inputs, decoder_outputs, name='decoder')

        # VAE
        vae_outputs = decoder(encoder(encoder_inputs)[2])
        self.vae = keras.Model(encoder_inputs, vae_outputs, name='vae')

        # Loss
        reconstruction_loss = keras.losses.mse(encoder_inputs, vae_outputs)
        kl_loss = -0.5 * tf.reduce_mean(z_log_var - tf.square(z_mean) - tf.exp(z_log_var) + 1)
        self.vae.add_loss(kl_loss + reconstruction_loss)

        self.vae.compile(optimizer='adam')

    def train_vae(self, legit_histograms: np.ndarray, epochs: int = 50):
        """Train VAE on legitimate data.

        Args:
            legit_histograms: Training histograms
            epochs: Training epochs
        """
        if self.vae is None:
            self.build_vae(legit_histograms.shape[1])
        self.vae.fit(legit_histograms, epochs=epochs, verbose=0)

    def classical_detect(self, dt_true: np.ndarray, dt_spoof: np.ndarray) -> float:
        """Classical detection using Hellinger distance.

        Args:
            dt_true: True time differences
            dt_spoof: Spoofed time differences

        Returns:
            Detection score (0-1)
        """
        _, hist_true = coincidence_histogram(dt_true, bins=self.bins)
        _, hist_spoof = coincidence_histogram(dt_spoof, bins=self.bins)

        # Normalize
        hist_true = hist_true / np.sum(hist_true)
        hist_spoof = hist_spoof / np.sum(hist_spoof)

        d_h = hellinger_distance(hist_true, hist_spoof)
        return 1 / (1 + np.exp(-10 * (d_h - self.threshold)))  # Sigmoid

    def ml_detect(self, histogram: np.ndarray) -> float:
        """ML detection using VAE reconstruction error.

        Args:
            histogram: Input histogram

        Returns:
            Anomaly score
        """
        if self.vae is None:
            raise ValueError("VAE not trained")

        reconstructed = self.vae.predict(histogram.reshape(1, -1), verbose=0)
        error = np.mean((histogram - reconstructed.flatten())**2)
        return error

    def detect(self, dt: np.ndarray, use_ml: bool = True) -> Dict:
        """Full detection pipeline.

        Args:
            dt: Time differences
            use_ml: Whether to use ML component

        Returns:
            Detection results
        """
        # Assume we have reference legit dt for comparison
        # In practice, this would be pre-computed
        legit_dt = np.random.normal(0, 50e-12, len(dt))  # Placeholder

        classical_score = self.classical_detect(legit_dt, dt)

        if use_ml:
            _, hist = coincidence_histogram(dt, bins=self.bins)
            ml_score = self.ml_detect(hist.astype(float))
            # Combine scores
            combined_score = 0.7 * classical_score + 0.3 * ml_score
        else:
            combined_score = classical_score

        return {
            'classical_score': classical_score,
            'ml_score': ml_score if use_ml else None,
            'combined_score': combined_score,
            'decision': combined_score > 0.5
        }

    def compute_roc(self, true_labels: np.ndarray, scores: np.ndarray) -> Dict:
        """Compute ROC metrics.

        Args:
            true_labels: Ground truth (0=legit, 1=spoof)
            scores: Detection scores

        Returns:
            ROC metrics
        """
        fpr, tpr, thresholds = roc_curve(true_labels, scores)
        roc_auc = auc(fpr, tpr)

        return {
            'fpr': fpr,
            'tpr': tpr,
            'thresholds': thresholds,
            'auc': roc_auc
        }