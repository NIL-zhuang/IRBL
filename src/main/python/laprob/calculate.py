import numpy as np
import matplotlib.pyplot as plt
import random
from math import ceil
from tqdm import tqdm
from collections import defaultdict
import json
import os
from constants import BHG_matrix, theta, markRate, bsPath, bbPath, F, final_score_path, projects_path, cheat_score_path
from mapper import BugSrcMapper
from util import BugIdx
from metric import Metric


class Calculate():
    '''
    初始化BHG，进行迭代计算直到BHG收敛，获得最终BHG图和预测结果
    '''

    def __init__(self, markLabelRate=0.05, quiet=False):
        self.W = np.load(BHG_matrix)
        self.bugIdx = BugIdx()
        self.bsMapper = BugSrcMapper()
        self.lossList = []
        self.quiet = quiet

        # 标记labeled，生成初始Y
        self.Y = np.load(bsPath)
        self.markedLabel = self.markLabeled(markLabelRate)
        # print(self.markedLabel)
        self.getY()
        self.F = self.Y.copy()

    def markLabeled(self, rate=markRate):
        '''
        选择rate%个bugReport，将其标记为labeled，在BHG图中对应位置进行标记
        '''
        bugCount = self.Y.shape[0]  # bug的数量
        return random.sample(range(0, bugCount), ceil(bugCount*rate))

    def getY(self):
        '''
        Y = [Y_{BL}; Y_{BU}; Ys]
        '''
        for marked in self.markedLabel:
            self.Y[marked] = 0
            bugId = self.bugIdx.getBugId(marked)
            fixedFiles = list(map(int, self.bsMapper.getBugFile(bugId)))
            self.Y[marked][fixedFiles] = 1
        sourceSize = self.Y.shape[1]
        self.Y = np.vstack((self.Y, np.eye(sourceSize)))

    def glh_process(self, F: np.ndarray):
        D = np.zeros((F.shape[1], F.shape[1]))
        for i in range(D.shape[0]):
            D[i][i] = 1 + np.nansum(F[self.markedLabel, i])
        F = np.dot(F, D)
        D = np.zeros((F.shape[0], F.shape[0]))
        for i in range(D.shape[1]):
            D[i][i] = 1 / np.nansum(F[i, :])
        F = np.dot(D,  F)
        return F

    def optimization(self, iter=1000):
        '''
        F* = (1-theta)(I-theta*W)^(-1)Y
        其中Y = getY()
        F0=Y, t=0, P = {}
        '''
        for i in range(iter):
            F_new = theta * np.dot(self.W, self.F) + (1-theta)*self.Y
            # F_new = self.glh_process(F_new)  # 添加了一个步骤
            loss = self.loss(F_new, self.F)
            if not self.quiet:
                print("Iteration {} round, loss: {}".format(i+1, loss))
            self.F = F_new
            if loss < 1e-5:
                break

    def loss(self, y1: np.ndarray, y2: np.ndarray):
        loss = np.sum((y1-y2)**2)
        self.lossList.append(loss)
        return loss

    def showRes(self):
        idx = list(range(1, len(self.lossList)+1))
        plt.plot(idx, self.lossList, 'o-', label='loss-iter')
        plt.xlabel('Iterations')
        plt.ylabel('Loss')
        plt.legend(loc='upper right')
        plt.show()

    def saveRes(self):
        np.save(F, self.F)
        predictRes = defaultdict(dict)
        for bugIdx in range(self.bugIdx.getBugNum()):
            # 标记过的bug忽略掉
            if bugIdx in self.markedLabel:
                continue
            bugId = self.bugIdx.getBugId(bugIdx)
            for fileIdx in range(self.F.shape[1]):
                predictRes[bugId][fileIdx] = self.F[bugIdx][fileIdx]
        # 查看要预测的bug数目
        # print(len(predictRes.keys()))
        with open(final_score_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(predictRes, indent=2))

    def saveCheatRes(self):
        def getAllBuggyFileIds():
            fileIds = set()
            mapper = json.load(open(os.path.join(projects_path, 'bug_src_map.json'), 'r'))
            for k, v in mapper.items():
                for item in v:
                    fileIds.add(int(item))
            return fileIds

        cheatF = np.copy(self.F)
        cheatFileIds = getAllBuggyFileIds()
        for col in range(cheatF.shape[1]):
            if col not in cheatFileIds:
                cheatF[:, col] = 0

        predictRes = defaultdict(dict)
        for bugIdx in range(self.bugIdx.getBugNum()):
            # 标记过的bug忽略掉
            if bugIdx in self.markedLabel:
                continue
            bugId = self.bugIdx.getBugId(bugIdx)
            for fileIdx in range(cheatF.shape[1]):
                predictRes[bugId][fileIdx] = cheatF[bugIdx][fileIdx]
        # 查看要预测的bug数目
        # print(len(predictRes.keys()))
        with open(cheat_score_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(predictRes, indent=2))


if __name__ == '__main__':
    calculate = Calculate(markLabelRate=markRate)
    calculate.optimization(iter=1000)
    calculate.saveRes()
    calculate.saveCheatRes()
