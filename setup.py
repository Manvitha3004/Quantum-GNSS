from setuptools import setup, find_packages

setup(
    name="quantum-gnss-guard",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "pandas>=2.0.0",
        "skyfield>=1.48",
        "qutip>=4.7.0",
        "scikit-learn>=1.3.0",
        "tensorflow>=2.14.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "seaborn>=0.12.0",
        "click>=8.1.0",
        "pytest>=7.4.0",
        "jupyterlab>=4.0.0",
        "black[jupyter]>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "run-sim=quantum_gnss_guard.scripts.run_sim:main",
        ],
    },
)