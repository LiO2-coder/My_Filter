from typing import Callable, Optional, Union

import numpy as np


Number = Union[int, float]
StateFunc = Callable[[np.ndarray, Optional[Number], np.random.Generator, float], np.ndarray]
LikelihoodFunc = Callable[[float, np.ndarray, float], np.ndarray]


class ParticleFilter:
    """
    一维粒子滤波器(Particle Filter)
    """

    def __init__(
        self,
        num_particles: int = 500,
        x_init: Number = 0.0,
        process_noise: Number = 1.0,
        measurement_noise: Number = 1.0,
        state_func: Optional[StateFunc] = None,
        likelihood_func: Optional[LikelihoodFunc] = None,
        random_seed: Optional[int] = None,
    ):
        """
        初始化滤波器

        num_particles: 粒子数, 必须大于 0
        x_init: 初始状态中心
        process_noise: 过程噪声标准差, 必须大于 0
        measurement_noise: 观测噪声标准差, 必须大于 0
        state_func: 可选状态转移函数
        likelihood_func: 可选似然函数
        random_seed: 随机种子
        """
        if not isinstance(num_particles, int) or isinstance(num_particles, bool):
            raise ValueError("num_particles 类型错误, 仅支持整数")
        if num_particles <= 0:
            raise ValueError("num_particles 必须大于 0")

        self._validate_number(x_init, "x_init")
        self._validate_number(process_noise, "process_noise")
        self._validate_number(measurement_noise, "measurement_noise")

        if process_noise <= 0:
            raise ValueError("process_noise 必须大于 0")
        if measurement_noise <= 0:
            raise ValueError("measurement_noise 必须大于 0")

        if state_func is not None and not callable(state_func):
            raise ValueError("state_func 必须是可调用对象")
        if likelihood_func is not None and not callable(likelihood_func):
            raise ValueError("likelihood_func 必须是可调用对象")

        self.num_particles = num_particles
        self.process_noise = float(process_noise)
        self.measurement_noise = float(measurement_noise)
        self.state_func = state_func
        self.likelihood_func = likelihood_func

        self.rng = np.random.default_rng(random_seed)
        self.x_init = float(x_init)

        self.particles = self.rng.normal(self.x_init, self.process_noise, size=self.num_particles)
        self.weights = np.full(self.num_particles, 1.0 / self.num_particles, dtype=float)

        self.filtered = float(np.mean(self.particles))
        self.effective_particle_count = float(self.num_particles)

    @staticmethod
    def _validate_number(value: Number, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")

    def _default_state_transition(self, particles: np.ndarray, control: Optional[Number]) -> np.ndarray:
        control_term = 0.0 if control is None else float(control)
        noise = self.rng.normal(0.0, self.process_noise, size=self.num_particles)
        return particles + control_term + noise

    def _default_likelihood(self, measurement: float, particles: np.ndarray) -> np.ndarray:
        residual = measurement - particles
        weights = np.exp(-0.5 * (residual / self.measurement_noise) ** 2)
        return weights

    def _normalize_weights(self):
        total = float(np.sum(self.weights))
        if total <= 0:
            self.weights.fill(1.0 / self.num_particles)
            return
        self.weights /= total

    def _systematic_resample(self):
        positions = (self.rng.random() + np.arange(self.num_particles)) / self.num_particles
        cumulative_sum = np.cumsum(self.weights)
        indices = np.searchsorted(cumulative_sum, positions)

        self.particles = self.particles[indices]
        self.weights.fill(1.0 / self.num_particles)

    def prior(self, u: Optional[Number] = None):
        """
        先验传播

        u: 控制量
        """
        if u is not None:
            self._validate_number(u, "u")

        if self.state_func is None:
            self.particles = self._default_state_transition(self.particles, u)
        else:
            updated = self.state_func(self.particles.copy(), u, self.rng, self.process_noise)
            if not isinstance(updated, np.ndarray):
                raise ValueError("state_func 返回值必须是 numpy.ndarray")
            if updated.shape != self.particles.shape:
                raise ValueError("state_func 返回数组形状错误")
            self.particles = updated.astype(float, copy=False)

    def update(self, z: Number, u: Optional[Number] = None) -> float:
        """
        更新滤波器

        z: 观测值
        u: 控制量
        """
        self._validate_number(z, "z")
        measurement = float(z)

        self.prior(u=u)

        if self.likelihood_func is None:
            self.weights = self._default_likelihood(measurement, self.particles)
        else:
            raw_weights = self.likelihood_func(measurement, self.particles.copy(), self.measurement_noise)
            if not isinstance(raw_weights, np.ndarray):
                raise ValueError("likelihood_func 返回值必须是 numpy.ndarray")
            if raw_weights.shape != self.weights.shape:
                raise ValueError("likelihood_func 返回数组形状错误")
            if np.any(raw_weights < 0):
                raise ValueError("likelihood_func 返回值不能包含负权重")
            self.weights = raw_weights.astype(float, copy=False)

        self._normalize_weights()
        self.filtered = float(np.dot(self.particles, self.weights))

        self.effective_particle_count = float(1.0 / np.sum(self.weights ** 2))
        if self.effective_particle_count < self.num_particles / 2.0:
            self._systematic_resample()
            self.filtered = float(np.mean(self.particles))
            self.effective_particle_count = float(self.num_particles)

        return self.filtered

    def get_filtered(self) -> float:
        """
        获取当前滤波值
        """
        return self.filtered

    def get_particles(self) -> np.ndarray:
        """
        获取当前粒子集合副本
        """
        return self.particles.copy()

    def get_effective_particle_count(self) -> float:
        """
        获取有效粒子数
        """
        return self.effective_particle_count

    def reset(self, x_init: Optional[Number] = None):
        """
        重置滤波器

        x_init: 可选, 重置初始状态中心
        """
        if x_init is not None:
            self._validate_number(x_init, "x_init")
            self.x_init = float(x_init)

        self.particles = self.rng.normal(self.x_init, self.process_noise, size=self.num_particles)
        self.weights.fill(1.0 / self.num_particles)
        self.filtered = float(np.mean(self.particles))
        self.effective_particle_count = float(self.num_particles)
