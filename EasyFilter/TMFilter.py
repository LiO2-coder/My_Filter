from collections import deque
from typing import Deque, Optional, Tuple, Union


Number = Union[int, float]


class TMFilter:
    """
    滑动窗口截尾均值滤波器(Trimmed Mean Filter)
    """

    def __init__(self, window_size: int = 5, trim_size: int = 1):
        """
        初始化滤波器

        window_size: 窗口大小, 必须大于 0
        trim_size: 每侧裁剪样本数, 需满足 2 * trim_size < window_size
        """
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise ValueError("window_size 类型错误, 仅支持整数")
        if not isinstance(trim_size, int) or isinstance(trim_size, bool):
            raise ValueError("trim_size 类型错误, 仅支持整数")
        if window_size <= 0:
            raise ValueError("window_size 必须大于 0")
        if trim_size < 0:
            raise ValueError("trim_size 必须大于等于 0")
        if 2 * trim_size >= window_size:
            raise ValueError("参数不合法, 需满足 2 * trim_size < window_size")

        self.window_size = window_size
        self.trim_size = trim_size
        self.window: Deque[float] = deque(maxlen=window_size)
        self.filtered: Optional[float] = None

    def _compute_trimmed_mean(self) -> float:
        values = sorted(self.window)
        n = len(values)

        if n == 0:
            raise RuntimeError("窗口为空, 无法计算截尾均值")

        trim = self.trim_size
        if 2 * trim >= n:
            trimmed = values
        elif trim == 0:
            trimmed = values
        else:
            trimmed = values[trim : n - trim]

        return sum(trimmed) / len(trimmed)

    def update(self, new_value: Number) -> Tuple[float, bool]:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        self.window.append(float(new_value))
        self.filtered = self._compute_trimmed_mean()
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
