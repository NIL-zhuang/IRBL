from tqdm import tqdm
from collections import defaultdict
from numpy import mean
import os
import shutil
import time
from preprocess import CodePreprocess, BugPreprocessor, MethodExtractor
from bb import BugBugSim
from bs import BugSourceSim
from ss import SourceSourceSim
from constants import dependency_matrix, projects_path, alpha, beta, final_score_path, cheat_score_path, proj
from calculate import Calculate, markRate
from edgeCombine import EdgeCombination
from calculate import Calculate
from metric import Metric


def printRunTime(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        func(*args, **kw)
        print('current Function [%s] run time is %.2f seconds' % (func.__name__, time.time() - local_time))
    return wrapper


def cleanFiles():
    preprocessDirs = ['bugComponent', 'bugs', 'srcComponent', 'words']
    preprocessFiles = ['bugs.json', 'codes.json', 'methods.json', 'final_score.json',
                       'code2vec.json', 'report2vec.json', 'word_idx.json',
                       'bb.npy', 'bs.npy', 'BHG.npy', 'F.npy']
    for dir in preprocessDirs:
        dir = os.path.join(projects_path, dir)
        if os.path.exists(dir):
            shutil.rmtree(dir)
    for file in preprocessFiles:
        file = os.path.join(projects_path, file)
        if os.path.exists(file):
            os.remove(file)
    print('Finish removing files')


def preprocessAll():
    '''
    从AST树抽取文件内提取components, methods, bugs and summary
    '''
    CodePreprocess().getFiles()
    BugPreprocessor().bugPreprocess()
    MethodExtractor().methodExtract()


# @printRunTime
def bbSim(portionK=0.75):
    '''处理bug bug相似度矩阵'''
    bb = BugBugSim()
    # matrix = bb.calculateMatrix()
    matrix = bb.calculateMatrixRefine()
    bb.simplify(matrix, k=portionK)
    print("Finish generate bb matrix")


# @printRunTime
def bsSim(portionK=0.75):
    '''bug source相似度'''
    bs = BugSourceSim()
    # matrix = bs.calculateMatrix()
    matrix = bs.calculateMatrixRefine()
    bs.modifyEdge(matrix, k=portionK)
    print("Finish generate bs matrix")


# @printRunTime
def ssSim():
    '''source source相似度'''
    ss = SourceSourceSim()
    ss.output_result(dependency_matrix)
    print("Finish generate ss matrix")


def edgeCombination(alphaCal, betaCal):
    '''构造BHG矩阵'''
    edges = EdgeCombination()
    edges.normalize()
    edges.BHG(a=alphaCal, b=betaCal)
    print("Finish combine BHG matrix")


def calculate(markRate=0.05, iterations=1000):
    '''进行标签传播和计算'''
    cal = Calculate(markLabelRate=markRate, quiet=True)
    cal.optimization(iter=iterations)
    cal.saveRes()
    cal.saveCheatRes()


def evaluate(resPath):
    '''评估'''
    metric = Metric(resPath)
    res = metric.getRes()
    return res


def fullEvaluate(iterTimes):
    '''多次采样取平均'''
    res = defaultdict(list)
    cheatRes = defaultdict(list)
    for i in tqdm(range(iterTimes), desc='full iterations'):
        calculate()
        for k, v in evaluate(final_score_path).items():
            res[k].append(v)
        for k, v in evaluate(cheat_score_path).items():
            cheatRes[k].append(v)
    print("\n==============={}=================".format(proj))
    for k, v in res.items():
        print("mean", k, round(float(mean(v)), 4))

    print("\n============max {}================".format(proj))

    for k, v in res.items():
        print("max", k, round(float(max(v)), 4))

    print("\n===============cheat {}============".format(proj))
    for k, v in cheatRes.items():
        print("mean", k, round(float(mean(v)), 4))

    print("\n============max {}=================".format(proj))
    for k, v in cheatRes.items():
        print("max", k, round(float(max(v)), 4))


if __name__ == "__main__":
    # preprocessAll()
    bbSim()
    bsSim()
    ssSim()
    edgeCombination(alpha, beta)
    fullEvaluate(10)
