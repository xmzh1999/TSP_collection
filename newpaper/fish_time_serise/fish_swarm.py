import numpy as np
from scipy import spatial


# class ASFA_raw:
#     # 这里统一做成极小值求解的问题
#     # 参考某 Matlab 教课书上的代码，很多地方的设定无力吐槽，基本没有泛用性
#     def __init__(self, func):
#         self.func = func
#         self.fish_num = 50
#         self.max_iter = 300
#         self.n_dim = 2
#         self.max_try_num = 100  # 最大尝试次数
#         self.step = 0.1  # 每一步的最大位移
#         self.visual = 0.5  # 鱼的最大感知范围
#         self.delta = 1.3  # 拥挤度阈值
#
#         self.X = np.random.rand(self.fish_num, self.n_dim)
#         self.Y = np.array([self.func(x) for x in self.X])
#
#         best_idx = self.Y.argmin()
#         self.best_Y = self.Y[best_idx]
#         self.best_X = self.X[best_idx, :]
#
#     def move_to_target(self, index_individual, x_target):
#         # 向目标移动，prey(), swarm(), follow() 三个算子中的移动都用这个
#         x = self.X[index_individual, :]
#         x_new = x + self.step * np.random.rand() * (x_target - x) / np.linalg.norm(x_target - x)
#         self.X[index_individual, :] = x_new
#         self.Y[index_individual] = self.func(x_new)
#         if self.Y[index_individual] < self.best_Y:
#             self.best_X = self.X[index_individual, :]
#
#     def move(self, index_individual):
#         r = 2 * np.random.rand(self.n_dim) - 1
#         x_new = self.X[index_individual, :] + self.visual * r
#         self.X[index_individual, :] = x_new
#         self.Y[index_individual] = self.func(x_new)
#         if self.Y[index_individual] < self.best_Y:
#             self.best_X = self.X[index_individual, :]
#
#     def prey(self, index_individual):
#         for try_num in range(self.max_try_num):
#             r = 2 * np.random.rand(self.n_dim) - 1
#             x_target = self.X[index_individual, :] + self.visual * r
#             if self.func(x_target) < self.Y[index_individual]:  # 捕食成功
#                 print('prey',index_individual)
#                 self.move_to_target(index_individual, x_target)
#                 return None
#         # 捕食 max_try_num 次后仍不成功，就调用 move 算子
#         self.move(index_individual)
#
#     def find_individual_in_vision(self, index_individual):
#         # 找出 index_individual 这个个体视线范围内的所有鱼
#         distances = spatial.distance.cdist(self.X[[index_individual], :], self.X, metric='euclidean').reshape(-1)
#         index_individual_in_vision = np.argwhere((distances > 0) & (distances < self.visual))[:, 0]
#         return index_individual_in_vision
#
#     def swarm(self, index_individual):
#         index_individual_in_vision = self.find_individual_in_vision(index_individual)
#         num_index_individual_in_vision = len(index_individual_in_vision)
#         if num_index_individual_in_vision > 0:
#             individual_in_vision = self.X[index_individual_in_vision, :]
#             center_individual_in_vision = individual_in_vision.mean(axis=0)
#             center_y_in_vision = self.func(center_individual_in_vision)
#             if center_y_in_vision * num_index_individual_in_vision < self.delta * self.Y[index_individual]:
#                 self.move_to_target(index_individual, center_individual_in_vision)
#                 return None
#         self.prey(index_individual)
#
#     def follow(self, index_individual):
#         index_individual_in_vision = self.find_individual_in_vision(index_individual)
#         num_index_individual_in_vision = len(index_individual_in_vision)
#         if num_index_individual_in_vision > 0:
#             individual_in_vision = self.X[index_individual_in_vision, :]
#             y_in_vision = np.array([self.func(x) for x in individual_in_vision])
#             index_target = y_in_vision.argmax()
#             x_target = individual_in_vision[index_target]
#             y_target = y_in_vision[index_target]
#             if y_target * num_index_individual_in_vision < self.delta * self.Y[index_individual]:
#                 self.move_to_target(index_individual, x_target)
#                 return None
#         self.prey(index_individual)
#
#     def fit(self):
#         for epoch in range(self.max_iter):
#             for index_individual in range(self.fish_num):
#                 self.swarm(index_individual)
#                 self.follow(index_individual)
#         return self.best_X, self.best_Y

# %%
class AFSA:
    def __init__(self, func, n_dim, fish_num=50, max_iter=300,
                 max_try_num=100, step=0.5, visual=0.3,
                 q=0.98, delta=0.5):
        self.func = func
        self.n_dim = n_dim  # 鱼参数维度d
        self.fish_num = fish_num  # 鱼的数量
        self.max_iter = max_iter  # 最大迭代次数
        self.max_try_num = max_try_num  # 最大尝试捕食次数
        self.step = step  # 每一步的最大位移比例
        self.visual = visual  # 鱼的最大感知范围
        self.q = q  # 鱼的感知范围衰减系数
        self.delta = delta  # 拥挤度阈值，越大越容易聚群和追尾

        self.X = np.random.rand(self.fish_num, self.n_dim)  # 生成数量*参数维度的输入矩阵 初始是随机的
        self.Y = np.array([self.func(x) for x in self.X])  # 通过func函数由x生成y并转为数组

        best_idx = self.Y.argmin()  # 获取适应度最小值
        self.best_x, self.best_y = self.X[best_idx, :], self.Y[best_idx]
        self.best_X, self.best_Y = self.best_x, self.best_y  # will be deprecated, use lowercase

    def move_to_target(self, idx_individual, x_target):
        """
        idx_individual索引move to x_target 方向
        called by prey(), swarm(), follow()

        :param idx_individual:
        :param x_target:
        :return:
        """
        x = self.X[idx_individual, :]  # idx_individual索引的鱼
        x_new = x + self.step * np.random.rand() * ((x_target - x) / np.linalg.norm(x_target - x))  # 单位方向向量
        # x_new = x_target
        self.X[idx_individual, :] = x_new  # 移动后新坐标传给X
        self.Y[idx_individual] = self.func(x_new)  # 计算新坐标适应度
        if self.Y[idx_individual] < self.best_Y:  # 若新坐标适应度小于全局最小适应度 则更新全局最小
            self.best_x = self.X[idx_individual, :].copy()
            self.best_y = self.Y[idx_individual].copy()

    def move(self, idx_individual):
        '''
        randomly move to a point
        随机移动
        :param idx_individual:
        :return:
        '''
        # r = 2 * np.random.rand(self.n_dim) - 1
        x_new = self.X[idx_individual, :] + self.visual * np.random.uniform(-1, 1)
        self.X[idx_individual, :] = x_new
        self.Y[idx_individual] = self.func(x_new)
        if self.Y[idx_individual] < self.best_Y:
            self.best_X = self.X[idx_individual, :].copy()
            self.best_Y = self.Y[idx_individual].copy()

    def prey(self, idx_individual):
        '''
        prey 觅食行为 趋向低适应度
        :param idx_individual:
        :return:
        '''
        for try_num in range(self.max_try_num):  # 最大尝试次数
            # r = 2 * np.random.rand(self.n_dim) - 1
            x_target = self.X[idx_individual, :] + self.visual * np.random.uniform(-1, 1)
            if self.func(x_target) < self.Y[idx_individual]:  # 捕食成功
                self.move_to_target(idx_individual, x_target)
                return None
        # 捕食 max_try_num 次后仍不成功，就调用 move 算子
        self.move(idx_individual)

    def find_individual_in_vision(self, idx_individual):
        """
        找出 idx_individual 这条鱼视线范围内的所有鱼
        :param idx_individual:
        :return:
        """
        distances = spatial.distance.cdist(self.X[[idx_individual], :], self.X, metric='euclidean').reshape(-1)
        # np.argwhere(x) 返回满足x条件的矩阵坐标
        idx_individual_in_vision = np.argwhere((distances > 0) & (distances < self.visual))[:, 0]
        return idx_individual_in_vision

    def swarm(self, idx_individual):
        """
        聚群行为 从find_individual_in_vision()获取感受野所有鱼的索引 计算集群中心
        :param idx_individual:
        :return:
        """
        idx_individual_in_vision = self.find_individual_in_vision(idx_individual)
        num_idx_individual_in_vision = len(idx_individual_in_vision)
        if num_idx_individual_in_vision > 0:  # 邻域鱼数量大于零
            individual_in_vision = self.X[idx_individual_in_vision, :]
            center_individual_in_vision = individual_in_vision.mean(axis=0)  # 聚群中心
            center_y_in_vision = self.func(center_individual_in_vision)
            # 中心适宜度 * 邻域鱼数量 < 拥挤度 * 当前位置适宜度
            if center_y_in_vision * num_idx_individual_in_vision < self.delta * self.Y[idx_individual]:
                self.move_to_target(idx_individual, center_individual_in_vision)
                return None
        # 没有鱼执行觅食行为
        self.prey(idx_individual)

    def follow(self, idx_individual):
        """
        追尾行为
        :param idx_individual:
        :return:
        """
        # 获取idx_individual索引视野内所有鱼的索引
        idx_individual_in_vision = self.find_individual_in_vision(idx_individual)
        num_idx_individual_in_vision = len(idx_individual_in_vision)
        if num_idx_individual_in_vision > 0:
            individual_in_vision = self.X[idx_individual_in_vision, :]
            y_in_vision = np.array([self.func(x) for x in individual_in_vision])
            idx_target = y_in_vision.argmin()
            x_target = individual_in_vision[idx_target]
            y_target = y_in_vision[idx_target]
            if y_target * num_idx_individual_in_vision < self.delta * self.Y[idx_individual]:
                self.move_to_target(idx_individual, x_target)
                return None
        self.prey(idx_individual)

    def run(self, max_iter=None):
        self.max_iter = max_iter or self.max_iter
        for epoch in range(self.max_iter):
            for idx_individual in range(self.fish_num):
                self.swarm(idx_individual)  # 聚群
                self.follow(idx_individual)  # 追尾
            self.visual *= self.q
        self.best_X, self.best_Y = self.best_x, self.best_y  # will be deprecated, use lowercase
        return self.best_x, self.best_y
