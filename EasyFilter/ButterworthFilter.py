from typing import Optional, Tuple, Union

import numpy as np

from scipy.signal import butter, sosfilt


Number = Union[int, float]


class ButterworthFilter:
    """
    巴特沃斯滤波器(Butterworth Filter)
    基于scipy.signal.butter + sosfilt的流式实现
    """

    def __init__(
        self,
        order: int = 2,
        cutoff: Union[Number, Tuple[Number, Number]] = 2.0,
        fs: Number = 50.0,
        btype: str = "lowpass",
    ):
        """
        初始化滤波器

        order: 滤波器阶数, 必须大于 0
        cutoff: 截止频率
        fs: 采样频率, 必须大于 0
        btype: 滤波类型, 支持 lowpass/highpass/bandpass/bandstop
        """
        self.order = 2
        self.cutoff: Union[float, Tuple[float, float]] = 2.0
        self.fs = 50.0
        self.btype = "lowpass"

        self.sos: Optional[np.ndarray] = None
        self.zi: Optional[np.ndarray] = None
        self.filtered: Optional[float] = None

        self._configure(order=order, cutoff=cutoff, fs=fs, btype=btype)

    @staticmethod
    def _validate_number(value: Number, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} 类型错误, 仅支持数值类型")

    def _validate_cutoff(self, cutoff, fs: float, btype: str):
        nyquist = fs / 2.0

        if btype in {"lowpass", "highpass"}:
            self._validate_number(cutoff, "cutoff")
            cutoff_value = float(cutoff)
            if not (0 < cutoff_value < nyquist):
                raise ValueError("cutoff 超出范围, 需满足 0 < cutoff < fs/2")
            return cutoff_value

        if btype in {"bandpass", "bandstop"}:
            if not isinstance(cutoff, (tuple, list)) or len(cutoff) != 2:
                raise ValueError("bandpass/bandstop 模式下 cutoff 需为长度为 2 的元组")
            low, high = cutoff
            self._validate_number(low, "cutoff[0]")
            self._validate_number(high, "cutoff[1]")
            low_f = float(low)
            high_f = float(high)
            if not (0 < low_f < high_f < nyquist):
                raise ValueError("cutoff 超出范围, 需满足 0 < low < high < fs/2")
            return (low_f, high_f)

        raise ValueError("不支持的 btype, 仅支持 lowpass/highpass/bandpass/bandstop")

    def _configure(
        self,
        order: int,
        cutoff: Union[Number, Tuple[Number, Number]],
        fs: Number,
        btype: str,
    ):
        if not isinstance(order, int) or isinstance(order, bool):
            raise ValueError("order 类型错误, 仅支持整数")
        if order <= 0:
            raise ValueError("order 必须大于 0")

        self._validate_number(fs, "fs")
        fs_f = float(fs)
        if fs_f <= 0:
            raise ValueError("fs 必须大于 0")

        if not isinstance(btype, str):
            raise ValueError("btype 类型错误, 仅支持字符串")
        btype_lower = btype.lower()

        cutoff_checked = self._validate_cutoff(cutoff, fs_f, btype_lower)

        self.order = order
        self.cutoff = cutoff_checked
        self.fs = fs_f
        self.btype = btype_lower

        self.sos = butter(
            N=self.order,
            Wn=self.cutoff,
            btype=self.btype,
            fs=self.fs,
            output="sos",
        )
        self.zi = np.zeros((self.sos.shape[0], 2), dtype=float)

    def update(self, new_value: Number) -> float:
        """
        使用新值更新滤波器

        new_value: 新的测量值
        """
        self._validate_number(new_value, "new_value")
        sample = np.asarray([float(new_value)], dtype=float)

        if self.sos is None or self.zi is None:
            raise RuntimeError("滤波器尚未正确初始化")

        filtered, self.zi = sosfilt(self.sos, sample, zi=self.zi)
        self.filtered = float(filtered[-1])
        return self.filtered

    def get_filtered(self) -> Optional[float]:
        """
        获取当前滤波值
        """
        return self.filtered

    def reset(self):
        """
        重置滤波器状态
        """
        if self.sos is None:
            raise RuntimeError("滤波器尚未正确初始化")
        self.zi = np.zeros((self.sos.shape[0], 2), dtype=float)
        self.filtered = None
