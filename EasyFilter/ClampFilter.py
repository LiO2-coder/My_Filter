from typing import Optional, Union


Number = Union[int, float]


class ClampFilter:
    """
    限幅滤波器(Clamp Filter)
    """

    def __init__(self, min_value: Optional[Number] = None, max_value: Optional[Number] = None):
        """
        初始化滤波器

        min_value: 下限, 为 None 时不限制下限
        max_value: 上限, 为 None 时不限制上限
        """
        self.min_value: Optional[float] = None
        self.max_value: Optional[float] = None
        self.filtered: Optional[float] = None
        self.set_limits(min_value=min_value, max_value=max_value)

    def set_limits(self, min_value: Optional[Number] = None, max_value: Optional[Number] = None):
        """
        设置上下限
        """
        if min_value is not None:
            if not isinstance(min_value, (int, float)) or isinstance(min_value, bool):
                raise ValueError("min_value 类型错误, 仅支持数值类型")
            min_cast = float(min_value)
        else:
            min_cast = None

        if max_value is not None:
            if not isinstance(max_value, (int, float)) or isinstance(max_value, bool):
                raise ValueError("max_value 类型错误, 仅支持数值类型")
            max_cast = float(max_value)
        else:
            max_cast = None

        if min_cast is not None and max_cast is not None and min_cast > max_cast:
            raise ValueError("参数不合法, min_value 不能大于 max_value")

        self.min_value = min_cast
        self.max_value = max_cast

    def update(self, new_value: Number) -> float:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)) or isinstance(new_value, bool):
            raise ValueError("传入值类型错误, 仅支持数值类型")

        value = float(new_value)
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)

        self.filtered = value
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self, min_value: Optional[Number] = None, max_value: Optional[Number] = None):
        """
        重置滤波器

        min_value/max_value: 可选, 重置时同时更新上下限
        """
        self.filtered = None
        if min_value is not None or max_value is not None:
            self.set_limits(min_value=min_value, max_value=max_value)
