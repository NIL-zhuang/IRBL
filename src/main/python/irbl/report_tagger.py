import re
import xml.etree.ElementTree as et
from tqdm import tqdm
from file_writer import JSONWriter
import os
from constants import data_pool_path, report_with_tag_p, stack_list_p, bugReport

value_rate = 4  # summary和description的权重比


class ReportTagger:
    def __init__(self):
        self.flags = re.M | re.I
        self.stackPattern = re.compile(r'java\.(.+)\.(.+Exception)( at (.+\.)+(.+)\(.+\.java:[1-9][0-9]*\))+',
                                       self.flags)
        # 依次为：public声明句、private声明句、类/方法声明句、if块、while块、for块、赋值语句、调用语句
        # warning：千万别乱动这里的正则表达式，错了很难恢复！
        self.codePattern = [re.compile(p, self.flags) for p in
                            [r'public.+(\{.+\})', r'private.+(\{.+\})', r'([a-zA-Z]+( )*){1,2}(\{.*\})',
                             r'if.+(\{.+\})',
                             r'while.+(\{.+\})', r'for.+(\{.+\})', r'(([a-zA-Z]+( )*){1,2}=[^;]+;( )*)+',
                             r'([^=;]+)(\.([^ \.]+\([^;]+\)));']]

    def split(self, content):
        stackRange = self.getStack(content)
        codeRange = self.getCode(content)
        result = {"NL": '', "SC": '', "ST": ''}
        if stackRange is None and codeRange is None:
            result['NL'] = content
        elif stackRange is None or codeRange is None:
            block = stackRange if stackRange else codeRange
            key = 'ST' if stackRange else 'SC'
            result[key] = content[block[0]:block[1]]
            result['NL'] = content[:block[0]] + content[block[1]:]
        else:
            if codeRange[0] < stackRange[0]:
                left = codeRange
                leftKey = 'SC'
                right = stackRange
                rightKey = 'ST'
            else:
                left = stackRange
                leftKey = 'ST'
                right = codeRange
                rightKey = 'SC'
            right[0] = max(left[1], right[0])  # 防止因为匹配漏洞出现交集
            result[leftKey] = content[left[0]:left[1]]
            result[rightKey] = content[right[0]:right[1]]
            result['NL'] = content[:left[0]] + content[left[1]:right[0]] + content[right[1]:]
        return result

    def getStack(self, content):
        result = self.stackPattern.search(content)
        if result is not None:
            return list(result.span())
        return None

    def getCode(self, content):
        n = len(content)
        result = [n, 0]
        for p in self.codePattern:
            tmp = p.search(content)
            if tmp is None:
                continue
            tmp = tmp.span()
            if tmp[0] >= result[0] and tmp[1] <= result[1]:
                continue
            result[0] = min(result[0], tmp[0])
            result[1] = max(result[1], tmp[1])
        return result if result[0] < n else None


# 测试用代码 def test(self): a = 'Here is a stack trace I found when trying to kill a running process by pressing the
# final Display display = new Display(); Shell shell = new Shell(display); shell.setLayout(new FillLayout()).display(
# ); SashForm form = new SashForm(shell, SWT.HORIZONTAL | SWT.SMOOTH); form.setLayout(new FillLayout()); Composite
# child1 = new Composite(form, SWT.NONE); child1.setLayout(new FillLayout()); new Label(child1, SWT.NONE).setText(
# &amp;quot;Label in pane 1&amp;quot;); Composite child2 = new Composite(form, SWT.NONE); child2.setLayout(new
# FillLayout()); new Button(child2, SWT.PUSH).setText(&amp;quot;Button in pane2&amp;quot;); Composite child3 = new
# Composite(form, SWT.NONE); child3.setLayout(new FillLayout()); new Label(child3, SWT.PUSH).setText(&amp;quot;Label
# in pane3&amp;quot;); form.setWeights(new int[] { 30, 40, 30 }); shell.open(); while (!shell.isDisposed()) { if (
# !display.readAndDispatch()) display.sleep(); } display.dispose(); } }' result = self.split(a) print(a) for k in
# result: print(k, ':', result[k])

#
# r = ReportTagger()
# r.test()

class StackExtractor:
    def __init__(self):
        self.java_files = list()
        for file in os.listdir(data_pool_path + os.sep + 'class'):
            if file[0] == '.':
                continue  # 跳过隐藏文件，例如.DS_Store
            self.java_files.append(file.replace('txt', 'java'))
        self.pattern = re.compile(r'\([^\)]+\.java', re.M)

    def get_relevant(self, stack):
        # 正则表达式匹配结果是带括号的，需要去掉最开始的括号
        files = [name[1:] for name in self.pattern.findall(stack)]
        result = []
        for f in files:
            if f in self.java_files:
                result.append(f)
        return result


def extract_from_stack(stack_extractor, stack_info):
    return stack_extractor.get_relevant(stack_info)


def tag_and_extract():
    """
    这个函数有职责过重的嫌疑，但是考虑到二阶段代码只是个抛弃式原型，就不做设计上的优化了
    职责1：为所有报告打上NL、ST、SC的标签，并存储为reports_with_tag.json
    职责2：将报告堆栈信息中的项目文件提取出来（如果有），并存储为stack_list.json
    两个职责的数据源都是bugReports
    :return:
    """
    # 读取并解析xml
    rt = ReportTagger()
    tree = et.ElementTree(file=bugReport)
    root = tree.getroot()
    # 下面两个字典分别用来存放class文件打标签的结果和报告堆栈信息中的项目文件
    result = {}
    stack_list = {}
    extractor = StackExtractor()

    for ele in tqdm(tree.iter(tag='bug'), total=len(root), desc="tagging:"):
        rptId = ele.attrib['id']
        summary = ele[0][0].text
        description = ele[0][1].text
        # description 可能为空，这里使用一下防御式编程，防止字符串和空值相加
        src = ''
        if summary:
            src += summary * value_rate
        else:
            print('发现问题报告', rptId)
        if description:
            src += description
        else:
            print('发现问题报告', rptId)
        # 打完标签的结果写入result
        result[rptId] = rt.split(src)
        # 写入stack信息中和项目直接关联的文件名
        stack_list[rptId] = extract_from_stack(extractor, result[rptId]["ST"])

    report_writer = JSONWriter(report_with_tag_p, result)
    report_writer.writeFile()

    stack_writer = JSONWriter(stack_list_p, stack_list)
    stack_writer.writeFile()

# 测试用代码，开发完成后可以删除
# if __name__ == '__main__':
#     pattern = re.compile(r'\([^\)]+\.java', re.M)
#     src = '(a.java);(b.java)'
#     print(pattern.findall(src))
