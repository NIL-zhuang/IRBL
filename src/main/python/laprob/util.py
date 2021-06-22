from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from file_reader import FileReader, XmlReader, JSONReader
from file_writer import JSONWriter
from constants import report_with_tag, bugReport, processed_report, processed_code, code_vectors, \
    report_vectors, word_idx, projects_path
import os
import re
from tqdm import tqdm
from typing import List
import json
import csv


class VectorBuilder:
    """
    使用TF-IDF算法进行权重计算，用one-hot编码将文本向量化
    """

    def __init__(self):
        self.corpus = []  # 语料库

        self.code_vectors = {}  # 转化后文件的词向量字典，使用文件id号作索引
        self.N = 0  # 代码文件个数

        self.report_vectors = {}  # 转化后报告的词向量字典，使用report id作索引
        self.words = []  # 特征词列表
        self.word2idx = {}  # 存储每个特征词的idx
        # try:
        #     self.word2idx = JSONReader(word_idx).readFile()
        # except IOError:
        #     print('初次执行')

        # 下面两个数据结构中，reportId均为str类型
        self.report2id = {}  # 记录所有reportId -> corpus id
        self.ireport2id = {}  # Inverse report2id 记录所有corpus id -> reportId

        if not os.path.exists(word_idx) or not os.path.exists(report_vectors) or not os.path.exists(code_vectors):
            self.process()
        self.word2idx = JSONReader(word_idx).readFile()
        self.reportVec = JSONReader(report_vectors).readFile()
        self.codeVec = JSONReader(code_vectors).readFile()
        print('vector is loaded')

    def _load_corpus(self):
        # 先将所有的code文件载入语料库
        # 语料库的key是str类型，对code file来说，是fileIdx
        # 对report来说，key是reportId
        files = os.listdir(processed_code)
        files.sort()
        for file in files:
            self.corpus.append(
                FileReader(os.path.join(processed_code, file)).readFile())
        cur = len(self.corpus)
        self.N = cur
        print('code num', self.N)
        # 再载入所有的report
        for file in os.listdir(processed_report):
            fid, _ = os.path.splitext(file)
            self.report2id[fid] = cur
            self.ireport2id[cur] = fid
            cur += 1
            self.corpus.append(
                FileReader(os.path.join(processed_report, file)).readFile())

    def _to_vector(self):
        # 将文本中的词语转换为词频矩阵
        vectorizer = CountVectorizer()
        # 计算个词语出现的次数
        X = vectorizer.fit_transform(self.corpus)
        self.words = vectorizer.get_feature_names()

        transformer = TfidfTransformer()
        # 将词频矩阵X统计成TF-IDF值
        tfidf = transformer.fit_transform(X)
        # 查看数据结构 tfidf[i]表示i类文本中的tf-idf权重
        print('finish vectoring (API finished)')
        tfidfArray = tfidf.toarray()
        for i in tqdm(range(self.N),desc='code to array'):
            self.code_vectors[i] = list(tfidfArray[i])

        for i in tqdm(range(self.N, len(self.corpus)), desc='report to array'):
            reportId = self.ireport2id[i]
            self.report_vectors[reportId] = list(tfidfArray[i])

    def _save_vector(self):
        JSONWriter(code_vectors, self.code_vectors).writeFile()
        JSONWriter(report_vectors, self.report_vectors).writeFile()
        for i, word in enumerate(self.words):
            self.word2idx[word] = i
        JSONWriter(word_idx, self.word2idx).writeFile()

    def process(self):
        print("loading corpus")
        self._load_corpus()
        print('word vectorizing')
        self._to_vector()
        print('saving vectors')
        self._save_vector()

    def get_subset(self, id: int, substr: List[str], is_reportId=False):
        """
        is_reportId=False:
        id是代码文件的ID号，substr是代码文件中的某一段内容（函数，注释等）
        is_reportId=True:
        id是report id，需要被转化为corpus id；substr含义不变
        """

        id = str(id)
        if is_reportId:
            vec = self.reportVec[id]
        else:
            vec = self.codeVec[id]
        sub_vec = [0.0] * len(vec)
        for word in substr:
            if word in self.word2idx:
                idx = self.word2idx[word]
                sub_vec[idx] = vec[idx]
        return sub_vec

    def get_vector(self, id: int, is_reportId=False):
        '''
        获取某个文件对应的向量，其中is_reportId=False代表要获取代码文件的向量，is_reportId=True代表要获取bug文件的向量
        '''

        id = str(id)
        if is_reportId:
            return self.reportVec[id]
        else:
            return self.codeVec[id]


class StackExtractor:
    def __init__(self):
        self.flags = re.M | re.I
        self.stackPattern = re.compile(r'( at [^()]+\([\w]+.java:[0-9]*\))+',
                                       self.flags)

    def split(self, content):
        result = {'OT': '', 'ST': ''}
        stackRange = self._get_stack(content)
        if not stackRange:
            result['OT'] = content
            return result
        # OT: other, ST: stack
        result['OT'] = content[:stackRange[0]] + content[stackRange[1]:]
        result['ST'] = content[stackRange[0]:stackRange[1]]
        return result

    def _get_stack(self, content):
        result = self.stackPattern.search(content)
        if result is not None:
            return list(result.span())
        return None

    def tag(self):
        """
        这个函数有职责过重的嫌疑，但是考虑到二阶段代码只是个抛弃式原型，就不做设计上的优化了
        职责1：为所有报告打上NL、ST、SC的标签，并存储为reports_with_tag.json
        职责2：将报告堆栈信息中的项目文件提取出来（如果有），并存储为stack_list.json
        两个职责的数据源都是bugReports
        :return:
        """
        # 读取并解析xml
        tree = XmlReader(bugReport).readFile()
        root = tree.getroot()

        result = {}

        for ele in tqdm(tree.iter(tag='bug'), total=len(root), desc="tagging:"):
            rptId = ele.attrib['id']
            summary = ele[0][0].text
            description = ele[0][1].text
            # description 可能为空，这里使用一下防御式编程，防止字符串和空值相加
            src = ''
            if description:
                src += description
            # 打完标签的结果写入result
            result[rptId] = self.split(src)
            result[rptId]['SM'] = summary

        report_writer = JSONWriter(report_with_tag, result)
        report_writer.writeFile()


class BugIdx():
    def __init__(self):
        self.path = os.path.join(projects_path, "reports_with_tag.json")
        if not os.path.exists(self.path):
            raise Exception("{} hasn't been generated".format(self.path))
        self.bugIdxPath = os.path.join(projects_path, "bugIdx.csv")
        if not os.path.exists(self.bugIdxPath):
            self.initFile()
        csvReader = csv.reader(open(self.bugIdxPath, 'r'))
        self.bugIdxMap = {}
        self.idxBugMap = {}
        for line in csvReader:
            self.bugIdxMap[line[1]] = int(line[0])  # bugId -> bugIndex
            self.idxBugMap[int(line[0])] = line[1]  # bugIndex -> bugId

    def initFile(self):
        print("Init bug-index mappings")
        bugIdx = []
        self.loadDict = json.load(open(self.path, 'r'))
        for idx, (k, v) in enumerate(self.loadDict.items()):
            bugIdx.append([str(idx), k])
        res = [','.join(item) for item in bugIdx]
        with open(self.bugIdxPath, 'w+', encoding='utf-8') as f:
            f.write('\n'.join(res))

    def getBugIdx(self, bugId: str):
        '''
        根据bugId获得对应的index，如 58885 -> 1
        '''
        return self.bugIdxMap[bugId]

    def getBugId(self, bugIdx: int):
        '''根据bugIdx获得对应的id，如 1 -> 58885'''
        return self.idxBugMap[bugIdx]

    def getAllBugId(self):
        return self.bugIdxMap.keys()

    def getBugNum(self):
        return len(self.bugIdxMap.keys())


class FileIdx:
    def __init__(self):
        self.path = os.path.join(projects_path, "fileIndex.csv")
        csvReader = csv.reader(open(self.path, 'r'))
        self.fileIdxMap = {}
        self.idxFileMap = {}
        for line in csvReader:
            self.fileIdxMap[line[1]] = int(line[0])
            self.idxFileMap[int(line[0])] = line[1]

    def file2idx(self, fileName: str):
        '''fileName -> fileIdx, "widgets/Widget.java" -> 484'''
        return self.fileIdxMap[fileName]

    def idx2file(self, idx: int):
        '''fileIdx -> fileName 484 -> "widgets/Widget.java"'''
        return self.idxFileMap[int(idx)]

    def getAllFiles(self):
        return self.fileIdxMap.keys()


class FileIdxForEclipse:
    """
    这个类是针对eclipse bug report中文件名称和项目文件名称命名严重不一致的问题而设计的
    从简化版本的fileIdx中读取idx - fileName
    crx 2021.1.14 11:31:27
    """

    def __init__(self):
        self.path = os.path.join(projects_path, "fileIndex_simplified.csv")
        csvReader = csv.reader(open(self.path, 'r'))
        self.fileIdx = {}
        self.idxFile = {}
        for line in csvReader:
            self.fileIdx[line[1]] = int(line[0])
            self.idxFile[int(line[0])] = line[1]

    def file2idx(self, fileName: str):
        '''fileName -> fileIdx, "widgets/Widget.java" -> 484'''
        return self.fileIdx[fileName]

    def idx2file(self, idx: int):
        '''fileIdx -> fileName 484 -> "widgets/Widget.java"'''
        return self.idxFile[idx]


if __name__ == '__main__':
    # st = StackExtractor()
    # st.tag()
    # vb = VectorBuilder()
    # vb.process()
    # bugidx = BugIdx()
    # print(bugidx.getAllBugId())
    print(str(None))
