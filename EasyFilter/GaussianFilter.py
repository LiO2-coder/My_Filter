from collections import deque
from typing import Deque, Optional, Tuple, Union

import numpy as np


Number = Union[int, float]


class GaussianFilter:
    """
    高斯加权滑动滤波器(Gaussian Weighted Filter)
    """

    def __init__(self, window_size: int = 5, sigma: float = 1.0):
        """
        初始化滤波器

        window_size: 窗口大小, 必须大于 0
        sigma: 高斯核标准差, 必须大于 0
        """
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise ValueError("window_size 类型错误, 仅支持整数")
        if window_size <= 0:
            raise ValueError("window_size 必须大于 0")
        if not isinstance(sigma, (int, float)) or isinstance(sigma, bool):
            raise ValueError("sigma 类型错误, 仅支持数值类型")
        if sigma <= 0:
            raise ValueError("sigma 必须大于 0")

        self.window_size = window_size
        self.sigma = float(sigma)
        self.window: Deque[float] = deque(maxlen=window_size)
        self.filtered: Optional[float] = None

    def _weights_for_len(self, length: int) -> np.ndarray:
        # 因为是流式处理, 给更近的样本更高权重
        distances = np.arange(length - 1, -1, -1, dtype=float)
        weights = np.exp(-0.5 * (distances / self.sigma) ** 2)
        weights_sum = float(np.sum(weights))
        if weights_sum <= 0:
            raise RuntimeError("高斯权重计算失败")
        return weights / weights_sum

    def update(self, new_value: Number) -> Tuple[float, bool]:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        self.window.append(float(new_value))
        arr = np.asarray(self.window, dtype=float)
        weights = self._weights_for_len(len(arr))
        self.filtered = float(np.dot(arr, weights))
        return self.filtered, len(self.window) == self.window_size

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self, sigma: Optional[Number] = None):
        """
        重置滤波器

        sigma: 可选, 重置时同时更新 sigma
        """
        self.window.clear()
        self.filtered = None
        if sigma is not None:
            if not isinstance(sigma, (int, float)) or isinstance(sigma, bool):
                raise ValueError("sigma 类型错误, 仅支持数值类型")
            if sigma <= 0:
                raise ValueError("sigma 必须大于 0")
            self.sigma = float(sigma)
