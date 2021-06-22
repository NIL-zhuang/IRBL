from util import VectorBuilder, JSONReader
from util import BugIdx
import numpy as np
from tqdm import tqdm
from math import ceil
from constants import projects_path, bugs
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict


class BugBugSim:
    """
    Here we uses TF-IDF to calculate the similarity between bugReports
    M = tf * idf
    """

    def __init__(self):
        self.vectorBuilder = VectorBuilder()
        self.bugIdx = BugIdx()
        self.bugs = JSONReader(bugs).readFile()

        # summary_summary_corpus = []
        # self.sum_sum = defaultdict(list)
        # self.ss_bug2idx = defaultdict(int)
        # idx = 0
        # for b_idx in tqdm(self.bugs, desc='load bug corpus'):
        #     summary_summary_corpus.append(' '.join(self.bugs[b_idx]['summary']))
        #     self.ss_bug2idx[b_idx] = idx
        #     idx += 1
        # vectorizer = CountVectorizer()
        # X = vectorizer.fit_transform(summary_summary_corpus)
        # transformer = TfidfTransformer()
        # tfidf = transformer.fit_transform(X)
        # self.sum_sum_vectors = tfidf.toarray()

        # desc_desc_corpus = []
        # self.desc_desc = defaultdict(list)
        # self.dd_bug2idx = defaultdict(int)
        # descIdx = 0
        # for b_idx in tqdm(self.bugs, desc='load code corpus'):
        #     desc_desc_corpus.append(' '.join(self.bugs[b_idx]['description']))
        #     self.dd_bug2idx[b_idx] = descIdx
        #     descIdx += 1
        # vectorizer = CountVectorizer()
        # X = vectorizer.fit_transform(desc_desc_corpus)
        # transformer = TfidfTransformer()
        # tfidf = transformer.fit_transform(X)
        # self.desc_desc_vectors = tfidf.toarray()

    def calculate_sim(self, bugIdx1, bugIdx2):
        """
        计算两个bug报告之间的相似度
        :param bugIdx1: 第一个报告的id
        :param bugIdx2: 第二个报告的id
        :return: 返回tf-idf相似度
        """
        # sum_sum_sim = self.calculateSummarySim(bugIdx1, bugIdx2)
        # desc_desc_sim = self.calculateDescSim(bugIdx1, bugIdx2)
        totalSim = self.calculateTotalSim(bugIdx1, bugIdx2)
        return totalSim
        # return (totalSim * 2 + sum_sum_sim * 2 + desc_desc_sim)/5

    def calculateSummarySim(self, bugIdx1, bugIdx2):
        sum1 = self.sum_sum_vectors[self.ss_bug2idx[bugIdx1]]
        sum2 = self.sum_sum_vectors[self.ss_bug2idx[bugIdx2]]
        return self.getCosSim(sum1, sum2)

    def calculateDescSim(self, bugIdx1, bugIdx2):
        desc1 = self.desc_desc_vectors[self.dd_bug2idx[bugIdx1]]
        desc2 = self.desc_desc_vectors[self.dd_bug2idx[bugIdx2]]
        return self.getCosSim(desc1, desc2)

    def calculateTotalSim(self, bugIdx1, bugIdx2):
        vec1 = np.array(self.vectorBuilder.get_vector(bugIdx1, is_reportId=True))
        vec2 = np.array(self.vectorBuilder.get_vector(bugIdx2, is_reportId=True))
        return self.getCosSim(vec1, vec2)

    def calculateMatrix(self):
        keys = len(self.bugIdx.getAllBugId())
        matrix = np.eye(keys)
        for i in tqdm(range(keys), desc='Loading bugbug matrix'):
            for j in range(i + 1, keys):
                sim = self.calculate_sim(self.bugIdx.getBugId(i), self.bugIdx.getBugId(j))
                matrix[i][j] = matrix[j][i] = sim
        return matrix

    def calculateMatrixRefine(self):
        def initBugVec():
            '''
            将所有的bug向量都加载到一个列表里
            '''
            bugVecList = []
            for i in range(len(self.bugIdx.getAllBugId())):
                bugIdx = self.bugIdx.getBugId(i)
                bugVec = np.array(self.vectorBuilder.get_vector(bugIdx, is_reportId=True))
                bugVecList.append(bugVec)
            return bugVecList

        bugVecs = initBugVec()
        print("Finish load bug vectors")
        from vector_sim import getCosSimMatrix
        return getCosSimMatrix(bugVecs, bugVecs)

    @staticmethod
    def getCosSim(vector1, vector2):
        def getCosRes():
            return vector1 @ vector2 / (np.linalg.norm(vector1)*np.linalg.norm(vector2))
        sim = getCosRes()
        if np.isnan(sim):
            return 0
        return sim

    def simplify(self, matrix: np.ndarray, k=0.75):
        '''
        对于BB，我们选择前 k% 的bugReport，别的都标记为0
        '''
        portion = ceil(matrix.shape[1] * k) - 1
        for line in matrix:
            line[line.argsort()[:portion]] = 0
        np.save(os.path.join(projects_path, "bb.npy"), matrix)


if __name__ == '__main__':
    bb = BugBugSim()
    # matrix = bb.calculateMatrix()
    matrix = bb.calculateMatrixRefine()
    bb.simplify(matrix, k=0.75)
