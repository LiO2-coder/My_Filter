import math
import os
import random
import sys

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


def build_signal(n=30):
    random.seed(7)
    data = []
    for i in range(n):
        base = 10.0 + 0.05 * i
        periodic = 0.6 * math.sin(i / 3.0)
        noise = random.uniform(-0.35, 0.35)
        value = base + periodic + noise
        if i in (8, 19):
            value += 2.2
        data.append(value)
    return data


def print_first_n(name, values, n=6):
    short = ", ".join(f"{v:.3f}" for v in values[:n])
    print(f"{name:<18}: {short}")


def run_linear_filters(data):
    mean_filter = MeanFilter()
    swm_filter = SWMFilter(window_size=5)
    median_filter = MedianFilter(window_size=5)
    tm_filter = TMFilter(window_size=5, trim_size=1)
    ewma_filter = EWMAFilter(alpha=0.3)
    gaussian_filter = GaussianFilter(window_size=5, sigma=1.2)
    clamp_filter = ClampFilter(min_value=9.0, max_value=12.5)
    hyst_filter = HysteresisFilter(deadband=0.25)
    bw_filter = ButterworthFilter(order=2, cutoff=1.5, fs=20.0, btype="lowpass")

    out_mean = []
    out_swm = []
    out_median = []
    out_tm = []
    out_ewma = []
    out_gauss = []
    out_clamp = []
    out_hyst = []
    out_bw = []

    for x in data:
        out_mean.append(mean_filter.update(x))
        out_swm.append(swm_filter.update(x)[0])
        out_median.append(median_filter.update(x)[0])
        out_tm.append(tm_filter.update(x)[0])
        out_ewma.append(ewma_filter.update(x))
        out_gauss.append(gaussian_filter.update(x)[0])
        out_clamp.append(clamp_filter.update(x))
        out_hyst.append(hyst_filter.update(x))
        out_bw.append(bw_filter.update(x))

    print("\n=== 传统与窗口类滤波器 ===")
    print_first_n("MeanFilter", out_mean)
    print_first_n("SWMFilter", out_swm)
    print_first_n("MedianFilter", out_median)
    print_first_n("TMFilter", out_tm)
    print_first_n("EWMAFilter", out_ewma)
    print_first_n("GaussianFilter", out_gauss)
    print_first_n("ClampFilter", out_clamp)
    print_first_n("HysteresisFilter", out_hyst)
    print_first_n("Butterworth", out_bw)


def run_kalman_family(data):
    kf = KalmanFilter(x=10.0, Q=0.03, R=0.18, P=1.0)

    def f_state(x, u):
        if u is None:
            return x
        return x + 0.1 * float(u)

    def h_measure(x):
        return x

    ekf = EKalmanFilter(
        x0=10.0,
        state_func=f_state,
        measure_func=h_measure,
        Q=0.03,
        R=0.2,
        P=1.0,
    )

    ukf = UKalmanFilter(
        x0=10.0,
        state_func=f_state,
        measure_func=h_measure,
        Q=0.03,
        R=0.2,
        P=1.0,
    )

    comp = ComplementaryFilter(alpha=0.9, predict_func=lambda last, c: last if c is None else last + 0.1 * c)

    pf = ParticleFilter(
        num_particles=400,
        x_init=10.0,
        process_noise=0.25,
        measurement_noise=0.45,
    )

    out_kf = []
    out_ekf = []
    out_ukf = []
    out_comp = []
    out_pf = []

    for z in data:
        out_kf.append(kf.update(z))
        out_ekf.append(ekf.update(z))
        out_ukf.append(ukf.update(z))
        out_comp.append(comp.update(measurement=z))
        out_pf.append(pf.update(z))

    print("\n=== 卡尔曼家族与融合滤波器 ===")
    print_first_n("KalmanFilter", out_kf)
    print_first_n("EKalmanFilter", out_ekf)
    print_first_n("UKalmanFilter", out_ukf)
    print_first_n("Complementary", out_comp)
    print_first_n("ParticleFilter", out_pf)


def main():
    data = build_signal(30)
    print("输入信号前6项      :", ", ".join(f"{v:.3f}" for v in data[:6]))

    run_linear_filters(data)
    run_kalman_family(data)


if __name__ == "__main__":
    main()
