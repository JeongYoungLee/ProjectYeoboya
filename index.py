from pdb import post_mortem
from queue import Empty
from unicodedata import name
from unittest import result
from flask import Flask, render_template, redirect, request, url_for, session
import cx_Oracle as db
import pickle
#from sklearn.feature_extraction.text import CountVectorizer
import plotly.express as px
import pandas as pd
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
import time

from hanspell import spell_checker
from pykospacing import Spacing
import googletrans
from googletrans import Translator

spacing = Spacing()
translator = Translator()

cEXT = pickle.load( open( "model/cEXT.p", "rb"))
cNEU = pickle.load( open( "model/cNEU.p", "rb"))
cAGR = pickle.load( open( "model/cAGR.p", "rb"))
cCON = pickle.load( open( "model/cCON.p", "rb"))
cOPN = pickle.load( open( "model/cOPN.p", "rb"))
vectorizer_31 = pickle.load( open( "model/vectorizer_31.p", "rb"))
vectorizer_30 = pickle.load( open( "model/vectorizer_30.p", "rb"))

app = Flask(__name__)

db_id = 'vis'
db_pw = 'gjvis4444'
url = 'project-db-stu.ddns.net:1524/xe'

app.secret_key = "vis"

@app.route('/')
def main():
    conn = db.connect(db_id, db_pw, url)
    curs = conn.cursor()
    
    sql = "select * from user_t"
    curs.execute(sql)
    result = curs.fetchall()
    print(result)
    curs.close()
    conn.close()
    return print('통신 확인 완료')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        print('로그인 시도')
        mail = request.form['mail']
        pw = request.form['pw']
        
        conn = db.connect(db_id, db_pw, url)
        curs = conn.cursor()
        
        sql = "select * from user_t where (user_mail = :1) and (user_pw = :2)"
        curs.execute(sql,(mail,pw))
        result = curs.fetchall()
        print(result)
        curs.close()
        conn.close()
        print('로그인 완료')
        return result

@app.route('/join', methods=['POST'])
def join():
    print('회원가입 요청')
    if request.method == 'POST':
        #id = request.form['id']
        pw = request.form['pw']
        email = request.form['email']
        nick = request.form['nick']
        birth = request.form['birth']
        gender = request.form['gender']
        
        conn = db.connect(db_id, db_pw, url)
        curs = conn.cursor()
        
        sql = "insert into user_t values (user_t_seq.nextval,:1,:2,:3,:4,:5,sysdate)"
        curs.execute(sql,(email,pw,nick,gender,birth))
        conn.commit()
        curs.close()
        conn.close()
        print(f'회원정보 : {pw},{email},{nick},{gender},{birth}')
        return '가입 완료'

@app.route('/personality', methods = ['GET', 'POST'])
def predict_personality(text):
    scentences = re.split("(?<=[.!?]) +", text)
    text_vector_31 = vectorizer_31.transform(scentences)
    text_vector_30 = vectorizer_30.transform(scentences)

    EXT1 = cEXT.predict_proba(text_vector_31)
    NEU1 = cNEU.predict_proba(text_vector_30)
    AGR1 = cAGR.predict_proba(text_vector_31)
    CON1 = cCON.predict_proba(text_vector_31)
    OPN1 = cOPN.predict_proba(text_vector_31)

    return [EXT1[0][1], NEU1[0][1], AGR1[0][1], CON1[0][1], OPN1[0][1]*0.8]

@app.route('/processing', methods = ['GET', 'POST'])
def processing(sentence):
    try:
        # 한글, 공백만 추출
        sentence = sentence.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
        # 표준어
        intrd_spell = spell_checker.check(sentence)
        sentence = intrd_spell.checked
        # 띄어쓰기
        sentence = spacing(sentence)
        # 영어번역
        sentence = translator.translate(sentence, src='ko', dest='en').text
        return sentence
    except:
        pass
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000)