from collections import deque
from typing import Union, Tuple

class SWMFilter:
    """
    滑动窗口均值滤波器(Sliding Window Mean Filter)
    """
    def __init__(self, window_size: int=5):
        """
        初始化滤波器

        window_size: 窗口大小
        """
        self.window = deque(maxlen=window_size)     # 固定长度队列
        self.window_size = window_size
        self.filted = None

    def update(self, new_value: Union[int, float])->Tuple[Union[int, float], bool]:
        """
        滤波器

        new_value: 新的测量值
        """
        if not isinstance(new_value, (int, float)):
            raise ValueError("传入值类型错误, 仅支持数值类型")
        
        self.window.append(new_value)

        if len(self.window) < self.window_size:
            self.filted = sum(self.window) / len(self.window)   # 窗口未满时部分计算
            return self.filted, False                           # 窗口未满时返回部分计算和False
        else:
            self.filted = sum(self.window) / self.window_size   # 完整窗口均值
            return self.filted, True                            # 完整窗口时返回均值和True



    def get_filted(self)->Union[int, float]:
        """
        获取滤波后的值
        """
        return self.filted


    def reset(self):
        """
        重置滤波器
        """
        self.window.clear()