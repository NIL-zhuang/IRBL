import os
import sys
import zipfile
from constants import projects_path, problesmfiles, proj

STORAGE_DIR = 'data'


# 代码文件路径一定要存放在src路径下


class FileFilter():
    def __init__(self):
        pass

    def filterFile(self, suffix='.java'):
        for root, dir, files in os.walk(os.path.join(projects_path, "src"), topdown=False):
            for filename in files:
                f = os.path.join(root, filename)
                if filename.startswith('$') or not f.endswith(suffix):
                    os.remove(f)
            if not os.listdir(root):
                os.rmdir(root)
        print("Finish filtering not .java files")


class FileIndex():
    def __init__(self):
        self.srcPath = os.path.join(projects_path, 'src')
        if not os.path.exists(self.srcPath):
            raise FileNotFoundError("Code must be stored in src directory.")
        self.idxPath = os.path.join(projects_path, 'fileIndex.csv')
        self.fileList = []
        self.collectFile()

    def collectFile(self):
        for root, dir, files in os.walk(self.srcPath):
            root = root.replace(self.srcPath, '')
            root = root[1:] if root.startswith('/') else root
            for filename in files:
                f = os.path.join(root, filename)
                self.fileList.append(f)
        self.fileList.sort()

    def storeIdx(self):
        fileList = '\n'.join(list(map(lambda x: ','.join([str(x[0]), x[1]]), enumerate(self.fileList))))
        with open(self.idxPath, 'w+', encoding='utf-8') as f:
            f.write(fileList)
        print("Finish indexing .java files")


class FileUnziper():
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.split(filepath)[1]
        if not zipfile.is_zipfile(self.filepath):
            raise FileNotFoundError("Can't unzip {} because of file type.".format(self.filename))
        self.zipfile = zipfile.ZipFile(filepath, 'r')

    def unzip(self):
        for file in self.zipfile.namelist():
            self.zipfile.extract(file, STORAGE_DIR)
        print("Finish unziping files")
        return os.path.join(STORAGE_DIR, self.filename.split('.')[0])


class AspectJFilter():
    def __init__(self):
        self.problemFiles = []
        with open(problesmfiles, 'r') as f:
            for line in f.readlines():
                line = line.replace("data\\aspectj\\src\\", "")
                line = os.path.join(projects_path, 'src', line)
                self.problemFiles.append(line.rstrip('\n'))

    def filter(self):
        for file in self.problemFiles:
            os.remove(file)
            print(file)


if __name__ == '__main__':
    if proj == 'aspectj':
        AspectJFilter().filter()
    FileFilter().filterFile(suffix='.java')
    FileIndex().storeIdx()
