import numpy as np


def getCosSimMatrix(v1: np.ndarray, v2: np.ndarray):
    '''结果的维度是 v1 * v2'''
    num = np.dot(np.array(v1), np.array(v2).T)    # 各向量点乘
    denom = np.linalg.norm(v1, axis=1).reshape(-1, 1) * np.linalg.norm(v2, axis=1)  # 模长的乘积
    res = num / denom
    # 将所有的inf或者nan值标记为0
    res[np.isinf(res)] = 0
    res[np.isnan(res)] = 0
    return 0.5+0.5*res
