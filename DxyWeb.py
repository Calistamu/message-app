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
vectorizer = CountVectorizer()
tfidf_transformer = TfidfTransformer()
classifier = MultinomialNB()

def NaiveBayesian():
    data = pd.read_csv("MessageBox.txt", encoding = 'utf-8', sep = '	', header = None,error_bad_lines=False)
    data['分词短信'] = data[1].apply(lambda x:' '.join(jieba.cut(x)))
    X=data['分词短信'].values  
    y=data[0].values         
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1/4, random_state=0)
    X_train_termcounts = vectorizer.fit_transform(X_train)
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_termcounts) 
    classifier.fit(X_train_tfidf, y_train)              #建立朴素贝叶斯分类器并进行训练
    X_input_termcounts  = vectorizer.transform(X_test)  #测试评估
    X_input_tfidf = tfidf_transformer.transform(X_input_termcounts)
    predicted_categories = classifier.predict(X_input_tfidf)
    print('\n正确率：' + str(accuracy_score(y_test, predicted_categories)))
    return classifier

def filter_illegal(datas):
    result=[]
    for data in datas:
        msg0=list(jieba.cut(data['message']))
        msg=''
        for e in msg0:
            msg+=e+' '
        msg=[msg]
        print(msg)
        X_input_termcounts  = vectorizer.transform(msg)  #测试评估
        print(X_input_termcounts)
        X_input_tfidf = tfidf_transformer.transform(X_input_termcounts)
        predicted_categories = classifier.predict(X_input_tfidf) 
        print(predicted_categories)
        if(predicted_categories==1):
            result.append(data)
    return result

app=Flask(__name__)
@app.route("/",methods=["POST"])
def index():
    jsondata = request.get_data()   #json类型
    data=json.loads(jsondata)       #处理json数据 
    fil_data=filter_illegal(data)
    print(json.dumps(fil_data))
    return json.dumps(fil_data)

if __name__=='__main__':
    NaiveBayesian()
    app.run(host='0.0.0.0',port=5001)