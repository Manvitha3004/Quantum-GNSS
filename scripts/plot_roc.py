"""Standalone ROC plot generator."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import roc_curve, auc


def plot_roc_from_csv(csv_file: str, output_file: str = 'roc.png'):
    """Generate ROC plot from CSV results.

    Args:
        csv_file: Path to results CSV
        output_file: Output plot file
    """
    df = pd.read_csv(csv_file)

    # Assume 'detection_score' and 'attack_type' columns
    y_true = (df['attack_type'] != 'none').astype(int)
    y_scores = df['detection_score']

    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig(output_file)
    plt.show()


if __name__ == '__main__':
    plot_roc_from_csv('results/simulation_results.csv')