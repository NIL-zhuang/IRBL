from util import VectorBuilder, BugIdx, FileIdx
from file_reader import FileReader, JSONReader, CsvReader
from constants import report_with_tag, fileIndex, projects_path, codes, methods, bugs
import numpy as np
import os
import re
from math import ceil
from tqdm import tqdm
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from vector_sim import getCosSimMatrix


class BugSourceSim:

    def __init__(self):
        self.vectorBuilder = VectorBuilder()
        self.dct = JSONReader(report_with_tag).readFile()
        self.bugIdx = BugIdx()
        self.fileIdx = FileIdx()

        self.codes = JSONReader(codes).readFile()
        self.bugs = JSONReader(bugs).readFile()
        self.methods = JSONReader(methods).readFile()
        self.allFiles = CsvReader(fileIndex).readFile()

        self.bugCount = len(self.bugIdx.getAllBugId())
        self.fileCount = len(self.fileIdx.getAllFiles())

        self.stackPattern = re.compile('[a-zA-Z][a-zA-Z0-9_\-\.]*.java')

        # 专门处理bug和各component之间的相似度
        component_and_bug_corpus = []
        self.bc_file2idx = defaultdict(list)
        self.bc_bug2idx = defaultdict(list)
        idx = 0
        for f_idx in tqdm(self.codes, desc='loading code corpus'):
            component_and_bug_corpus.append(' '.join(self.codes[f_idx]['ClassORInterfaceName']))
            component_and_bug_corpus.append(' '.join(self.codes[f_idx]['comment']))
            component_and_bug_corpus.append(' '.join(self.codes[f_idx]['variables']))
            component_and_bug_corpus.append(' '.join(self.codes[f_idx]['methods']))
            self.bc_file2idx[f_idx] = idx
            idx += 4
        for b_idx in tqdm(self.bugs, desc='loading bug corpus'):
            component_and_bug_corpus.append(' '.join(self.bugs[b_idx]['summary']))
            component_and_bug_corpus.append(' '.join(self.bugs[b_idx]['description']))
            self.bc_bug2idx[b_idx] = idx
            idx += 2
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(component_and_bug_corpus)
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(X)
        self.bug_and_component_vectors = tfidf.toarray()

        # 专门处理bug和方法间的相似度
        method_and_bug_corpus = []
        self.file_methods = defaultdict(list)
        self.bug2idx = defaultdict(int)
        idx = 0
        for f in self.methods:
            for b in self.methods[f]:
                self.file_methods[f].append(idx)
                idx += 1
                method_and_bug_corpus.append(' '.join(self.methods[f][b]))
        bug_dct = JSONReader(bugs).readFile()
        for bug_id in bug_dct:
            self.bug2idx[bug_id] = idx
            idx += 1
            method_and_bug_corpus.append(' '.join(bug_dct[bug_id]['total']))
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(method_and_bug_corpus)
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(X)
        self.method_and_code_vectors = tfidf.toarray()

    @staticmethod
    def getCosSim(vector1, vector2):
        def getCosRes():
            return vector1 @ vector2 / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        sim = getCosRes()
        if np.isnan(sim):
            return 0
        return sim

    def textSim(self, fileIdx, bugId):
        """
        w3(bi, si)=cos(vi, vj)
        计算code文件和bug报告整体的相似度
        """
        vec1 = np.array(self.vectorBuilder.get_vector(fileIdx, is_reportId=False))
        vec2 = np.array(self.vectorBuilder.get_vector(bugId, is_reportId=True))
        return self.getCosSim(vec1, vec2)

    def componentSim(self, fileIdx, bugId):
        """
        w4(bi, si)=Sigma_{sum, desc}Sigma_{class/unit, method/func/procedureName, variable/constantName, comments}
        """
        code_vector = self.bug_and_component_vectors[self.bc_file2idx[fileIdx]:self.bc_file2idx[fileIdx] + 4]
        bug_vector = self.bug_and_component_vectors[self.bc_bug2idx[bugId]:self.bc_bug2idx[bugId] + 2]
        # step4: 计算总和
        sim = 0
        for code_v in code_vector:
            for bug_v in bug_vector:
                sim += self.getCosSim(code_v, bug_v)
        return sim

    def methodSim(self, fileIdx, bugId):
        """
        w5(bi, si)=max{cos(vi, vjq|q in si)}
        """
        sim = 0
        bug_vec = self.method_and_code_vectors[self.bug2idx[bugId]]
        for method_vec in self.method_and_code_vectors[self.file_methods[fileIdx]]:
            sim = max(sim, self.getCosSim(bug_vec, method_vec))
        return sim

    def stackTraceSim(self, fileIdx, bugId):
        """
        w6 is in below
        1/rank  if sj in bi trace and rank<10
        0.1     if rank >= 10
        0       otherwise
        """

        # step1: 先读取bug的堆栈信息出来
        ST = self.dct[str(bugId)]['ST']

        # step2: 需要切分出其中的java文件
        file_in_stack = self.stackPattern.findall(ST)

        # step3: 需要拿到代码文件的文件名
        filename = self.stackPattern.findall(self.allFiles[int(fileIdx)])[0]

        # step3: 计算文件名在堆栈中出现的位置
        if filename in file_in_stack:
            rank = file_in_stack.index(filename) + 1
            return max(1 / rank, 0.1)
        else:
            return 0

    def calculateSim(self, bugId, SourceIdx):
        """
        Wbs = (w3+w4+w5+w6)/4
        """
        SourceIdx = str(SourceIdx)
        w3 = self.textSim(SourceIdx, bugId)
        w4 = self.componentSim(SourceIdx, bugId)
        w5 = self.methodSim(SourceIdx, bugId)
        w6 = self.stackTraceSim(SourceIdx, bugId)
        return (w3 + w4 + w5 + w6) / 4
        # return (w3 + w5 + w6) / 3

    def calculateMatrix(self):
        bugCount = len(self.bugIdx.getAllBugId())
        fileCount = len(self.fileIdx.getAllFiles())
        matrix = np.zeros([bugCount, fileCount])
        for bugIdx in tqdm(range(bugCount), desc='calculating bug source sim'):
            for srcId in range(fileCount):
                sim = self.calculateSim(self.bugIdx.getBugId(bugIdx), srcId)
                matrix[bugIdx, srcId] = sim
        return matrix

    def calculateMatrixRefine(self):
        '''
        每个矩阵的形状都应该是B*S
        '''
        print("Start generate bs matrix")
        textSimMatrix = self.textSimMatrixRefine()
        print("Finish generate text similarity matrix")
        componentSimMatrix = self.componentSimMatrixRefine()
        print("Finish generate component similarity matrix")
        methodSimMatrix = self.methodSimMatrixRefine()
        print("Finish generate method similarity matrix")
        stackTraceSimMatrix = self.stackTraceSimMatrixRefine()
        print("Finish generate stack trace similarity matrix")
        return (textSimMatrix + componentSimMatrix + methodSimMatrix + stackTraceSimMatrix) / 4

    def textSimMatrixRefine(self):
        '''整体相似度'''
        def initFileVec():
            fileVecList = []
            for srcId in range(self.fileCount):
                srcId = str(srcId)
                srcVec = np.array(self.vectorBuilder.get_vector(srcId, is_reportId=False))
                fileVecList.append(srcVec)
            return fileVecList

        def initBugVec():
            bugVecList = []
            for bugIdx in range(self.bugCount):
                bugId = self.bugIdx.getBugId(bugIdx)
                bugVec = np.array(self.vectorBuilder.get_vector(bugId, is_reportId=True))
                bugVecList.append(bugVec)
            return bugVecList

        fileVectors = initFileVec()
        bugVectors = initBugVec()
        return getCosSimMatrix(bugVectors, fileVectors)

    def componentSimMatrixRefine(self):
        classOrInterfaceNameVecList = []
        commentVecList = []
        variablesVecList = []
        methodsVecList = []

        def initSrcComponentVec():
            for fileIdx in range(self.fileCount):
                fileIdx = str(fileIdx)
                componentStart = self.bc_file2idx[fileIdx]
                codeVectors = self.bug_and_component_vectors[componentStart: componentStart+4]
                classOrInterfaceNameVecList.append(codeVectors[0])
                commentVecList.append(codeVectors[1])
                variablesVecList.append(codeVectors[2])
                methodsVecList.append(codeVectors[3])

        summaryList = []
        descriptionList = []

        def initBugComponentVec():
            for bugIdx in range(self.bugCount):
                bugId = self.bugIdx.getBugId(bugIdx)
                bugStart = self.bc_bug2idx[bugId]
                summaryList.append(self.bug_and_component_vectors[bugStart])
                descriptionList.append(self.bug_and_component_vectors[bugStart+1])

        initSrcComponentVec()
        initBugComponentVec()

        srcVecList = [classOrInterfaceNameVecList, commentVecList, variablesVecList, methodsVecList]
        bugVecList = [summaryList, descriptionList]
        resMatrix = sum([getCosSimMatrix(bugComponent, srcComponent) for srcComponent in srcVecList for bugComponent in bugVecList])
        return resMatrix

    def methodSimMatrixRefine(self):
        methodSimMatrix = np.zeros([self.bugCount, self.fileCount])
        for bugIdx in range(self.bugCount):
            bugId = self.bugIdx.getBugId(bugIdx)
            bugVec = self.method_and_code_vectors[self.bug2idx[bugId]]
            for fileIdx in range(self.fileCount):
                curSim = 0
                for methodVec in self.method_and_code_vectors[self.file_methods[str(fileIdx)]]:
                    curSim = max(curSim, self.getCosSim(bugVec, methodVec))
                methodSimMatrix[bugIdx][fileIdx] = curSim
        return methodSimMatrix

    def stackTraceSimMatrixRefine(self):
        stackTraceSimMatrix = np.zeros([self.bugCount, self.fileCount])
        for bugIdx in range(self.bugCount):
            bugId = self.bugIdx.getBugId(bugIdx)
            ST = self.dct[str(bugId)]['ST']
            fileInStack = self.stackPattern.findall(ST)

            for fileIdx in range(self.fileCount):
                curSim = 0
                filename = self.stackPattern.findall(self.allFiles[fileIdx])[0]
                if filename in fileInStack:
                    rank = fileInStack.index(filename)+1
                    curSim = max(1/rank, 0.1)
                stackTraceSimMatrix[bugIdx][fileIdx] = curSim
        return stackTraceSimMatrix

    def modifyEdge(self, matrix: np.ndarray, k=0.75):
        '''
        the k-th largest value in the i-th row of the matrix
        select top k of the i-th row
        '''
        portion = ceil(matrix.shape[1] * k) - 1
        for line in matrix:
            line[line.argsort()[:portion]] = 0
        np.save(os.path.join(projects_path, "bs.npy"), matrix)


if __name__ == "__main__":
    bs = BugSourceSim()
    matrix = bs.calculateMatrix()
    # matrix = bs.calculateMatrixRefine()
    bs.modifyEdge(matrix)
    # fileIdx = 0
    # bugIdx = 77948
    # print('total similarity:', bs.calculateSim(bugIdx, fileIdx))
