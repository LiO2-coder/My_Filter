# MyFilter - 轻量级滤波器库
一个简单易用的 Python 滤波器库，包含多种常用的一维数据滤波算法。

## 项目结构

```
main/
├── MyFilter/                    # 主包目录
│   ├── EWMAFilter.py           # 指数加权移动平均滤波器
│   ├── KalmanFilter.py         # 卡尔曼滤波器
│   ├── SWMFilter.py            # 滑动窗口均值滤波器
│   └── __init__.py             # 包初始化文件
├── LICENSE                     # 许可证文件
├── README.md                   # 项目说明文档
├── fileList.txt                # 文件列表
└── requirements.txt            # 依赖包列表
```

## 特性

- 🚀 **轻量级**：纯 Python 实现，依赖简单
- 📦 **开箱即用**：简单的 API 设计，快速上手
- 🔧 **可扩展**：易于集成到现有项目中
- 📊 **多种算法**：包含三种常用滤波器

## 安装

```bash
git clone https://github.com/LiO2-coder
/MyFilter.git
cd MyFilter
pip install -r requirements.txt
```

## 依赖

- Python 3.6+
- numpy>=1.19.0

## 滤波器介绍

### 1. 滑动窗口均值滤波器 (SWMFilter)
- **原理**：使用固定大小的窗口，计算窗口内数据的算术平均值
- **适用场景**：数据波动较大，需要平滑处理的场景
- **参数**：`window_size` - 窗口大小

### 2. 指数加权移动平均滤波器 (EWMAFilter)
- **原理**：对历史数据赋予指数衰减的权重，新数据权重更高
- **适用场景**：需要快速响应数据变化，同时保持一定平滑性
- **参数**：`alpha` - 平滑因子 (0-1)，值越大对新数据响应越快

### 3. 卡尔曼滤波器 (KalmanFilter)
- **原理**：基于状态空间模型，通过预测和更新两个步骤进行最优估计
- **适用场景**：系统有明确模型，需要最优估计的场景
- **参数**：多种状态矩阵参数，可根据系统特性调整

## 快速开始

### 基本使用

```python
from MyFilter import SWMFilter, EWMAFilter, KalmanFilter
import numpy as np

# 生成示例数据
data = np.random.randn(100) + 5  # 带噪声的数据

# 滑动窗口均值滤波器
swm_filter = SWMFilter(window_size=5)
filtered_swm = []
for value in data:
    result, is_full = swm_filter.update(value)
    filtered_swm.append(result)

# 指数加权移动平均滤波器
ewma_filter = EWMAFilter(alpha=0.3)
filtered_ewma = []
for value in data:
    result = ewma_filter.update(value)
    filtered_ewma.append(result)

# 卡尔曼滤波器
kf = KalmanFilter(x=0, Q=0.1, R=1)  # 初始状态为0
filtered_kalman = []
for value in data:
    kf.update(value)
    filtered_kalman.append(kf.get_x())
```

### 详细示例

```python
# 滑动窗口均值滤波器示例
swm = SWMFilter(window_size=3)
print("SWMFilter 示例:")
for i, value in enumerate([1, 2, 3, 4, 5]):
    filtered, full_window = swm.update(value)
    print(f"输入: {value}, 输出: {filtered:.2f}, 窗口满: {full_window}")

# 指数加权移动平均滤波器示例
ewma = EWMAFilter(alpha=0.5)
print("\nEWMAFilter 示例:")
for i, value in enumerate([1, 2, 3, 2, 1]):
    filtered = ewma.update(value)
    print(f"输入: {value}, 输出: {filtered:.2f}")

# 卡尔曼滤波器示例
kf = KalmanFilter(x=0, P=1, Q=0.1, R=1)
print("\nKalmanFilter 示例:")
measurements = [1.1, 1.9, 3.2, 4.1, 4.8]
for i, z in enumerate(measurements):
    kf.update(z)
    print(f"观测值: {z:.1f}, 估计值: {kf.get_x():.2f}, 卡尔曼增益: {kf.get_KK():.3f}")
```

## API 文档

### SWMFilter 类

```python
SWMFilter(window_size: int = 5)
```
- `update(new_value)`: 更新滤波器，返回 (滤波值, 窗口是否满)
- `get_filted()`: 获取当前滤波值
- `reset()`: 重置滤波器状态

### EWMAFilter 类

```python
EWMAFilter(alpha: float = 0.3)
```
- `update(new_value)`: 更新滤波器，返回滤波值
- `get_filted()`: 获取当前滤波值
- `set_alpha(alpha)`: 设置平滑因子
- `reset(alpha=None)`: 重置滤波器

### KalmanFilter 类

```python
KalmanFilter(x, A=1, B=None, H=1, Q=0.1, R=1, P=1)
```
- `update(z)`: 使用观测值更新滤波器
- `get_x()`: 获取当前状态估计值
- `get_KK()`: 获取当前卡尔曼增益
- `get_P()`: 获取状态估计误差协方差
- `get_Q()`, `get_R()`: 获取噪声协方差

## 应用场景

- **传感器数据处理**：温度、湿度、位置等传感器数据的平滑处理
- **金融时间序列**：股票价格、汇率等金融数据的趋势分析
- **运动跟踪**：鼠标轨迹、物体运动轨迹的平滑
- **信号处理**：音频信号、生物信号等一维信号的去噪

## TODO: 开发计划(作者给自己画饼)

### 滤波器扩展
后续版本将增加更多实用的滤波器算法：
- **中值滤波器** (Median Filter) - 有效去除脉冲噪声
- **巴特沃斯滤波器** (Butterworth Filter) - 频域滤波
- **粒子滤波器** (Particle Filter) - 非线性非高斯系统
- **无迹卡尔曼滤波器** (Unscented Kalman Filter) - 非线性系统
- **扩展卡尔曼滤波器** (Extended Kalman Filter) - 非线性系统近似

### 卡尔曼滤波器升级
当前 v1.0 版本为简单的一阶卡尔曼滤波器，后续将更新：
- **多维卡尔曼滤波器** - 支持多状态变量
- **自适应卡尔曼滤波器** - 动态调整噪声参数
- **联邦卡尔曼滤波器** - 多传感器数据融合
- **容积卡尔曼滤波器** (Cubature Kalman Filter) - 高精度非线性估计

### 开发C++版本

## 贡献

欢迎提交 Issue 和 Pull Request！对于新功能建议或问题反馈，请创建 GitHub Issue。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 作者

- **LiO2** - [2099602919@qq.com](mailto:2099602919@qq.com)
- **GitHub**: [https://github.com/LiO2-coder](https://github.com/LiO2-coder)

## 版本历史

- **v1.0** - 初始版本发布
  - 实现三种基本滤波器
  - 提供完整的 API 文档和示例

## 支持

如果您在使用过程中遇到任何问题，可以通过以下方式联系：
- 邮箱: 2099602919@qq.com
- GitHub Issues: [项目 Issues 页面](https://github.com/LiO2-coder/MyFilter/issues)

---

⭐ 第一次上传项目，如果这个项目对您有帮助，请给个Star！
