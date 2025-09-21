from typing import Union

class EWMAFilter:
    """
    互补加权移动平均滤波器(Exponentially Weighted Moving Average Filter)
    """
    def __init__(self, alpha: float=0.3):
        """
        初始化滤波器

        alpha: 平滑因子(0-1)
        """
        self.set_alpha(alpha)     # 平滑因子(0-1)
        self.filted = None


    def set_alpha(self, alpha: float):
        """
        设置平滑因子, 0-1之间

        alpha: 平滑因子(0-1)
        """
        if alpha >1:
            alpha = 1
        elif alpha < 0:
            alpha = 0
            
        self.alpha = alpha
    

    def update(self, new_value: Union[int, float])->Union[int, float]:
        """
        滤波器

        new_value: 新的测量值
        """
        if self.filted is None:
            self.filted = new_value
        else:
            self.filtered = self.alpha * new_value + (1 - self.alpha) * self.filtered
        return self.filted


    def get_filted(self)->Union[int, float]:
        """
        获取当前滤波值
        """
        return self.filtered


    def reset(self, alpha: float=None):
        """
        重置滤波器
        """
        self.filted = None

        if alpha is not None:
            self.set_alpha(alpha)

    
