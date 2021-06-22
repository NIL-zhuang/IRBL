from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet, stopwords
from nltk.stem import snowball as sb
import re
from typing import List
import os


class Lemma:
    stop_words = set(stopwords.words('english') + ['swt', 'eclipse'])
    # stop_words = set([word[:-1] for word in open(os.path.join(os.getcwd(), 'data', 'stopwords.txt'), 'r').readlines()])
    stemmer = sb.SnowballStemmer('english')
    punctuation = "!\"#$%&'()*+-/:;<=>?@[\]^_`{|}~.,"
    regex = re.compile('[%s]' % re.escape(punctuation))
    frontRegex = re.compile(r'&.*?;')

    @staticmethod
    def camel_case_split(word):
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', word)
        return [m.group(0) for m in matches]

    def get_wordnet_pos(self, tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def lemmatizeStr(self, s: str) -> List[str]:
        if not s:
            return []
        s = self.frontRegex.sub(' ', s)  # remove signals like &quote;
        s = self.regex.sub(' ', s)      # remove punctuation
        tokens = word_tokenize(s)
        tagged_sent = pos_tag(tokens)
        wnl = WordNetLemmatizer()
        lemmas_res = []
        for tag in tagged_sent:
            wordnet_pos = self.get_wordnet_pos(tag[1]) or wordnet.NOUN
            word = wnl.lemmatize(tag[0], pos=wordnet_pos)
            for w in self.camel_case_split(word):
                w = self.stemmer.stem(w)
                if not w in self.stop_words and len(w) > 2 and w.isalpha():
                    lemmas_res.append(w)
        return lemmas_res

    def lemmatizeWord(self, words: str) -> List[str]:
        words = self.regex.sub(' ', words).split(' ')
        lemmas_res = []
        for word in words:
            for w in self.camel_case_split(word):
                w = self.stemmer.stem(w)
                if not w in self.stop_words and len(w) > 2 and w.isalpha():
                    lemmas_res.append(w)
        return lemmas_res

    def lemmatizeCode(self, s: str) -> List[str]:
        if not s:
            return []
        lemmas_res = []
        s = self.regex.sub(' ', s).split(' ')
        for word in s:
            for w in self.camel_case_split(word):
                w = self.stemmer.stem(word)
                if len(w) > 2 and w.isalpha():
                    lemmas_res.append(w)
        return lemmas_res


class CommentFilter:
    regAt = re.compile(r'@[^\s]*\s')
    regAngleBracket = re.compile(r'<[^>]*>')
    regSlash = re.compile(r'/[^\s]*\s')

    def filterComment(self, comment: str):
        cmt = comment.replace('* ', '')
        cmt = self.regAt.sub(' ', cmt)
        cmt = self.regAngleBracket.sub('', cmt)
        cmt = self.regSlash.sub(' ', cmt)
        return cmt


if __name__ == "__main__":
    lemma = Lemma()
    print(lemma.lemmatizeWord('STATE_NORMAL'))
