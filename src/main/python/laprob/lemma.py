from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet, stopwords
from nltk.stem import snowball as sb
import re
from typing import List
import os


class Lemma():
    def __init__(self):
        additionStopWords = ['swt', 'eclipse', 'aspectj']
        javaWords = "abstract,assert,boolean,break,byte,case,catch,char,class,const,continue,default,do,double,else,enum,extends,final,finally,float,for,if,implements,import,instanceof,int,interface,long,native,new,package,private,protected,public,return,short,static,strictfp,super,switch,synchronized,this,throw,throws,transient,try,void,volatile,while,byValue,cast,false,future,generic,inner,operator,outer,rest,true,var,goto,const,null"
        codePunctuation = "!\"#$%&'()*+-/:;<=>?@[\]^`{|}~.,"
        fullPunctuation = codePunctuation+'_'
        # self.bigStopwords = set(stopwords.words('english')+additionStopWords + javaWords.split(','))
        # self.stopwords = set(stopwords.words('english')+additionStopWords)
        # self.stopwords = set(javaWords.split(','))
        self.stopwords = set(stopwords.words('english'))
        self.camelCaseSplit = '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)'
        self.punctuationSplit = re.compile('[%s]' % re.escape(codePunctuation))
        self.fullPunctuationSplit = re.compile('[%s]' % re.escape(fullPunctuation))
        self.stemmer = sb.SnowballStemmer('english')
        self.quoteSplit = re.compile(r'&.*?;')

    def camel_case_split(self, word):
        matches = re.finditer(self.camelCaseSplit, word)
        lst = [m.group(0) for m in matches]
        if word not in lst:
            lst.append(word)
        return lst

    def lemmatizeWord(self, word):
        """
        把一个可能有多个分隔的单词拆开，然后拆开特定的驼峰命名单词
        """
        words = self.punctuationSplit.sub(' ', word).split(' ')
        lemmas_res = []
        for word in words:
            curWord = [item.lower() for w in word.split('_') for item in self.camel_case_split(w)]
            for w in curWord:
                w = self.stemmer.stem(w)
                if len(w) > 2 and w.isalpha():
                    lemmas_res.append(w)
        return lemmas_res

    def lemmatizeStr(self, s) -> List[str]:
        """
        将字符串作分割后引入
        """
        if not s:
            return []
        s = self.quoteSplit.sub(' ', s)
        s = self.fullPunctuationSplit.sub(' ', s)
        res = []
        for word in s.split(' '):
            res += self.lemmatizeWord(word)
        return res
        # return [word for word in res if word not in self.stopwords]


class CommentFilter():

    def __init__(self):
        self.regAt = re.compile(r'@[^\s]*\s')
        self.regAngleBracket = re.compile(r'<[^>]*>')
        self.regSlash = re.compile(r'/[^\s]*\s')

    def filterComment(self, comment: str):
        if comment is None:
            return ""
        cmt = comment.replace('* ', '')
        cmt = self.regAt.sub(' ', cmt)
        cmt = self.regAngleBracket.sub('', cmt)
        cmt = self.regSlash.sub(' ', cmt)
        return cmt


if __name__ == "__main__":
    lemma = Lemma()
    print(*lemma.lemmatizeWord("word_word w1 ww11"))
    # print(lemma.lemmatizeStr("Big News isComming"))
