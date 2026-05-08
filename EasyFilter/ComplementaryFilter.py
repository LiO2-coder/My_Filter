from typing import Callable, Optional, Union


Number = Union[int, float]
PredictFunc = Callable[[float, Optional[Number]], Number]


class ComplementaryFilter:
    """
    互补滤波器(Complementary Filter)
    使用预测值与观测值进行加权融合
    """

    def __init__(self, alpha: float = 0.98, predict_func: Optional[PredictFunc] = None):
        """
        初始化滤波器

        alpha: 预测项权重, 范围 [0, 1]
        predict_func: 可选预测函数, 签名为 predict_func(last_filtered, control)
        """
        self.alpha = 0.98
        self.predict_func = predict_func
        self.filtered: Optional[float] = None
        self.set_alpha(alpha)

    def set_alpha(self, alpha: Number):
        """
        设置融合权重
        """
        if not isinstance(alpha, (int, float)) or isinstance(alpha, bool):
            raise ValueError("alpha 类型错误, 仅支持数值类型")
        if alpha < 0 or alpha > 1:
            raise ValueError("alpha 超出范围, 需满足 0 <= alpha <= 1")
        self.alpha = float(alpha)

    def update(
        self,
        measurement: Number,
        prediction: Optional[Number] = None,
        control: Optional[Number] = None,
    ) -> float:
        """
        使用观测与预测更新滤波器

        measurement: 观测值
        prediction: 可选外部预测值, 传入时优先使用
        control: 传给 predict_func 的控制量
        """
        if not isinstance(measurement, (int, float)) or isinstance(measurement, bool):
            raise ValueError("measurement 类型错误, 仅支持数值类型")

        measurement_f = float(measurement)

        if prediction is None:
            if self.predict_func is not None and self.filtered is not None:
                predicted = self.predict_func(self.filtered, control)
                if not isinstance(predicted, (int, float)) or isinstance(predicted, bool):
                    raise ValueError("predict_func 返回值类型错误, 仅支持数值类型")
                prediction_f = float(predicted)
            elif self.filtered is not None:
                prediction_f = self.filtered
            else:
                prediction_f = measurement_f
        else:
            if not isinstance(prediction, (int, float)) or isinstance(prediction, bool):
                raise ValueError("prediction 类型错误, 仅支持数值类型")
            prediction_f = float(prediction)

        self.filtered = self.alpha * prediction_f + (1.0 - self.alpha) * measurement_f
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self, alpha: Optional[Number] = None):
        """
        重置滤波器

        alpha: 可选, 重置时同时更新融合权重
        """
        self.filtered = None
        if alpha is not None:
            self.set_alpha(alpha)
