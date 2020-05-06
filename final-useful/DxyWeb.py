from flask import Flask,render_template,redirect,request
import json
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

#停用词表
with open('StopWord.txt', 'rb') as fp:
    stopword = fp.read().decode('utf-8') 
stpwrdlst = stopword.splitlines()

vectorizer = CountVectorizer(stop_words=stpwrdlst)
tfidf_transformer = TfidfTransformer()
classifier = MultinomialNB()
   
def NaiveBayesian():
    data = pd.read_csv("MessageBox.txt", encoding = 'utf-8', sep = '	', header = None,error_bad_lines=False)
    data = data.astype(str)
    #分词
    data['分词短信'] = data[1].apply(lambda x:' '.join(jieba.cut_for_search(x)))
    X=data['分词短信'].values  
    y=data[0].values 
    #分隔训练集和测试集        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1/4, random_state=0)
    #文本特征提取
    X_train_termcounts = vectorizer.fit_transform(X_train)              #将文本数据转化成特征向量
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_termcounts) #将特征向量转化为tf-idf矩阵
    #建立朴素贝叶斯分类器并进行训练
    classifier.fit(X_train_tfidf, y_train)                  
    #测试评估
    X_input_termcounts  = vectorizer.transform(X_test)      
    X_input_tfidf = tfidf_transformer.transform(X_input_termcounts)
    predicted_categories = classifier.predict(X_input_tfidf)
    print('\n正确率：' + str(accuracy_score(y_test, predicted_categories)))
    return classifier

def filter_illegal(datas):
    result=[]
    for data in datas:
        msg0=list(jieba.cut_for_search(data['message']))
        msg=''
        for e in msg0:
            msg+=e+' '
        msg=[msg]
        print(msg)
        X_input_termcounts  = vectorizer.transform(msg)
        X_input_tfidf = tfidf_transformer.transform(X_input_termcounts)
        predicted_categories = classifier.predict(X_input_tfidf) 
        print(predicted_categories)
        if(predicted_categories[0]=='1'):
            result.append(data)
    print('-------------------------------')
    print(result)
    return result

app=Flask(__name__)
@app.route("/",methods=["POST"])
def index():
    jsondata = request.get_data()   #json类型
    data=json.loads(jsondata)       #处理json数据 
    fil_data=filter_illegal(data)   #垃圾短信筛选函数
    return json.dumps(fil_data)

if __name__=='__main__':
    NaiveBayesian()
    app.run(host='0.0.0.0',port=5001)