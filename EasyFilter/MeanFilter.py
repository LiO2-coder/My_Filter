from typing import Optional, Union


Number = Union[int, float]


class MeanFilter:
    """
    累计均值滤波器(Cumulative Mean Filter)
    """

    def __init__(self):
        """
        初始化滤波器
        """
        self.count = 0
        self.total = 0.0
        self.filtered: Optional[float] = None

    def update(self, new_value: Number) -> float:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        self.count += 1
        self.total += float(new_value)
        self.filtered = self.total / self.count
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self):
        """
        重置滤波器
        """
        self.count = 0
        self.total = 0.0
        self.filtered = None
