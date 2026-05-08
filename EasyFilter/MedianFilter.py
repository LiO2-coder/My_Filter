from collections import deque
from statistics import median
from typing import Deque, Optional, Tuple, Union


Number = Union[int, float]


class MedianFilter:
    """
    滑动窗口中值滤波器(Median Filter)
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

    def update(self, new_value: Number) -> Tuple[float, bool]:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        self.window.append(float(new_value))
        self.filtered = float(median(self.window))
        return self.filtered, len(self.window) == self.window_size

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self):
        """
        重置滤波器
        """
        self.window.clear()
        self.filtered = None
