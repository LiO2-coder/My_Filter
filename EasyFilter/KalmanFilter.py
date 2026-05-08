import math
from typing import Optional, Union


Number = Union[int, float]


class KalmanFilter:
    """
    一维线性卡尔曼滤波器(Kalman Filter)
    """

    def __init__(
        self,
        x: Number,
        A: Number = 1.0,
        B: Optional[Number] = None,
        H: Number = 1.0,
        Q: Number = 0.1,
        R: Number = 1.0,
        P: Number = 1.0,
    ):
        """
        初始化滤波器

        x: 初始状态值
        A: 状态转移系数
        B: 控制输入系数, 为 None 时忽略控制量
        H: 观测系数
        Q: 过程噪声方差, Q >= 0
        R: 观测噪声方差, R > 0
        P: 初始估计误差方差, P > 0
        """
        self._validate_number(x, "x")
        self._validate_number(A, "A")
        self._validate_number(H, "H")
        self._validate_number(Q, "Q")
        self._validate_number(R, "R")
        self._validate_number(P, "P")

        if B is not None:
            self._validate_number(B, "B")

        if Q < 0:
            raise ValueError("Q 必须满足 Q >= 0")
        if R <= 0:
            raise ValueError("R 必须满足 R > 0")
        if P <= 0:
            raise ValueError("P 必须满足 P > 0")

        self.x = float(x)
        self.A = float(A)
        self.B = None if B is None else float(B)
        self.H = float(H)
        self.Q = float(Q)
        self.R = float(R)
        self.P = float(P)

        self.kalman_gain = 0.0
        self.x_prior: Optional[float] = None
        self.P_prior: Optional[float] = None
        self.x_posterior: Optional[float] = None
        self.P_posterior: Optional[float] = None

    @staticmethod
    def _validate_number(value: Number, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} 不能为 NaN 或 Inf")

    def prior(self, u: Optional[Number] = None):
        """
        先验估计

        u: 控制量, 仅当 B 不为 None 时生效
        """
        if u is not None:
            self._validate_number(u, "u")

        control_term = 0.0
        if self.B is not None:
            control_term = 0.0 if u is None else self.B * float(u)

        self.x_prior = self.A * self.x + control_term
        self.P_prior = (self.A ** 2) * self.P + self.Q

    def update_kalman_gain(self):
        """
        更新卡尔曼增益
        """
        if self.P_prior is None:
            raise RuntimeError("请先执行 prior()")

        numerator = self.P_prior * self.H
        denominator = (self.H ** 2) * self.P_prior + self.R
        if denominator <= 0:
            raise RuntimeError("卡尔曼增益计算失败: 分母非正")
        if not math.isfinite(denominator):
            raise RuntimeError("卡尔曼增益计算失败: 分母不是有限数值")
        self.kalman_gain = numerator / denominator
        if not math.isfinite(self.kalman_gain):
            raise RuntimeError("卡尔曼增益计算失败: 增益不是有限数值")

    def posterior(self, z: Number):
        """
        后验估计

        z: 观测值
        """
        self._validate_number(z, "z")
        if self.x_prior is None or self.P_prior is None:
            raise RuntimeError("请先执行 prior()")

        innovation = float(z) - self.H * self.x_prior
        self.x_posterior = self.x_prior + self.kalman_gain * innovation
        self.P_posterior = self.P_prior - self.kalman_gain * self.H * self.P_prior
        if self.P_posterior is None or not math.isfinite(self.P_posterior):
            raise RuntimeError("后验估计失败: 协方差不是有限数值")
        if self.P_posterior < 0:
            raise RuntimeError("后验估计失败: 协方差为负值")

    def update(self, z: Number, u: Optional[Number] = None) -> float:
        """
        更新滤波器

        z: 观测值
        u: 控制量, 仅当 B 不为 None 时生效
        """
        self.prior(u=u)
        self.update_kalman_gain()
        self.posterior(z)

        self.x = float(self.x_posterior)
        self.P = float(self.P_posterior)
        if not math.isfinite(self.x):
            raise RuntimeError("更新失败: 状态估计不是有限数值")
        if self.P < 0:
            raise RuntimeError("更新失败: 状态协方差为负值")
        return self.x

    def get_filtered(self) -> float:
        """
        获取当前估计值
        """
        return self.x

    def get_state(self) -> float:
        """
        获取当前状态估计值
        """
        return self.x

    def get_kalman_gain(self) -> float:
        """
        获取当前卡尔曼增益
        """
        return self.kalman_gain

    def get_covariance(self) -> float:
        """
        获取当前状态估计误差方差
        """
        return self.P

    def get_process_noise(self) -> float:
        """
        获取过程噪声方差
        """
        return self.Q

    def get_measurement_noise(self) -> float:
        """
        获取观测噪声方差
        """
        return self.R

    def reset(self, x: Optional[Number] = None, P: Optional[Number] = None) -> None:
        """
        重置滤波器

        x: 可选, 重置状态值
        P: 可选, 重置状态协方差
        """
        if x is not None:
            self._validate_number(x, "x")
            self.x = float(x)
        if P is not None:
            self._validate_number(P, "P")
            if P <= 0:
                raise ValueError("P 必须满足 P > 0")
            self.P = float(P)

        self.kalman_gain = 0.0
        self.x_prior = None
        self.P_prior = None
        self.x_posterior = None
        self.P_posterior = None
