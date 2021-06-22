import os
from tqdm import tqdm
from PreProcessor.lemma import Lemma
from file_writer import FileWriter
from file_reader import JSONReader
import report_tagger
import re
from constants import report_with_tag_p

if __name__ == "__main__":
    lemmanizer = Lemma()
    pattern = re.compile(r'<.+>', re.M | re.I)

    report_tagger.tag_and_extract()
    reports = JSONReader(report_with_tag_p).readFile()

    for eleId in tqdm(reports, desc="lemmatize bugs:"):
        # id = ele.attrib['id']
        # summary = lemmanizer.lemmatizeStr(ele[0][0].text)
        # description = lemmanizer.lemmatizeStr(ele[0][1].text)
        nl = lemmanizer.lemmatizeStr(reports[eleId]['NL'])
        sc = lemmanizer.lemmatizeStr(reports[eleId]['SC'])
        FileWriter(os.sep.join(['report', str(eleId) + ".txt"]), '\n'.join(nl + sc)).writeFile()
