from file_reader import XmlReader, JSONReader
from constants import bugReport, final_score_path, proj
from util import FileIdx, FileIdxForEclipse
from mapper import BugSrcMapper
import sys
from collections import defaultdict


class Metric:
    def __init__(self, resPath):
        # fileidx 和 filename之间的转换
        self.trans = FileIdx()
        # eclipse的名称冲突严重，需要使用特别的FileIdx类 -- crx
        if proj == 'eclipse':
            self.trans = FileIdxForEclipse()

        # 读取推荐矩阵, 推荐矩阵必须使用reportId作key, 每个key对应的value仍然是一个字典
        # 内层字典的key是file id号，value是推荐权值
        # reportId -> {fileId:value}
        self.simi_matrix = JSONReader(resPath).readFile()

        # 从xml中提取ground truth
        self.mapper = BugSrcMapper()
        self.ground_truth = self._get_ground_truth()

        self.n = len(self.ground_truth)
        self.report_topK = {}

    def _get_ground_truth(self):
        """
        获取ground truth, 即每个bug对应的fixed files
        ground_truth = {}
        key = report Id
        value是由修复文件对应的id组成的数据 e.g. [1,2,3...]
        """

        groundTruth = defaultdict(list)
        bugIds = self.simi_matrix.keys()
        for bugId in bugIds:
            groundTruth[bugId] = self.mapper.getBugFile(bugId)
        return groundTruth

        # def preprocess_name(fn):
        #     """
        #     因为各个项目bugReport里的fixedFile格式参差不齐，
        #     所以单独实现一个函数用来转化
        #     """
        #     result = ''
        #     if proj == 'swt':
        #         result = fn.replace('org.eclipse.swt.', '').replace('.', '/')
        #     elif proj == 'eclipse':
        #         result = fn.replace('.', '/')
        #     elif proj == 'aspectj':
        #         result = fn.replace('org.aspectj/modules/', '')
        #     return result

        # tree = XmlReader(bugReport).readFile()
        # for ele in tree.iter(tag='bug'):
        #     idx = ele.attrib['id']
        #     self.ground_truth[idx] = []
        #     files = ele.find('fixedFiles')

        #     # 将每个fixed file转化为file id存入ground truth列表
        #     for file in files.iter('file'):
        #         # 首先对fixed file名称进行规范化，方便使用FileIdx进行转换
        #         file = preprocess_name(file)
        #         self.ground_truth[idx].append(
        #             self.trans.fileIdx(file))

    def _get_file_name(self, idx):
        fname = self.trans.idx2file(idx)
        return fname

    def print_top_K(self):
        for report in self.report_topK:
            print('==================================================')
            print(report + ':')
            for id in self.report_topK[report]:
                print(id, self._get_file_name(id))

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
            if hit:
                hits += 1
        return hits / self.n

    def getMRR(self):
        """
        MRR=1/n ∑_(j=1)^n 1/[rank]_j
        [rank]_j表示第j个缺陷报告所对应的列表中第一个与缺陷报告相关的源码的排名。
        :return:
        """
        r_sum = 0
        for report in self.simi_matrix:
            codes = sorted(list(self.simi_matrix[report].items()), key=lambda x: -x[1])
            rank = 0
            for idx, pair in enumerate(codes):
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

        MAP=1/n ∑_(j=1)^n[AvgP]_j
        AvgP_j=1/(|K_j |) ∑_(k∈K_j)[{Prec@k}]
        Prec(k)=(∑_(i=1)^k[IsRelevant(k)])/k

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

    def print_metrics(self, printInfo=False):
        # k = int(sys.argv[1])
        k = 0  # debug用
        tops = {1: 0, 5: 0, 10: 0, k: round(self.getTopKRecall(k), 4)}
        if printInfo:
            self.print_top_K()
        print('==========', 'Metrics', '==========')
        # 计算并打印所有的topk指标
        for key in tops:
            tops[key] = round(self.getTopKRecall(key), 4)
            print('Top@{}: {:.2f}%'.format(key, tops[key] * 100))
        # 计算MRR和MAP
        print('MRR: {:.4f}'.format(self.getMRR()))
        print('MAP: {:.4f}'.format(self.getMAP()))

    def getRes(self):
        tops = [1, 5, 10]
        res = dict()
        for key in tops:
            res['Top@{}'.format(key)] = round(self.getTopKRecall(key), 4)
        res['MRR'] = round(self.getMRR(), 4)
        res['MAP'] = round(self.getMAP(), 4)
        return res


if __name__ == '__main__':
    # 构造Metric对象，计算指标
    m = Metric(final_score_path)
    m.print_metrics()
