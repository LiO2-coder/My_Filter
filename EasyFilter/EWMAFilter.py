import math
from typing import Optional, Union


Number = Union[int, float]


class EWMAFilter:
    """
    指数加权移动平均滤波器(Exponentially Weighted Moving Average Filter)
    """

    def __init__(self, alpha: float = 0.3):
        """
        初始化滤波器

        alpha: 平滑因子, 范围 [0, 1]
        """
        self.alpha: float = 0.3
        self.filtered: Optional[float] = None
        self.set_alpha(alpha)

    @staticmethod
    def _validate_number(value: Number, name: str):
        """
        校验输入是否为有效数值
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} 不能为 NaN 或 Inf")

    def set_alpha(self, alpha: float) -> None:
        """
        设置平滑因子

        alpha: 平滑因子, 范围 [0, 1]
        """
        self._validate_number(alpha, "alpha")
        if alpha < 0 or alpha > 1:
            raise ValueError("alpha 超出范围, 需满足 0 <= alpha <= 1")
        self.alpha = float(alpha)

    def update(self, new_value: Number) -> float:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        self._validate_number(new_value, "new_value")

        value = float(new_value)
        if self.filtered is None:
            self.filtered = value
        else:
            self.filtered = self.alpha * value + (1.0 - self.alpha) * self.filtered
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self, alpha: Optional[float] = None) -> None:
        """
        重置滤波器

        alpha: 可选, 重置时同时更新平滑因子
        """
        self.filtered = None
        if alpha is not None:
            self.set_alpha(alpha)
