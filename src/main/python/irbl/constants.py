import os

# data_pool_path = 'Datapool'  # DEBUG专用
data_pool_path = os.sep.join(['src', 'main', 'python', 'irbl', 'Datapool'])  # 正常使用时激活
bugReport = os.sep.join(["data", "SWTBugRepository.xml"])

report_with_tag_p = 'reports_with_tag.json'
stack_list_p = 'stack_list.json'

# simi_calculator使用
doc2vec_path = 'doc2vec.json'  # 向量化文本(代码文件+bug报告)数据文件所在路径
bug2vec_path = 'bug2vec.json'  # 向量化bug报告结果
rvsm_score_path = 'rvsm_score.json'
simibugs_score_path = 'simibugs_score.json'
final_score_path = 'final_score.json'
g_dct_path = 'g_dct.json'  # 调和值g的所在路径
