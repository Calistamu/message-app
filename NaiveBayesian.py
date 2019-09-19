import pandas as pd
import numpy  as np
import jieba
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer
from sklearn.naive_bayes import GaussianNB,MultinomialNB
from sklearn.metrics import accuracy_score

category_map = {
    0:'正常',
    1:'垃圾'
}

#导入数据集 得到的data[0]=1则是垃圾短信 data[1]是短信内容文本
data = pd.read_csv("MessageBox.txt", encoding = 'utf-8', sep = '	', header = None,error_bad_lines=False)
#对每一条短信内容都进行分词 以空格隔开
data['分词短信'] = data[1].apply(lambda x:' '.join(jieba.cut(x)))
#print(data.head())
#print(data.shape) 数据集的形状？


#分隔训练集和测试集 我们需要从训练集数据中产出学习器，再用测试集来测试所得学习器对新样本的判别能力，
#测试集与训练集是不能有交集的，要做到互相不干扰
X=data['分词短信'].values  #一个列表 80w行 每行是当行短信的分词字符串
#print(X)
y=data[0].values          #一个列表 80w个数字 对应每个短信的判别0/1
#print(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1/4, random_state=0)
#分别对应划分出的训练集数据、测试集数据、训练集标签、测试集标签


#提取文本特征
'''
CountVectorizer是属于常见的特征数值计算类，是一个文本特征提取方法。
对于每一个训练文本，它只考虑每种词汇在该训练文本中出现的频率。
CountVectorizer类是通过fit_transform函数将文本中的词语转换为词频矩阵，
矩阵元素a[i][j] 表示j词在第i个文本下的词频。即各个词语出现的次数，
通过get_feature_names()可看到所有文本的关键字，通过toarray()可看到词频稀疏矩阵的结果。
'''
#将文本数据转化成特征向量
vectorizer = CountVectorizer()
X_train_termcounts = vectorizer.fit_transform(X_train)
#print(X_train_termcounts)
'''词频-逆向文件频率
IF：词频。IF(w)=(词w在文档中出现的次数)/(文档的总词数)
DF：逆向文件频率。有些词可能在文本中频繁出现，但并不重要，也即信息量小，如is,of,that这些单词，
这些单词在语料库中出现的频率也非常大，我们就可以利用这点，降低其权重。
IDF(w)=log_e(语料库的总文档数)/(语料库中词w出现的文档数)
综合参数：IF-IDF=IF*IDF
将文本数据转化为特征向量后，还要将其转化为tf-idf矩阵，TfidfTransformer()方法就是为了这一步的。

CountVectorizer：
    只考虑词汇在文本中出现的频率
TfidfVectorizer：
    除了考量某词汇在文本出现的频率，还关注包含这个词汇的所有文本的数量
    能够削减高频没有意义的词汇出现带来的影响, 挖掘更有意义的特征
'''
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_termcounts) 
#print(X_train_tfidf)


#建立朴素贝叶斯分类器并进行训练
classifier = MultinomialNB()
classifier.fit(X_train_tfidf, y_train)   #建立朴素贝叶斯分类器并进行训练


#模型测试评估
X_input_termcounts  = vectorizer.transform(X_test)
X_input_tfidf = tfidf_transformer.transform(X_input_termcounts)
predicted_categories = classifier.predict(X_input_tfidf)
print('\n正确率：' + str(accuracy_score(y_test, predicted_categories)))
""" for sentence, category, real in zip(X_test[:5], predicted_categories[:5],y_test[:5]):
    print('\n短信内容: ', sentence, '\nPredicted 分类: ', category_map[category], "真实值: ", category_map[real]) """


