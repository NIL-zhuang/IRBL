# Research Note

## 研究发现

### 停用词相关

对于swt项目来说，如果保留所有的停用词，效果最好，比去除`nltk.stopwords('english')`内停用词，提高7个百分点。而去除JAVA所有保留词的效果是最差的。

其中的原因是，对于word2vec的处理，我们使用了`sklearn.feature_extraction.text.CountVectorizer`。对于停用词会进行少量处理。此外，我们使用了snowball
