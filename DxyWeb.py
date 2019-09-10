from flask import Flask,render_template,redirect,request
import json

def filter_illegal(data):

    return data

app=Flask(__name__)
@app.route("/",methods=["POST"])
def index():
    jsondata = request.get_data() #json类型
    data=json.loads(jsondata) #处理json数据 
    fil_data=filter_illegal(data)
    print(json.dumps(fil_data))
    return json.dumps(fil_data)


if __name__=='__main__':
    app.run(host='0.0.0.0',port=5001)