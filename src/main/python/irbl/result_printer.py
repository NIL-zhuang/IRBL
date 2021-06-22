from file_reader import *
from constants import bugReport, final_score_path
import xml.etree.ElementTree as et
import sys


def print_top_K(report_topK):
    for report in report_topK:
        print('==================================================')
        print(report + ':')
        for name in report_topK[report]:
            print(name)


class Metric:
    def __init__(self):
        tree = et.ElementTree(file=bugReport)
        self.ground_truth = {}
        for ele in tree.iter(tag='bug'):
            idx = ele.attrib['id']
            self.ground_truth[idx] = []
            files = ele.find('fixedFiles')
            for file in files.iter('file'):
                self.ground_truth[idx].append(file.text.split('.')[-2])
        self.simi_matrix = JSONReader(final_score_path).readFile()
        self.n = len(self.ground_truth)
        self.report_topK = {}

    def get_top_K(self, k):
        result = {}
        for report in self.simi_matrix:
            simis = self.simi_matrix[report]
            # 计算总得分
            # 对bug报告对应的class相似度向量进行排序
            simi_pairs = list(simis.items())
            simi_pairs.sort(key=lambda x: -x[1])
            top_k = []
            for i in range(k):
                top_k.append(simi_pairs[i][0])
            result[report] = top_k
        return result

    def getTopKRecall(self, k):
        self.report_topK = self.get_top_K(k)
        hits = 0
        for report in self.ground_truth:
            hit = False
            for f in self.report_topK[report]:
                # 只要命中了ground_truth中的一个就算命中，而不是完整命中，否则top1无法计算涉及多个fixFile的情况
                if f in self.ground_truth[report]:
                    hit = True
                    break
            if hit: hits += 1
        return hits / self.n

    def getMRR(self):
        """
        MRR=1/n ∑_(j=1)^n 1/〖rank〗_j
        〖rank〗_j表示第j个缺陷报告所对应的列表中第一个与缺陷报告相关的源码的排名。
        :return:
        """
        r_sum = 0
        for report in self.simi_matrix:
            codefiles = sorted(list(self.simi_matrix[report].items()), key=lambda x: -x[1])
            rank = 0
            for idx, pair in enumerate(codefiles):
                if pair[0] in self.ground_truth[report]:
                    rank = idx + 1
                    break
            r_sum += 1 / rank
        return r_sum / self.n

    def getMAP(self):
        """
        MAP
        对第j个缺陷报告有一个推荐列表l；
        Prec@k表示l的前k个文件中与缺陷报告相关的源码文件的比例；
        IsRelevant(k)为1表示列表l中第k个源码文件与缺陷报告相关，否则无关；
        K_j表示列表l中所有与缺陷报告相关的源码文件位置集合

        MAP=1/n ∑_(j=1)^n〖AvgP〗_j
        AvgP_j=1/(|K_j |) ∑_(k∈K_j)〖{Prec@k}〗
        Prec(k)=(∑_(i=1)^k〖IsRelevant(k)〗)/k

        :return:
        """

        def find(src, name):
            for i, pair in enumerate(src):
                if pair[0] == name:
                    return i
            return -1

        aps = 0.0  # 所有的avg@prec之和
        for report in self.ground_truth:
            # 对每一个report，计算ap值
            # print("report{}:".format(report))
            simi_pairs = sorted(list(self.simi_matrix[report].items()), key=lambda x: -x[1])

            pos = {}  # 修复bug涉及文件在推荐列表中的位置集合
            for file in self.ground_truth[report]:
                pos[file] = find(simi_pairs, file)

            pos = sorted(list(pos.items()), key=lambda x: x[1])  # 按照出现的顺序排序
            n = len(pos)
            ps = 0.0
            for i, (name, r) in enumerate(pos):
                ps += (i + 1) / (r + 1)
            ap = ps / n  # 该report的平均准确率
            aps += ap
        return aps / self.n

    def print_metrics(self, printInfo=True):
        k = int(sys.argv[1])
        # k = 5  # debug用
        tops = {1: 0, 5: 0, 10: 0, k: round(self.getTopKRecall(k), 4)}
        if printInfo:
            print_top_K(self.report_topK)
        print('==========', 'Metrics', '==========')
        # 计算并打印所有的topk指标
        for key in tops:
            tops[key] = round(self.getTopKRecall(key), 4)
            print('Top@{}: {:.2f}%'.format(key, tops[key] * 100))
        # 计算MRR和MAP
        print('MRR: {:.4f}'.format(self.getMRR()))
        print('MAP: {:.4f}'.format(self.getMAP()))


if __name__ == '__main__':
    # 构造Metric对象，计算指标
    m = Metric()
    m.print_metrics()
