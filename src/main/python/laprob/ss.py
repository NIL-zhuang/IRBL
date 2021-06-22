from file_reader import CsvReader
from file_writer import NpyWriter
from constants import dependency, fileIndex, dependency_matrix
import os
from tqdm import tqdm


class SourceSourceSim:
    def __init__(self):
        self.idxs = {}
        self.n = 0

        self._get_idxs()

        self.dependencies = [[0] * self.n for _ in range(self.n)]
        self._get_dep()

    def _get_idxs(self):
        """
        获取所有file的idx
        :return:
        """
        fileIdxs = CsvReader(fileIndex).readFile()
        for row in fileIdxs:
            row = row.split(',')
            # row[0]表示index，row[1]表示文件相对路径
            self.idxs[row[1]] = int(row[0])
        self.n = len(self.idxs)

    def _get_dep(self):
        """
        给出各个文件对之间的调用度
        :return:
        """
        sumOfCall = [0] * self.n  # 每个文件的调用总数
        if not os.path.exists(dependency):
            raise FileNotFoundError('ss.csv does not exist')
        dependencies = CsvReader(dependency).readFile()
        for i in tqdm(range(1, len(dependencies)), desc='dependency'):
            row = dependencies[i].split(',')
            try:
                fm = self.idxs[row[0]]
                to = self.idxs[row[1]]
                refs = int(row[2])
                sumOfCall[fm] += refs
                self.dependencies[fm][to] = refs
            except KeyError:
                print(i)
        # 把计数除以总调用数
        for i in range(self.n):
            for j in range(self.n):
                if sumOfCall[i] > 0:
                    self.dependencies[i][j] /= sumOfCall[i]

    def output_result(self, fname):
        writer = NpyWriter(fname, self.dependencies)
        writer.writeFile()
        print(fname, 'has been loaded')


if __name__ == '__main__':
    ss = SourceSourceSim()
    ss.output_result(dependency_matrix)
