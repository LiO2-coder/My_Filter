from typing import Optional, Union


Number = Union[int, float]


class HysteresisFilter:
    """
    滞回滤波器(Hysteresis Filter)
    变化量未超过 deadband 时保持上一输出
    """

    def __init__(self, deadband: float = 0.1):
        """
        初始化滤波器

        deadband: 死区阈值, 必须大于等于 0
        """
        self.deadband = 0.1
        self.filtered: Optional[float] = None
        self.set_deadband(deadband)

    def set_deadband(self, deadband: Number):
        """
        设置死区阈值
        """
        if not isinstance(deadband, (int, float)) or isinstance(deadband, bool):
            raise ValueError("deadband 类型错误, 仅支持数值类型")
        if deadband < 0:
            raise ValueError("deadband 必须大于等于 0")
        self.deadband = float(deadband)

    def update(self, new_value: Number) -> float:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        value = float(new_value)
        if self.filtered is None:
            self.filtered = value
            return self.filtered

        if abs(value - self.filtered) >= self.deadband:
            self.filtered = value
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self, deadband: Optional[Number] = None):
        """
        重置滤波器

        deadband: 可选, 重置时同时更新死区阈值
        """
        self.filtered = None
        if deadband is not None:
            self.set_deadband(deadband)
