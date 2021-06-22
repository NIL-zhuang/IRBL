from constants import projects_path
from mapper import MapperGenerator
from fileFilter import FileIndex, FileFilter
from util import FileIdx
import os
import json


class CleanUnfixedFiles():
    def __init__(self):
        self.generateFiles()
        self.fileIdx = FileIdx()
        self.buggyFiles = self.getAllBuggyFiles()

    def generateFiles(self):
        FileFilter().filterFile()
        FileIndex().storeIdx()
        MapperGenerator().generate()

    def cleanFiles(self):
        srcPath = os.path.join(projects_path, 'src')
        for file in self.buggyFiles:
            file = os.path.join(srcPath, file)
            os.remove(file)

    def getAllBuggyFiles(self):
        files = set()
        mapper = json.load(open(os.path.join(projects_path, 'bug_src_map.json'), 'r'))
        for k, v in mapper.items():
            for item in v:
                files.add(self.fileIdx.idx2file(item))
        return files

    def cleanMiddleFiles(self):
        cleanFile = ['bug_src_map.json', 'fileIndex.csv']
        for file in cleanFile:
            os.remove(os.path.join(projects_path, file))

    def cheat(self):
        self.cleanFiles()
        self.cleanMiddleFiles()
        self.generateFiles()


if __name__ == '__main__':
    CleanUnfixedFiles().cheat()
