# Extended Kalman Filter for 2D Robot Localization

This project implements an **Extended Kalman Filter (EKF)** to estimate a mobile robot's pose in a 2D map.

At each time step, the filter:
1. Predicts the next pose from odometry (`r1`, `t`, `r2`).
2. Corrects that estimate using landmark range measurements.
3. Updates the uncertainty (covariance) and visualizes the result.

The output is an interactive Matplotlib view showing:
- landmark positions,
- the estimated robot pose,
- and a covariance ellipse for position uncertainty.

## Repository Structure

- `code/kalman_filter.py` — EKF implementation (prediction, correction, plotting, main loop).
- `code/read_data.py` — Parsers for map and sensor logs.
- `data/world.dat` — Landmark map (`id x y`).
- `data/sensor_data.dat` — Sequential odometry + sensor observations.

## How It Works

- **State**: robot pose `mu = [x, y, theta]`.
- **Prediction**: applies the motion model and propagates covariance with Jacobians.
- **Correction**: compares expected landmark ranges with measured ranges, computes Kalman gain, then updates `mu` and `sigma`.

## Usage

### Requirements
- Python 3
- `numpy`
- `matplotlib`

Install dependencies:

```bash
pip install numpy matplotlib
```

Run the filter from the `code` directory:

```bash
cd code
python kalman_filter.py
```

An interactive plot window will open and update as the filter processes the dataset.
