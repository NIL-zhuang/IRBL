from tqdm import tqdm
from PreProcessor.lemma import Lemma, CommentFilter
from typing import List, Tuple
import os
from file_writer import FileWriter
import json


class CodePreprocess:
    def __init__(self, var_list: List[str], comment_list: List[str]):
        """
        var_list: the variables, extendOrImplementFiles, classOrInterfaceName json file list
        comment_list: the comments of files
        """
        self.lemmanizer = Lemma()
        self.cmtFilter = CommentFilter()
        self.code_comment_pair = list(zip(var_list, comment_list))

    @staticmethod
    def get_all_file(path: str, suffix: str) -> List[str]:
        path_list = []
        for filepath in os.listdir(path):
            com_path = os.path.join(path, filepath)
            if os.path.isfile(com_path) and com_path.endswith(suffix):
                path_list.append(com_path)
            elif os.path.isdir(com_path):
                path_list.extend(CodePreprocess.get_all_file(com_path, suffix))
        return sorted(path_list)

    def preprocess(self):
        for pair in tqdm(self.code_comment_pair, desc="preprocess codes"):
            code = self.codePreprocess(pair[0])
            comment = self.commentPreprocess(pair[1])
            lemma_code = [w for word in code for w in self.lemmanizer.lemmatizeWord(word)]
            lemma_comment = [word for cmt in comment for word in self.lemmanizer.lemmatizeStr(cmt)]
            fileName = pair[0].split(os.sep)[-1].split('.')[0]
            FileWriter(os.sep.join(['class', fileName + ".txt"]), '\n'.join(lemma_comment + lemma_code)).writeFile()

    def codePreprocess(self, codePath: str) -> List[str]:
        with open(codePath, 'r') as f:
            json_file = json.load(f)
        vars = json_file['variables'] + json_file['methods'] + json_file['extendORImplementFiles']
        n = len(vars) // 10  # 取总长度的10%
        vars += json_file['ClassORInterfaceName'] * n
        return vars

    def commentPreprocess(self, commentPath: str) -> List[str]:
        # 要删掉 /xxx， * , @xxx， <xx>这些符号
        with open(commentPath, 'r') as f:
            comments = [self.cmtFilter.filterComment(line[:-1]) for line in f.readlines()]
        return comments


if __name__ == '__main__':
    codeList = CodePreprocess.get_all_file(os.sep.join(['data', 'swt_json']), '.json')
    commentList = CodePreprocess.get_all_file(os.sep.join(['data', 'swt_comment']), '.txt')
    codeP = CodePreprocess(codeList, commentList)
    # codeP = CodePreprocess(["data/swt_json/ACC.json"], ["data/swt_comment/ACC.txt"])
    codeP.preprocess()
