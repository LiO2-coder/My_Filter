# EasyFilter - Lightweight 1D Filtering Library

[中文文档](./README.md)

`EasyFilter` is a simple and practical filtering library for 1D scalar data smoothing, denoising, and state estimation.

The current version provides **14 filters** with a consistent API style, suitable for both quick experiments and real projects.

## Project Structure

```text
main/
├── MyFilter/
│   ├── ButterworthFilter.py
│   ├── ClampFilter.py
│   ├── ComplementaryFilter.py
│   ├── EKalmanFilter.py
│   ├── EWMAFilter.py
│   ├── GaussianFilter.py
│   ├── HysteresisFilter.py
│   ├── KalmanFilter.py
│   ├── MeanFilter.py
│   ├── MedianFilter.py
│   ├── ParticleFilter.py
│   ├── SWMFilter.py
│   ├── TMFilter.py
│   ├── UKalmanFilter.py
│   └── __init__.py
├── examples/
│   ├── demo_all_filters.py
│   └── plot_filter_groups.py
├── LICENSE
├── README.md
├── README_en.md
├── FilterList.txt
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/LiO2-coder/EasyFilter.git
cd EasyFilter
pip install -r requirements.txt
```

## Dependencies

- Python 3.8+
- numpy>=1.19.0
- scipy>=1.7.0
- matplotlib>=3.5.0

## Quick Start

```python
from MyFilter import SWMFilter, EWMAFilter, KalmanFilter

swm = SWMFilter(window_size=5)
print(swm.update(1.2))  # (1.2, False)

ema = EWMAFilter(alpha=0.3)
print(ema.update(1.2))

kf = KalmanFilter(x=0.0, Q=0.1, R=1.0)
print(kf.update(1.2))
```

## Filter List

### Basic Smoothing Filters

| Filter | Core API | Characteristics | Main Advantage | Limitation | Typical Scenarios | Parameter Tips |
| --- | --- | --- | --- | --- | --- | --- |
| `MeanFilter` | `update(x)` | Cumulative average over all historical observations. | Simplest baseline smoother. | Very slow response to new changes. | Long-term temperature trends, slow baseline tracking. | Use `reset()` periodically if you need phase-based averaging. |
| `EWMAFilter` | `update(x)` | Exponential weighting; newer observations get higher weight. | Good balance between smoothness and responsiveness. | Poor `alpha` setting may be too laggy or too noisy. | Real-time sensor smoothing, price curve visualization. | Start with `alpha=0.2~0.4`; increase for faster response. |
| `SWMFilter` | `update(x) -> (value, full_window)` | Fixed-size moving average with equal weights. | Stable and intuitive behavior. | Larger window adds more lag. | Uniformly sampled 1D signal smoothing. | `window_size=3~7` is a practical default range. |
| `MedianFilter` | `update(x) -> (value, full_window)` | Moving median; naturally suppresses isolated spikes. | Strong impulse-noise resistance. | Weaker than mean-like filters for pure Gaussian noise. | Distance sensor spikes, touch signal glitches. | Prefer odd windows (`3/5/7`) for stable median behavior. |
| `TMFilter` | `update(x) -> (value, full_window)` | Trimmed mean after dropping extreme values on both sides. | Keeps trend while reducing outlier impact. | Aggressive trimming can lose useful information. | Industrial measurements with occasional outliers. | Start with `window_size=5, trim_size=1`; keep `2*trim_size < window_size`. |
| `GaussianFilter` | `update(x) -> (value, full_window)` | Gaussian-weighted moving average, emphasizing recent data. | Better local dynamics than equal-weight averaging. | Mismatched `sigma`/window can degrade quality. | Smooth curves while preserving local variations. | Start with `window_size=5`, `sigma=1.0~1.5`. |

### Rule/Fusion Filters

| Filter | Core API | Characteristics | Main Advantage | Limitation | Typical Scenarios | Parameter Tips |
| --- | --- | --- | --- | --- | --- | --- |
| `ClampFilter` | `update(x)` | Hard clamps observation into configured bounds. | Direct protection against out-of-range values. | Not a smoother, only a limiter. | Sensor protection, safety-bound input handling. | Set `min_value/max_value` based on physical limits. |
| `HysteresisFilter` | `update(x)` | Holds previous output until change exceeds deadband. | Greatly reduces micro-jitter triggers. | Too large deadband can hide small real changes. | Threshold switching, anti-flicker UI values. | Start with deadband around half of noise peak-to-peak amplitude. |
| `ComplementaryFilter` | `update(measurement, prediction=None, control=None)` | Fuses prediction and observation into one output. | Lightweight model-assisted fusion. | Depends on `alpha` and prediction quality. | 1D IMU-like fusion, simple state blending. | Start with `alpha=0.9~0.98`; reduce if prediction is unreliable. |

### State Estimation & Frequency Filters

| Filter | Core API | Characteristics | Main Advantage | Limitation | Typical Scenarios | Parameter Tips |
| --- | --- | --- | --- | --- | --- | --- |
| `ButterworthFilter` | `update(x)` | Streaming IIR frequency filter (low/high/band-pass/stop). | Clear frequency-domain control. | Requires correct `fs` and cutoff design. | Power-line interference suppression, low-pass control signals. | Validate `fs` first, then tune `cutoff`. |
| `KalmanFilter` | `update(z, u=None)` | 1D linear state estimation via predict-update cycle. | Stable and interpretable estimation. | Needs linear model assumptions and noise tuning. | Constant/near-linear process estimation. | Fix `R` first, then tune `Q` for tracking speed. |
| `EKalmanFilter` | `update(z, u=None)` | First-order linearization for nonlinear systems. | Handles mild-to-moderate nonlinearity. | Linearization error may affect robustness. | Nonlinear sensor mapping, simplified dynamics. | Ensure smooth `state_func/measure_func` before tuning `Q/R`. |
| `UKalmanFilter` | `update(z, u=None)` | Sigma-point propagation without explicit Jacobians. | Often more robust than EKF in nonlinear cases. | More hyperparameters to tune. | Low-dimensional nonlinear estimation with better fidelity. | Typical start: `alpha=1e-3, beta=2, kappa=0`. |
| `ParticleFilter` | `update(z, u=None)` | Particle-based posterior approximation for complex noise. | Flexible in strongly nonlinear/non-Gaussian problems. | Higher compute cost; sensitive to particle count. | Multi-modal noise, uncertain models, heavy disturbances. | Start with `num_particles=300~800`, then tune noise scales. |

## How to Choose a Filter

### By Noise Type

- Mainly high-frequency jitter: start with `EWMAFilter`, `SWMFilter`, or `GaussianFilter`.
- Strong impulse/outlier noise: start with `MedianFilter` or `TMFilter`; optionally add `ClampFilter` first.
- Slow drift with occasional jumps: try `EWMAFilter`, optionally combined with `HysteresisFilter`.
- Frequency-specific periodic noise: prefer `ButterworthFilter` (low-pass or band-stop).

### By System Constraints

- Low compute budget and strict real-time: `MeanFilter`, `EWMAFilter`, `ClampFilter`.
- Linear process model available: `KalmanFilter`.
- Nonlinear process model available: `EKalmanFilter` or `UKalmanFilter`.
- Nonlinear + non-Gaussian/noisy uncertainty: `ParticleFilter`.

### Quick Rules (Practical)

1. Need fast and lightweight denoising: start with `EWMAFilter(alpha=0.3)`.
2. Data has obvious spikes: start with `MedianFilter(window_size=5)`, then optionally add `EWMAFilter`.
3. Need both outlier resistance and trend retention: start with `TMFilter(window_size=5, trim_size=1)`.
4. Known valid value range: apply `ClampFilter` first, then smoothing.
5. Too many tiny-trigger changes: use `HysteresisFilter(deadband=...)`.
6. Frequency-domain target available: use `ButterworthFilter` with verified `fs`.
7. Need model-based state estimation: start with `KalmanFilter`, then upgrade to `EKF/UKF` if needed.
8. Model is uncertain and noise is complex: use `ParticleFilter` and scale particle count gradually.

## Filtering Results (Plots)

![Basic Smoothing Filters](images/Basic_Smoothing_Filters.png "Figure 1: Basic Smoothing Filters")
*Figure 1: Basic Smoothing Filters*

![Rule/Fusion Filters](images/Rule%26Fusion_Filters.png "Figure 2: Rule/Fusion Filters")
*Figure 2: Rule/Fusion Filters*

![State Estimation & Frequency Filters](images/StateEstimation%26Frequency_Filters.png "Figure 3: State Estimation & Frequency Filters")
*Figure 3: State Estimation & Frequency Filters*

## Example Scripts

Run all-filter console demo:

```bash
python3 examples/demo_all_filters.py
```

This demo covers:

- stable signal + impulse noise + slow drift
- minimum runnable usage of all filters
- injectable-model examples for `EKalman/UKalman/Particle/Complementary`

Run grouped plotting demo:

```bash
python3 examples/plot_filter_groups.py
```

Plot demo details:

- Generates one random signal using Python's `random` module
- Produces 3 line charts:
1. Basic Smoothing (`MF`, `EWMA`, `SWM`, `MED`, `TM`, `GAU`)
2. Rule/Fusion (`CLP`, `HYS`, `CMP`)
3. State Estimation & Frequency (`BWF`, `KF`, `EKF`, `UKF`, `PF`)
- Each chart includes `RAW` plus all filters in that category
- `RAW` is always plotted in red

## Notes

- The current library focuses on lightweight **1D scalar** filtering.
- API naming follows the current implementation, e.g. `get_filtered()`.

## TODO (Future Work)

### Kalman Family Upgrades

Planned upgrades beyond current 1D basic Kalman implementation:

- Multi-dimensional Kalman filters
- Adaptive Kalman filters
- Federated Kalman filters for multi-sensor fusion
- Cubature Kalman filters

### C++ Version

A C++ implementation is also planned.

## Contributing

Issues and pull requests are welcome.
For feature requests and bug reports, please open a GitHub Issue.

## License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for details.

## Author
- **GitHub**: [https://github.com/LiO2-coder](https://github.com/LiO2-coder)

## Version History

- **v1.0** - Initial release
  - Implemented 3 basic filters
  - Added API docs and examples
- **v1.1** - Added 11 more filters
  - Total 14 common filters in three categories
  - Added complete API docs and examples
  - Added filter selection guidance
  - Added grouped visualization for filtering performance

## Support

If you encounter any issue, contact via:
- GitHub Issues: [https://github.com/LiO2-coder/EasyFilter/issues](https://github.com/LiO2-coder/EasyFilter/issues)

---

⭐ If this project helps you, a Star is appreciated!
