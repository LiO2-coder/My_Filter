from typing import Callable, Optional, Union

import numpy as np


Number = Union[int, float]
StateFunc = Callable[[float, Optional[Number]], Number]
MeasureFunc = Callable[[float], Number]


class UKalmanFilter:
    """
    一维无迹卡尔曼滤波器(Unscented Kalman Filter)
    """

    def __init__(
        self,
        x0: Number,
        state_func: StateFunc,
        measure_func: MeasureFunc,
        Q: Number = 0.1,
        R: Number = 1.0,
        P: Number = 1.0,
        alpha: float = 1e-3,
        beta: float = 2.0,
        kappa: float = 0.0,
    ):
        """
        初始化滤波器

        x0: 初始状态值
        state_func: 状态转移函数 f(x, u)
        measure_func: 观测函数 h(x)
        Q: 过程噪声方差, Q >= 0
        R: 观测噪声方差, R > 0
        P: 初始估计误差方差, P > 0
        alpha/beta/kappa: UKF 超参数
        """
        self._validate_number(x0, "x0")
        self._validate_number(Q, "Q")
        self._validate_number(R, "R")
        self._validate_number(P, "P")
        self._validate_number(alpha, "alpha")
        self._validate_number(beta, "beta")
        self._validate_number(kappa, "kappa")

        if Q < 0:
            raise ValueError("Q 必须满足 Q >= 0")
        if R <= 0:
            raise ValueError("R 必须满足 R > 0")
        if P <= 0:
            raise ValueError("P 必须满足 P > 0")
        if alpha <= 0:
            raise ValueError("alpha 必须大于 0")

        if not callable(state_func):
            raise ValueError("state_func 必须是可调用对象")
        if not callable(measure_func):
            raise ValueError("measure_func 必须是可调用对象")

        self.n = 1
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.kappa = float(kappa)
        self.lambda_ = self.alpha ** 2 * (self.n + self.kappa) - self.n

        c = self.n + self.lambda_
        if c <= 0:
            raise ValueError("UKF 参数不合法: n + lambda 必须大于 0")

        self.gamma = float(np.sqrt(c))
        self.wm = np.array([self.lambda_ / c, 1.0 / (2.0 * c), 1.0 / (2.0 * c)], dtype=float)
        self.wc = np.array(
            [self.lambda_ / c + (1.0 - self.alpha ** 2 + self.beta), 1.0 / (2.0 * c), 1.0 / (2.0 * c)],
            dtype=float,
        )

        self.state_func = state_func
        self.measure_func = measure_func

        self.x = float(x0)
        self.P = float(P)
        self.Q = float(Q)
        self.R = float(R)

        self.filtered = self.x
        self.kalman_gain = 0.0
        self.x_prior: Optional[float] = None
        self.P_prior: Optional[float] = None

    @staticmethod
    def _validate_number(value: Number, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")

    def _sigma_points(self, x: float, P: float) -> np.ndarray:
        spread = self.gamma * float(np.sqrt(max(P, 1e-12)))
        return np.array([x, x + spread, x - spread], dtype=float)

    def prior(self, u: Optional[Number] = None):
        """
        先验估计

        u: 控制量
        """
        if u is not None:
            self._validate_number(u, "u")

        sigma = self._sigma_points(self.x, self.P)
        sigma_pred = np.zeros_like(sigma)

        for i in range(3):
            pred = self.state_func(float(sigma[i]), u)
            if not isinstance(pred, (int, float)) or isinstance(pred, bool):
                raise ValueError("state_func 返回值类型错误, 仅支持数值类型")
            sigma_pred[i] = float(pred)

        x_prior = float(np.dot(self.wm, sigma_pred))
        diff = sigma_pred - x_prior
        P_prior = float(np.dot(self.wc, diff * diff) + self.Q)

        self.sigma_pred = sigma_pred
        self.x_prior = x_prior
        self.P_prior = P_prior

    def update(self, z: Number, u: Optional[Number] = None) -> float:
        """
        更新滤波器

        z: 观测值
        u: 控制量
        """
        self._validate_number(z, "z")
        z_f = float(z)

        self.prior(u=u)

        if self.x_prior is None or self.P_prior is None:
            raise RuntimeError("先验估计失败")

        z_sigma = np.zeros(3, dtype=float)
        for i in range(3):
            observed = self.measure_func(float(self.sigma_pred[i]))
            if not isinstance(observed, (int, float)) or isinstance(observed, bool):
                raise ValueError("measure_func 返回值类型错误, 仅支持数值类型")
            z_sigma[i] = float(observed)

        z_pred = float(np.dot(self.wm, z_sigma))
        z_diff = z_sigma - z_pred
        x_diff = self.sigma_pred - self.x_prior

        S = float(np.dot(self.wc, z_diff * z_diff) + self.R)
        if S <= 0:
            raise RuntimeError("UKF 更新失败: S 非正")

        cross_cov = float(np.dot(self.wc, x_diff * z_diff))
        self.kalman_gain = cross_cov / S

        self.x = self.x_prior + self.kalman_gain * (z_f - z_pred)
        self.P = max(self.P_prior - self.kalman_gain * S * self.kalman_gain, 1e-12)
        self.filtered = self.x
        return self.filtered

    def get_filtered(self) -> float:
        """
        获取当前滤波值
        """
        return self.filtered

    def get_kalman_gain(self) -> float:
        """
        获取当前卡尔曼增益
        """
        return self.kalman_gain

    def get_covariance(self) -> float:
        """
        获取当前估计误差方差
        """
        return self.P

    def reset(self, x0: Optional[Number] = None, P: Optional[Number] = None):
        """
        重置滤波器

        x0: 可选, 重置状态值
        P: 可选, 重置状态协方差
        """
        if x0 is not None:
            self._validate_number(x0, "x0")
            self.x = float(x0)
        if P is not None:
            self._validate_number(P, "P")
            if P <= 0:
                raise ValueError("P 必须满足 P > 0")
            self.P = float(P)

        self.filtered = self.x
        self.kalman_gain = 0.0
        self.x_prior = None
        self.P_prior = None
