class KalmanFilter:
    """
    卡尔曼滤波器(Kalman Filter)
    该滤波器仅适用于一维状态估计，无法处理非线性问题
    """
    def __init__(self, x, A=1, B=None, H=1, Q=0.1, R=1, P=1):
        """
        初始化滤波器

        A: 状态转移矩阵,描述上一时刻的状态如何转移到当前时刻
        B: 控制输入矩阵,描述控制输入如何影响状态转移

        H: 状态观测矩阵,描述当前状态如何观测到测量值
        
        Q: 过程噪声协方差矩阵Q,p(w)~N(0,Q),噪声来自真实世界中的不确定性
        R: 观测噪声协方差矩阵R,p(v)~N(0,R),噪声因测量而来
        P: 状态估计协方差矩阵,描述当前状态的估计值与真实值之间的误差
        """
        self.x = x                  # 初始状态值
        self.A = A                  # 状态转移矩阵
        self.B = B                  # 控制输入矩阵

        self.H = H                  # 状态观测矩阵
        
        self.Q = Q                  # 过程噪声协方差矩阵
        self.P = P                  # 初始状态误差协方差矩阵
        self.R = R                  # 观测噪声协方差矩阵

        self.KK = 0                 # Kalman Gain
        self.x_prior = None         # 先验估计值
        self.P_prior = None         # 先验估计误差协方差矩阵
        self.x_posterior = None     # 后验估计值
        self.P_posterior = None     # 后验估计误差协方差矩阵


    def prior(self):
        """
        先验估计
        """
        self.x_prior = self.A * self.x              
        # np.dot(self.A, self.x)
        self.P_prior = self.A**2 * self.P + self.Q  
        # np.dot(np.dot(self.A, self.P), self.A.T) + self.Q


    def update_KK(self):
        """
        更新卡尔曼增益
        """
        KK_1 = self.P_prior * self.H                
        # np.dot(self.P_prior, self.H.T)
        KK_2 = self.H**2 * self.P_prior + self.R    
        # np.dot(np.dot(self.H, self.P_prior), self.H.T) + self.R
        self.KK = KK_1 / KK_2                       
        # np.dot(kK_1, np.linalg.inv(KK_2))


    def posterior(self, z):
        """
        后验估计
        """
        self.x_posterior = self.x_prior + self.KK * (z - self.H*self.x_prior)   
        # self.x_prior + self.KK @ (z - np.dot(self.H, self.x_prior))
        self.P_posterior = self.P_prior - self.KK * self.H * self.P_prior
        # self.P_prior - self.KK @ np.dot(self.H, self.P_prior)


    def update(self, z: float):
        """
        更新滤波器
        
        z: 观测值
        """
        self.prior()
        self.update_KK()
        self.posterior(z)
        self.x = self.x_posterior
        self.P = self.P_posterior


    def get_x(self)->float:
        """
        获取当前估计值
        """
        return self.x


    def get_KK(self)->float:
        """
        获取当前卡尔曼增益
        """
        return self.KK
    
    
    def get_P(self)->float:
        """
        获取当前状态估计误差协方差矩阵
        """
        return self.P
    

    def get_Q(self)->float:
        """
        获取过程噪声协方差矩阵
        """
        return self.Q
    

    def get_R(self)->float:
        """
        获取观测噪声协方差矩阵
        """
        return self.R