from typing import Callable, Optional, Union


Number = Union[int, float]
StateFunc = Callable[[float, Optional[Number]], Number]
MeasureFunc = Callable[[float], Number]
StateJacobian = Callable[[float, Optional[Number]], Number]
MeasureJacobian = Callable[[float], Number]


class EKalmanFilter:
    """
    一维扩展卡尔曼滤波器(Extended Kalman Filter)
    """

    def __init__(
        self,
        x0: Number,
        state_func: StateFunc,
        measure_func: MeasureFunc,
        state_jacobian: Optional[StateJacobian] = None,
        measure_jacobian: Optional[MeasureJacobian] = None,
        Q: Number = 0.1,
        R: Number = 1.0,
        P: Number = 1.0,
        epsilon: float = 1e-6,
    ):
        """
        初始化滤波器

        x0: 初始状态值
        state_func: 状态转移函数 f(x, u)
        measure_func: 观测函数 h(x)
        state_jacobian: 可选状态函数雅可比 df/dx
        measure_jacobian: 可选观测函数雅可比 dh/dx
        Q: 过程噪声方差, Q >= 0
        R: 观测噪声方差, R > 0
        P: 初始估计误差方差, P > 0
        epsilon: 数值求导扰动, epsilon > 0
        """
        self._validate_number(x0, "x0")
        self._validate_number(Q, "Q")
        self._validate_number(R, "R")
        self._validate_number(P, "P")
        self._validate_number(epsilon, "epsilon")

        if Q < 0:
            raise ValueError("Q 必须满足 Q >= 0")
        if R <= 0:
            raise ValueError("R 必须满足 R > 0")
        if P <= 0:
            raise ValueError("P 必须满足 P > 0")
        if epsilon <= 0:
            raise ValueError("epsilon 必须大于 0")

        if not callable(state_func):
            raise ValueError("state_func 必须是可调用对象")
        if not callable(measure_func):
            raise ValueError("measure_func 必须是可调用对象")
        if state_jacobian is not None and not callable(state_jacobian):
            raise ValueError("state_jacobian 必须是可调用对象")
        if measure_jacobian is not None and not callable(measure_jacobian):
            raise ValueError("measure_jacobian 必须是可调用对象")

        self.x = float(x0)
        self.P = float(P)
        self.Q = float(Q)
        self.R = float(R)
        self.epsilon = float(epsilon)

        self.state_func = state_func
        self.measure_func = measure_func
        self.state_jacobian = state_jacobian
        self.measure_jacobian = measure_jacobian

        self.filtered = self.x
        self.kalman_gain = 0.0
        self.x_prior: Optional[float] = None
        self.P_prior: Optional[float] = None
        self.innovation: Optional[float] = None

    @staticmethod
    def _validate_number(value: Number, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")

    def _numerical_jacobian(self, func: Callable[[float], Number], x: float) -> float:
        e = self.epsilon
        f_plus = func(x + e)
        f_minus = func(x - e)
        if not isinstance(f_plus, (int, float)) or isinstance(f_plus, bool):
            raise ValueError("雅可比数值求导失败: 函数返回值不是数值")
        if not isinstance(f_minus, (int, float)) or isinstance(f_minus, bool):
            raise ValueError("雅可比数值求导失败: 函数返回值不是数值")
        return (float(f_plus) - float(f_minus)) / (2.0 * e)

    def prior(self, u: Optional[Number] = None):
        """
        先验估计

        u: 控制量
        """
        if u is not None:
            self._validate_number(u, "u")

        x_pred = self.state_func(self.x, u)
        if not isinstance(x_pred, (int, float)) or isinstance(x_pred, bool):
            raise ValueError("state_func 返回值类型错误, 仅支持数值类型")
        self.x_prior = float(x_pred)

        if self.state_jacobian is not None:
            f_j = self.state_jacobian(self.x, u)
            if not isinstance(f_j, (int, float)) or isinstance(f_j, bool):
                raise ValueError("state_jacobian 返回值类型错误, 仅支持数值类型")
            F = float(f_j)
        else:
            F = self._numerical_jacobian(lambda xi: self.state_func(xi, u), self.x)

        self.P_prior = F * self.P * F + self.Q

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

        if self.measure_jacobian is not None:
            h_j = self.measure_jacobian(self.x_prior)
            if not isinstance(h_j, (int, float)) or isinstance(h_j, bool):
                raise ValueError("measure_jacobian 返回值类型错误, 仅支持数值类型")
            H = float(h_j)
        else:
            H = self._numerical_jacobian(self.measure_func, self.x_prior)

        z_pred = self.measure_func(self.x_prior)
        if not isinstance(z_pred, (int, float)) or isinstance(z_pred, bool):
            raise ValueError("measure_func 返回值类型错误, 仅支持数值类型")
        z_pred_f = float(z_pred)

        self.innovation = z_f - z_pred_f
        S = H * self.P_prior * H + self.R
        if S <= 0:
            raise RuntimeError("EKF 更新失败: S 非正")

        self.kalman_gain = self.P_prior * H / S
        self.x = self.x_prior + self.kalman_gain * self.innovation
        self.P = (1.0 - self.kalman_gain * H) * self.P_prior

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
        self.innovation = None
