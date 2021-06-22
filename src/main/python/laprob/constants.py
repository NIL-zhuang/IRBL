import os
from init import project

data_pool_path = 'data'  # 正常使用时激活
# data_pool_path = '/Users/chengrongxin/irbl/data'  # crx debug专用
# proj = 'aspectj'
# proj = 'eclipse'
proj = 'swt'

projects_path = os.path.join(data_pool_path, proj)
problesmfiles = os.path.join(data_pool_path, 'problemfiles.txt')
# projects_path = os.sep.join([r'E:\NJU\Course\软工专业课\软件工程与计算3\KhyYYDS\irbl\data', proj])  # glh DEBUG专用

bugReport = os.sep.join([projects_path, 'bugReport.xml'])  # bug报告路径，随项目proj的切换一起切换
codeFiles = os.sep.join([projects_path, 'json'])  # 所有的代码文件（经过AST抽取）

bugs = os.path.join(projects_path, 'bugs.json')
codes = os.path.join(projects_path, 'codes.json')
methods = os.path.join(projects_path, 'methods.json')

processed_report = os.path.join(projects_path, 'bugs')
processed_code = os.path.join(projects_path, 'words')
srcComponent = os.path.join(projects_path, 'srcComponent')
bugComponent = os.path.join(projects_path, 'bugComponent')
srcMethods = os.path.join(projects_path, 'methods')

report_vectors = os.path.join(projects_path, 'report2vec.json')
code_vectors = os.path.join(projects_path, 'code2vec.json')
word_idx = os.path.join(projects_path, 'word_idx.json')

dependency = os.path.join(projects_path, 'ss.csv')
dependency_matrix = os.path.join(projects_path, 'ss.npy')
ssPath = os.path.join(projects_path, 'ss.npy')
bsPath = os.path.join(projects_path, 'bs.npy')
bbPath = os.path.join(projects_path, 'bb.npy')
BHG_matrix = os.path.join(projects_path, 'BHG.npy')
F = os.path.join(projects_path, 'F.npy')

bug_src_map = os.path.join(projects_path, 'bug_src_map.json')

fileIndex = os.path.join(projects_path, 'fileIndex.csv')

report_with_tag = os.path.join(projects_path, 'reports_with_tag.json')
final_score_path = os.path.join(projects_path, 'final_score.json')
cheat_score_path = os.path.join(projects_path, 'cheat_score.json')

alpha = 0.9
beta = 0.3
theta = 0.2
markRate = 0.05

# =======================================================================
# 以下为迭代二中使用，三阶段原则上弃用
# simi_calculator使用
doc2vec_path = 'doc2vec.json'  # 向量化文本(代码文件+bug报告)数据文件所在路径
bug2vec_path = 'bug2vec.json'  # 向量化bug报告结果
rvsm_score_path = 'rvsm_score.json'
simibugs_score_path = 'simibugs_score.json'
g_dct_path = 'g_dct.json'  # 调和值g的所在路径
