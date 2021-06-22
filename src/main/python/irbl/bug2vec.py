"""
更加简洁的WeightDefiner版本
用于实现bug report转vec
2021.4.14 crx
"""

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from file_reader import FileReader
from file_writer import JSONWriter
from constants import data_pool_path
import os


class VectorBuilder:
    def __init__(self, report_path, save_path):
        self.corpus = []  # 语料库
        self.file2idx = {}  # 保存file在corpus中的位置
        self.report_path = report_path
        self.save_path = save_path
        self.vectors = {}

    def load_corpus(self):
        # 将所有的report文件读入语料库
        for idx, file in enumerate(os.listdir(os.path.join(data_pool_path, self.report_path))):
            fn, _ = os.path.splitext(file)
            self.file2idx[fn] = idx
            self.corpus.append(
                FileReader(os.path.join(self.report_path, file)).readFile())

    def vectorize(self):
        # 将文本中的词语转换为词频矩阵
        vectorizer = CountVectorizer()
        # 计算个词语出现的次数
        X = vectorizer.fit_transform(self.corpus)
        transformer = TfidfTransformer()
        # 将词频矩阵X统计成TF-IDF值
        tfidf = transformer.fit_transform(X)
        # 查看数据结构 tfidf[i]表示i类文本中的tf-idf权重
        for file in self.file2idx:
            idx = self.file2idx[file]
            self.vectors[file] = list(tfidf.toarray()[idx])

    def save_vector(self):
        JSONWriter(self.save_path, self.vectors).writeFile()

    def process(self):
        self.load_corpus()
        self.vectorize()
        self.save_vector()


if __name__ == '__main__':
    wd = VectorBuilder('report', 'bug2vec.json')
    wd.process()
