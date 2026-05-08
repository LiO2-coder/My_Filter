from collections import deque
import math
from typing import Deque, Optional, Tuple, Union


Number = Union[int, float]


class SWMFilter:
    """
    滑动窗口均值滤波器(Sliding Window Mean Filter)
    """

    def __init__(self, window_size: int = 5):
        """
        初始化滤波器

        window_size: 窗口大小, 必须大于 0
        """
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise ValueError("window_size 类型错误, 仅支持整数")
        if window_size <= 0:
            raise ValueError("window_size 必须大于 0")

        self.window_size = window_size
        self.window: Deque[float] = deque(maxlen=window_size)
        self.filtered: Optional[float] = None

    @staticmethod
    def _validate_number(value: Number, name: str):
        """
        校验输入是否为有效数值
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} 不能为 NaN 或 Inf")

    def update(self, new_value: Number) -> Tuple[float, bool]:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        self._validate_number(new_value, "new_value")

        self.window.append(float(new_value))
        full_window = len(self.window) == self.window_size

        if not full_window:
            self.filtered = sum(self.window) / len(self.window)
            return self.filtered, False

        self.filtered = sum(self.window) / self.window_size
        return self.filtered, True

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self) -> None:
        """
        重置滤波器
        """
        self.window.clear()
        self.filtered = None
