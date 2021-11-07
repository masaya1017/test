
from flask import Flask, request, render_template,\
    redirect, url_for, jsonify
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

'''
db_uri = "sqlite:///api.db"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["DEBUG"] = True
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    #テーブル名
    __tablename__='article'
    #autoicrement=Trueのときは自動的に1からデータを割り振ってくれる。
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    article = db.Column(db.String(300))
'''
app = Flask(__name__)
# デバッグを可能とする
app.config.update({'DEBUG': True})
# 秘密鍵
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
