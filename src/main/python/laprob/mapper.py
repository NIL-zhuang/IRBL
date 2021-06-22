from constants import projects_path, bug_src_map, bugReport, fileIndex
from file_reader import XmlReader, CsvReader
from file_writer import JSONWriter
from collections import defaultdict
import json
import os
import pygtrie


class MapperGenerator():
    '''
    生成一个bugId -> [FileIdxList]的映射
    转存为bug_src_map.json
    '''

    def __init__(self):
        self.bugReport = None

    def generate(self):
        tree = XmlReader(bugReport).readFile()
        root = tree.getroot()

        # 记录bug->fixedFileList
        bug_files = defaultdict(list)
        for bug in root:
            # 获取该bug的id
            bugId = bug.get('id', default=-1)
            # 获取其对应的文件名
            fixedFiles = bug.find('fixedFiles')
            for files in fixedFiles.findall('file'):
                fname = files.text
                fname = fname.replace('/', '.')
                bug_files[bugId].append(fname)

        # 记录file->fileId
        file2idx = defaultdict(int)
        for lst in CsvReader(fileIndex).readFile():
            id = lst.split(',')[0]
            name = lst.split(',')[1].replace('/', '.')
            file2idx[name] = id

        # 逆向构建字典树
        t = pygtrie.StringTrie(separator='.')
        for file in file2idx:
            lst = file[::-1].split('.')
            reversed_filename = ''
            for i in range(len(lst)):
                reversed_filename += lst[i]
                t[reversed_filename] = file
                reversed_filename += '.'

        # 查询每一个bug的file对应的是项目中的哪个文件，并找出其fileId
        bug2fileId = defaultdict(list)
        for bugId in bug_files:
            for filename in bug_files[bugId]:
                file_found = t.longest_prefix(filename[::-1]).value
                bug2fileId[bugId].append(file2idx[file_found])
        with open(bug_src_map, 'w+', encoding='utf-8')as f:
            f.write(json.dumps(bug2fileId, indent=2))
        # JSONWriter(bug_src_map, bug2fileId).writeFile()


class BugSrcMapper():
    def __init__(self):
        if not os.path.exists(bug_src_map):
            MapperGenerator().generate()
        self.mapper = json.load(open(bug_src_map, 'r'))

    def getBugFile(self, bugId):
        '''bugId -> fixedFileList'''
        return self.mapper[bugId]


if __name__ == '__main__':
    mapGenerator = MapperGenerator()
    mapGenerator.generate()
    # bugId = '84906'
    # bugSrcMapper = BugSrcMapper()
    # print(bugSrcMapper.getBugFile(bugId))
