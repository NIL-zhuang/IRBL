import json
import os
import numpy as np
from constants import data_pool_path


class FileWriter:
    def __init__(self, filename, content):
        self.fname = filename
        self.content = content

    def writeFile(self):
        try:
            with open(self.fname, 'w+') as f:
                f.write(self.content)
        except IOError:
            print('打开文件失败！')


class JSONWriter(FileWriter):
    def writeFile(self):
        if self.fname.split('.')[1] == 'json':
            try:
                with open(self.fname, 'w+') as f:
                    json.dump(self.content, f)
            except IOError:
                print('打开文件失败！')


class NpyWriter(FileWriter):
    def writeFile(self):
        if self.fname.split('.')[1] == 'npy':
            try:
                np.save(self.fname, self.content)
            except IOError:
                print('打开文件失败！')


