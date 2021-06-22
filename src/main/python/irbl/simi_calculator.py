from tqdm import tqdm
import numpy as np
from file_reader import JSONReader
from file_writer import JSONWriter
import xml.etree.ElementTree as et
from constants import bugReport, data_pool_path, doc2vec_path, bug2vec_path, rvsm_score_path, simibugs_score_path, \
    final_score_path, \
    g_dct_path
import collections
import os
import sys
from result_printer import Metric


def get_cos_sim(a, b):
    """
    :param a: 行向量a
    :param b: 行向量b
    :return: a、b相似度，范围0～1之间的浮点数
    """
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot_prod = np.dot(a_arr, b_arr.T)  # 向量点乘
    nom_prod = np.linalg.norm(a) * np.linalg.norm(b)  # 计算向量a、b的二范数乘积
    res = dot_prod / nom_prod
    return round(res, 4)


class RVSMModel:
    def __init__(self):
        self.rvsm_score = collections.defaultdict(dict)
        self.simibugs_score = collections.defaultdict(dict)
        self.final_simi_matrix = collections.defaultdict(dict)  # 存放rVSM+simi bugs的综合结果
        self.reports = []
        self.codefiles = []

    def process(self):
        self.load()
        self.get_rvsm_score()
        self.get_simibugs_score()
        self.get_final_score(alpha=0.2)
        self.save()

    def load(self):

        for file in os.listdir(os.path.join(data_pool_path, 'report')):
            r, _ = os.path.splitext(file)
            self.reports.append(r)

        for file in os.listdir(os.path.join(data_pool_path, 'class')):
            c, _ = os.path.splitext(file)
            self.codefiles.append(c)

        for r in self.reports:
            for c in self.codefiles:
                self.rvsm_score[r][c] = 0.0
                self.simibugs_score[r][c] = 0.0

    def get_final_score(self, alpha=0.2):
        # 这里默认取α为0.2，因为我们复现的论文中是这么做的
        # 会根据实际执行效果调整alpha值
        for r in self.reports:
            for c in self.codefiles:
                self.final_simi_matrix[r][c] = (1 - alpha) * self.rvsm_score[r][c] + alpha * self.simibugs_score[r][c]

    def get_rvsm_score(self):
        """
        计算bug和code之间的相似度矩阵
        :return:
        """
        doc2vec = JSONReader(doc2vec_path).readFile()
        g_dct = JSONReader(g_dct_path).readFile()

        report2vec, code2vec = {}, {}

        for r in self.reports:
            report2vec[r] = doc2vec[r]
        for c in self.codefiles:
            code2vec[c] = doc2vec[c]

        for r in tqdm(report2vec, desc='Calculating rVSM scores...'):
            for c in code2vec:
                self.rvsm_score[r][c] = get_cos_sim(report2vec[r], code2vec[c]) * g_dct[c]

    def get_simibugs_score(self):
        """
        根据报告和历史报告的相似度为代码文件加分
        """
        tree = et.ElementTree(file=bugReport)

        def ref_histories(rpt):
            """
            :param rpt: 源report, 每次都要计算相似的历史报告，可以考虑把计算报告相似度的中间结果持久化，但是二阶段先不做了
            :return:
            """
            bug2vec = JSONReader(bug2vec_path).readFile()
            reportId = rpt.attrib['id']
            self.simibugs_score[reportId] = collections.defaultdict(float)
            # 获取报告的日期，这是为了找到其历史报告
            src_date = rpt.attrib['fixdate']
            for bug in tree.iter('bug'):
                targetId = bug.attrib['id']
                if targetId == reportId: continue
                dest_date = bug.attrib['fixdate']
                if dest_date >= src_date: continue
                # 计算当前报告和目标报告的相似度
                sim = get_cos_sim(bug2vec[reportId], bug2vec[targetId])
                # 对报告涉及修复文件挨个加分
                files = bug.find('fixedFiles').findall('file')
                n = len(files)
                for file in files:
                    name = file.text.split('.')[-2]  # 代码文件名称（不含.java）
                    self.simibugs_score[reportId][name] += sim / n

        for report in tqdm(tree.findall('bug'), desc='Calculating simibugs scores...'):
            ref_histories(report)

    def eval_alpha(self):
        """
        本方法用来测试alpha调参效果
        :return:
        """
        m = Metric()
        self.load()
        self.get_rvsm_score()
        self.get_simibugs_score()
        alpha = 0.0
        f = open('alpha_log.txt', 'w+')
        out = sys.stdout
        sys.stdout = f
        while alpha <= 1:
            print('alpha =', alpha)
            self.get_final_score(alpha)
            m.simi_matrix = self.final_simi_matrix
            m.print_metrics(printInfo=False)
            print()
            alpha += 0.05
        sys.stdout = out
        f.close()

    def save(self):
        """
        将计算结果持久化
        :return:
        """
        JSONWriter(rvsm_score_path, self.rvsm_score).writeFile()
        JSONWriter(simibugs_score_path, self.simibugs_score).writeFile()
        JSONWriter(final_score_path, self.final_simi_matrix).writeFile()


if __name__ == '__main__':
    model = RVSMModel()
    model.process()
