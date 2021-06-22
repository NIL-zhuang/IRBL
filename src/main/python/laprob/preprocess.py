from lemma import Lemma, CommentFilter
from typing import List
import os
import json
from tqdm import tqdm
from constants import projects_path
from util import StackExtractor
from collections import defaultdict


class CodePreprocess():
    '''
    获取文档为一个多重json
    json->srcIdx-> total
                -> variables
                -> comment
                -> methods
                -> ClassORInterfaceName
    '''

    def __init__(self):
        # 总体项目路径
        self.srcPath = os.path.join(projects_path, "json")
        self.targetPath = os.path.join(projects_path, "codes.json")
        self.codeDict = defaultdict(lambda: defaultdict(list))

        self.commentPath = os.path.join(projects_path, "comment")
        self.totalPath = os.path.join(projects_path, "words")
        self.componentPath = os.path.join(projects_path, "srcComponent")
        if not os.path.exists(self.totalPath):
            os.makedirs(self.totalPath)
        if not os.path.exists(self.componentPath):
            os.makedirs(self.componentPath)

        # 当前项目路径
        self.curFileIdx = -1
        self.curComponentPath = ""
        self.curCommentPath = ""
        self.curLoadDict = None
        # 其他工具类
        self.lemma = Lemma()
        self.commentFilter = CommentFilter()

    def getFiles(self):
        for file in tqdm(os.listdir(self.srcPath), desc="code preprocess"):
            fileIdx = file.split('.')[0]
            self.curFileIdx = int(fileIdx)
            # comment的路径和 对应 component 文件夹的地址
            self.curCommentPath = os.path.join(self.commentPath, fileIdx+".txt")
            self.curComponentPath = os.path.join(self.componentPath, fileIdx)
            if not os.path.exists(self.curComponentPath):
                os.makedirs(self.curComponentPath)

            srcPath = os.path.join(self.srcPath, file)
            allDest = os.path.join(self.totalPath, fileIdx + ".txt")
            self.curLoadDict = json.load(open(srcPath, 'r'))

            srcWords = self.getVariables(srcPath)
            commentWords = self.getComment()
            self.codeDict[self.curFileIdx]['total'] = srcWords+commentWords

            with open(allDest, 'w+', encoding='utf-8') as f:
                f.write('\n'.join(srcWords+commentWords))

        with open(self.targetPath, 'w+', encoding='utf-8')as f:
            f.write(json.dumps(self.codeDict, indent=2))

    def getComment(self) -> List[str]:
        '''
        处理代码注释
        '''
        f = open(self.curCommentPath, 'r')
        res = []
        for line in f.readlines():
            line = line.strip('\n')
            cmt = self.commentFilter.filterComment(line)
            res += self.lemma.lemmatizeStr(cmt)

        self.codeDict[self.curFileIdx]['comment'] = res
        commentComponentPath = os.path.join(self.curComponentPath, 'comment.txt')
        with open(commentComponentPath, 'w+', encoding='utf-8') as f:
            f.write('\n'.join(res))
        return res

    def getVariables(self, filePath) -> List[str]:
        '''
        处理代码变量
        '''
        variables = self.extractComponent('variables')
        methods = self.extractComponent('methods')
        classORInterface = self.extractComponent('ClassORInterfaceName')
        # imports = self.loadDict['import']
        # package = self.loadDict['package']
        return variables + methods + classORInterface

    def extractComponent(self, type: str):
        var = sum([self.lemma.lemmatizeWord(word) for word in self.curLoadDict[type]], [])
        self.codeDict[self.curFileIdx][type] = var
        path = os.path.join(self.curComponentPath, type+'.txt')
        with open(path, 'w+', encoding='utf-8') as f:
            f.write('\n'.join(var))
        return var


class BugPreprocessor():
    def __init__(self):
        self.bugReportPath = os.path.join(projects_path, "bugReport.xml")
        self.taggedReport = os.path.join(projects_path, "reports_with_tag.json")
        self.target = os.path.join(projects_path, "bugs.json")
        self.bugDict = defaultdict(lambda: defaultdict(list))
        if not os.path.exists(self.taggedReport):
            st = StackExtractor()
            st.tag()

        self.destPath = os.path.join(projects_path, "bugs")
        self.componentPath = os.path.join(projects_path, "bugComponent")
        if not os.path.exists(self.destPath):
            os.makedirs(self.destPath)
        if not os.path.exists(self.componentPath):
            os.makedirs(self.componentPath)

        self.lemma = Lemma()
        self.commentFilter = CommentFilter()
        self.loadDict = json.load(open(self.taggedReport, 'r'))

    def bugPreprocess(self):
        for bugId, v in tqdm(self.loadDict.items(), desc="bug preprocess"):
            summary = self.lemma.lemmatizeStr(self.commentFilter.filterComment(v['SM']))
            other = self.lemma.lemmatizeStr(self.commentFilter.filterComment(v['OT']))
            self.bugDict[bugId]['summary'] = summary
            self.bugDict[bugId]['description'] = other
            self.bugDict[bugId]['total'] = summary+other

            destDir = os.path.join(self.componentPath, bugId)
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            with open(os.path.join(destDir, 'summary.txt'), 'w+', encoding='utf-8') as f:
                f.write('\n'.join(summary))
            with open(os.path.join(destDir, "description.txt"), 'w+', encoding='utf-8')as f:
                f.write('\n'.join(other))
            with open(os.path.join(self.destPath, "{}.txt".format(bugId)), 'w+') as f:
                f.write('\n'.join(summary + other))

        with open(self.target, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(self.bugDict, indent=2))


class MethodExtractor():
    def __init__(self):
        self.methodPath = os.path.join(projects_path, 'json')
        self.destPath = os.path.join(projects_path, 'methods')
        self.targetPath = os.path.join(projects_path, "methods.json")
        self.methodDict = defaultdict(lambda: defaultdict(list))

        self.curFileIdx = -1
        if not os.path.exists(self.methodPath):
            os.makedirs(self.destPath)
        self.lemma = Lemma()
        self.commentFilter = CommentFilter()

    def methodExtract(self):
        for file in tqdm(os.listdir(self.methodPath), desc="method extract"):
            fileIdx = file.split('.')[0]
            self.curFileIdx = int(fileIdx)
            srcPath = os.path.join(self.methodPath, file)
            loadDict = json.load(open(srcPath, 'r'))['methodsBody']
            fileDest = os.path.join(self.destPath, fileIdx)
            if not os.path.exists(fileDest):
                os.makedirs(fileDest)
            self.methodHandler(loadDict, fileDest)
        with open(self.targetPath, 'w+', encoding='utf-8')as f:
            f.write(json.dumps(self.methodDict, indent=2))

    def methodHandler(self, loadDict, fileDest):
        for idx, (k, v) in enumerate(loadDict.items()):
            destPath = os.path.join(fileDest, "{}.txt".format(idx))
            methodBody = v['methodBody']
            comments = v['comments']
            methodName = v['methodName']
            comments = self.commentFilter.filterComment(comments)
            words = self.lemma.lemmatizeStr(methodName+methodBody+comments)

            self.methodDict[self.curFileIdx][idx] = words
            with open(destPath, 'w+', encoding='utf-8') as f:
                f.write('\n'.join(words))


if __name__ == "__main__":
    cPreprocess = CodePreprocess()
    cPreprocess.getFiles()
    bPreprocess = BugPreprocessor()
    bPreprocess.bugPreprocess()
    methodExtractor = MethodExtractor()
    methodExtractor.methodExtract()
