import json
import os
import numpy as np
from constants import data_pool_path, projects_path
import xml.etree.ElementTree as et


class FileReader:
    def __init__(self, n):
        self.fname = n

    def readFile(self):
        out = ''
        try:
            with open(self.fname, 'r') as f:
                out = f.read()
        except IOError:
            print('打开文件{}失败！'.format(self.fname))
        return out


class JSONReader(FileReader):
    def readFile(self):
        out = {}
        if self.fname.split('.')[1] == 'json':
            try:
                with open(self.fname, 'r') as f:
                    out = json.load(f)
            except IOError:
                print('打开文件{}失败！'.format(self.fname))
        return out


class NpyReader(FileReader):
    def readFile(self):
        out = None
        if self.fname.split('.')[1] == 'npy':
            try:
                out = np.load(self.fname)
            except IOError:
                print('文件打开失败！')
        return out


class XmlReader(FileReader):
    def readFile(self):
        out = None
        if self.fname.split('.')[1] == 'xml':
            try:
                out = et.ElementTree(file=self.fname)
            except IOError:
                print('文件{}打开失败！'.format(self.fname))
        return out


class CsvReader(FileReader):
    def readFile(self):
        out = ''
        try:
            with open(self.fname, 'r') as f:
                out = f.read().strip()
        except IOError:
            print('打开{}文件失败！'.format(self.fname))
        return out.split('\n')


class CodeIdx():
    def __init__(self):
        path = os.path.join(projects_path, "fileIndex.csv")
        if not os.path.exists(path):
            raise FileNotFoundError("{} does not exist".format(path))
        self.codeIdx = {}
        f = open(path, 'r', encoding='utf-8')
        for line in f.readlines():
            line = line.rstrip('\n').split(',')
            self.codeIdx[int(line[0])] = line[1]

    def getCodePath(self, idx):
        return self.codeIdx[idx]
