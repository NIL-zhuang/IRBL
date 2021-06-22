# IRBL

NJUSE Software Engineering & Computing III Project

本项目的代码结构如下，每个项目及其对应中间文件都被存放在统一的目录名下

```txt
.
├── data
│   ├── aspectj
│   ├── eclipse
│   └── swt
├── develop_rule.md
├── Jenkinsfile
├── LICENSE
├── pom.xml
├── README.md
└── src
```

对应项目文件下的各文件/文件夹如下

|         file         | description           |
| :------------------: | :-------------------- |
|         json         | 代码文件AST树提取内容 |
|         src          | 代码源文件            |
|         xml          | AST树提取的文件       |
|    bugReport.xml     | bugReport             |
|    fileIndex.csv     | 文件对应的idx         |
| report_with_tag.json | 代码报告及切分的堆栈  |

## 程序处理流程

1. 将要处理的代码文件放在proj/src路径下，bugReport.xml放在proj路径下
2. 清洗文件，删除所有非.java文件，执行fileFilter.py，生成fileIndex.csv
3. 提取AST树，执行SourceCodePreprocessor.java，指定好dataset路径。会生成json和xml文件夹
4. 执行preprocess.py，提取source文件和bug文件。会生成reports_with_tag.json, codes.json, bugs.json, methods.json文件
5. 执行bb.py，处理bug-bug 相似度，生成bb.npy
   1. 如果此前没有执行过word2vec的相关工作，还会生成code2vec.json, report2vec.json和word_idx.json
6. 执行bs.py，处理bug-source的相似度，生成bs.npy

