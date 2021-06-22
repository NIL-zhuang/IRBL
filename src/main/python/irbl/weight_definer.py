import math
from file_writer import *
from file_reader import *
from constants import data_pool_path
from collections import Counter


def get_words(fname: str) -> list:
    """
    获取某个文件中的所有单词
    :param fname: 文件名
    :return: 单词列表
    """
    words = FileReader(fname).readFile().split('\n')
    return words


def get_word_count(words: list) -> dict:
    """
    获得单词以及出现的次数
    :param words: 所有单词的列表
    :return: 返回字典，key:单词，value:单词出现的次数
    """
    return Counter(words)


# 用于根据文档大小加权，帮助大文档有更高排名
def get_g(terms, max_num, min_num):
    N = (terms - min_num) / (max_num - min_num)
    g = 1 / (1 + math.exp(-N))
    return g


def calculate_tfidf(file_list: list, all_word_count: dict, each_file_word_count: list):
    tfidf = []
    g_dct = {}
    doc_num = len(each_file_word_count)  # 文档数目
    all_words = sorted(all_word_count)  # 所有单词
    max_num = 0  # 所有代码文件中总词数的最大值
    min_num = 1e9  # 所有代码文件中总词数的最小值
    for word_count in each_file_word_count:
        total_words = sum(word_count.values())  # 一个文档中所有词语的总数
        max_num = max(max_num, total_words)
        min_num = min(min_num, total_words)

    for idx, word_count in enumerate(each_file_word_count):
        dct = {}
        total_words = sum(word_count.values())  # 一个文档中所有词语的总数

        filepath, tempfilename = os.path.split(file_list[idx])
        fname, extension = os.path.splitext(tempfilename)
        g_dct[fname] = get_g(total_words, max_num, min_num)

        for word in all_words:
            if word in word_count:
                # tf value
                tf = math.log(word_count[word]) + 1
                # idf value
                idf = math.log(doc_num / all_word_count[word] + 1)
                # store tf-idf value
                dct[word] = tf * idf
            else:
                dct[word] = 0
        tfidf.append(dct.copy())

    JSONWriter('g_dct.json', g_dct).writeFile()
    return tfidf


def get_tfidf(file_list: list, word_idx_path: str, doc2vec_path: str):
    """
    变量说明
    each_file_words: list
    其中每个元素是一个dict，其结构如下
    { key: 单词, value: 单词在文档中出现的次数 }

    all_words: dict
    记录所有在文档中出现过的单词
    { key: 单词, value: 在多少篇文档中出现 }

    tfidf: list
    """
    each_file_words = []
    all_words = {}
    doc_num = len(file_list)

    # step1: 记录每个文件，每个单词对应的个数
    for file in file_list:
        each_file_words.append(get_word_count(get_words(file)))

    # step2: 记录每个单词各在多少篇文章中出现过
    for word_count in each_file_words:
        # word_count中的word出现在文档中
        for word in word_count:
            if word in all_words:
                all_words[word] += 1
            else:
                all_words[word] = 1

    dct = {}
    index = 0
    sorted_words = sorted(all_words)
    for key in sorted_words:
        dct[key] = index
        index += 1
    JSONWriter(word_idx_path, dct).writeFile()

    tfidf = calculate_tfidf(file_list, all_words, each_file_words)
    result = {}
    for i in range(doc_num):
        filepath, tempfilename = os.path.split(file_list[i])
        fname, extension = os.path.splitext(tempfilename)
        lst = []
        for w in sorted_words:
            lst.append(tfidf[i][w])
        result[fname] = lst
    JSONWriter(doc2vec_path, result).writeFile()


if __name__ == '__main__':
    file_paths = []
    class_dir = 'class'
    report_dir = 'report'
    for filename in os.listdir(os.path.join(data_pool_path, class_dir)):
        file_paths.append(os.path.join(class_dir, filename))
    for filename in os.listdir(os.path.join(data_pool_path, report_dir)):
        file_paths.append(os.path.join(report_dir, filename))
    word2idx_path = 'word2idx.json'
    word2vec_path = 'doc2vec.json'
    get_tfidf(file_paths, word2idx_path, word2vec_path)
