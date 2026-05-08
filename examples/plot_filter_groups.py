import math
import os
import random
import sys

import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from MyFilter import (
    ButterworthFilter,
    ClampFilter,
    ComplementaryFilter,
    EKalmanFilter,
    EWMAFilter,
    GaussianFilter,
    HysteresisFilter,
    KalmanFilter,
    MeanFilter,
    MedianFilter,
    ParticleFilter,
    SWMFilter,
    TMFilter,
    UKalmanFilter,
)


def build_random_signal(length: int = 220, seed: int = 2026):
    """
    使用 random 库生成带漂移/周期/噪声/脉冲的随机信号
    """
    random.seed(seed)
    data = []

    for i in range(length):
        baseline = 10.0 + 0.01 * i
        periodic = 0.75 * math.sin(i * 0.16)
        gaussian_noise = random.gauss(0.0, 0.28)
        value = baseline + periodic + gaussian_noise

        # 少量随机脉冲, 模拟异常扰动
        if random.random() < 0.035:
            value += random.choice([-1.0, 1.0]) * random.uniform(1.2, 2.2)

        data.append(value)
    return data


def apply_basic_smoothing(data):
    filters = {
        "MF": MeanFilter(),
        "EWMA": EWMAFilter(alpha=0.3),
        "SWM": SWMFilter(window_size=5),
        "MED": MedianFilter(window_size=5),
        "TM": TMFilter(window_size=5, trim_size=1),
        "GAU": GaussianFilter(window_size=5, sigma=1.2),
    }

    outputs = {abbr: [] for abbr in filters}
    for x in data:
        outputs["MF"].append(filters["MF"].update(x))
        outputs["EWMA"].append(filters["EWMA"].update(x))
        outputs["SWM"].append(filters["SWM"].update(x)[0])
        outputs["MED"].append(filters["MED"].update(x)[0])
        outputs["TM"].append(filters["TM"].update(x)[0])
        outputs["GAU"].append(filters["GAU"].update(x)[0])
    return outputs


def apply_rule_fusion(data):
    filters = {
        "CLP": ClampFilter(min_value=8.8, max_value=13.8),
        "HYS": HysteresisFilter(deadband=0.22),
        "CMP": ComplementaryFilter(alpha=0.92),
    }

    outputs = {abbr: [] for abbr in filters}
    for x in data:
        outputs["CLP"].append(filters["CLP"].update(x))
        outputs["HYS"].append(filters["HYS"].update(x))
        outputs["CMP"].append(filters["CMP"].update(measurement=x))
    return outputs


def apply_state_freq(data):
    kf = KalmanFilter(x=data[0], Q=0.03, R=0.2, P=1.0)
    bwf = ButterworthFilter(order=2, cutoff=2.0, fs=50.0, btype="lowpass")

    def state_func(x, u):
        return x if u is None else x + 0.08 * float(u)

    def measure_func(x):
        return x

    ekf = EKalmanFilter(
        x0=data[0],
        state_func=state_func,
        measure_func=measure_func,
        Q=0.03,
        R=0.22,
        P=1.0,
    )
    ukf = UKalmanFilter(
        x0=data[0],
        state_func=state_func,
        measure_func=measure_func,
        Q=0.03,
        R=0.22,
        P=1.0,
    )
    pf = ParticleFilter(
        num_particles=500,
        x_init=data[0],
        process_noise=0.25,
        measurement_noise=0.45,
        random_seed=2026,
    )

    outputs = {"BWF": [], "KF": [], "EKF": [], "UKF": [], "PF": []}
    for z in data:
        outputs["BWF"].append(bwf.update(z))
        outputs["KF"].append(kf.update(z))
        outputs["EKF"].append(ekf.update(z))
        outputs["UKF"].append(ukf.update(z))
        outputs["PF"].append(pf.update(z))
    return outputs


def plot_group(title, raw_data, filtered_map):
    x = list(range(len(raw_data)))

    plt.figure(figsize=(12, 4.5))
    plt.plot(x, raw_data, color="red", linewidth=1.2, label="RAW")

    for abbr, series in filtered_map.items():
        plt.plot(x, series, linewidth=1.1, label=abbr)

    plt.title(title)
    plt.xlabel("Sample Index")
    plt.ylabel("Signal Value")
    plt.grid(alpha=0.25)
    plt.legend(ncol=3, fontsize=9)
    plt.tight_layout()


def main():
    raw = build_random_signal()

    basic_results = apply_basic_smoothing(raw)
    rule_results = apply_rule_fusion(raw)
    state_results = apply_state_freq(raw)

    plot_group("Basic Smoothing Filters", raw, basic_results)
    plot_group("Rule/Fusion Filters", raw, rule_results)
    plot_group("State Estimation & Frequency Filters", raw, state_results)

    plt.show()


if __name__ == "__main__":
    main()
