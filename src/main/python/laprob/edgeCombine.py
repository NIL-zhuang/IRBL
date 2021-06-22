import numpy as np
import os
from constants import projects_path, alpha, beta, BHG_matrix


class EdgeCombination():
    def __init__(self):
        self.bb = np.load(os.path.join(projects_path, 'bb.npy'))
        self.bs = np.load(os.path.join(projects_path, 'bs.npy'))
        self.ss = np.load(os.path.join(projects_path, 'ss.npy'))

    def getDiagonalD(self, matrix: np.ndarray):
        '''
        将获得的matrix矩阵归一化,获得矩阵D的逆矩阵
        '''
        size = matrix.shape[0]
        D = np.eye(size)
        for i in range(size):
            D[i][i] = np.sum(matrix[i])
        DInv = np.linalg.inv(D)
        return np.dot(DInv, matrix)

    def normalize(self):
        '''
        W = D-1W
        '''
        self.bb = self.getDiagonalD(self.bb)
        self.bs = self.getDiagonalD(self.bs)
        # ! 由于ss矩阵已经经过归一化，在这里就不对他进行额外处理，而且如果有无调用文件，其逆矩阵值为0
        # todo 可能需要对ss矩阵进行修复
        # self.ss = self.getDiagonalD(self.ss)

    def BHG(self, a=alpha, b=beta):
        '''
        (1-a)Wbb  aWbs
        (1-b)WbsT bWss
        '''
        wbb = (1-a)*self.bb
        wbs = a*self.bs
        wbst = (1-b)*(np.transpose(self.bs))
        wss = b * self.ss

        upper = np.hstack((wbb, wbs))
        lower = np.hstack((wbst, wss))
        bhg = np.vstack((upper, lower))
        np.save(BHG_matrix, bhg)


if __name__ == "__main__":
    edgeCombine = EdgeCombination()
    edgeCombine.normalize()
    edgeCombine.BHG()
