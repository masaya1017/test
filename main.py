from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash, make_response, send_from_directory

import MySQLdb
from validate import Form
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import japanize_matplotlib
import matplotlib.pyplot as plt
import random
import numpy as np
from io import BytesIO
import urllib
import cv2
from image_process import canny
from datetime import datetime
import string
from PIL import Image
from keras.models import load_model


# 接続する
conn = MySQLdb.connect(
    user='root',
    passwd='satomi0358',
    host='localhost',
    db='sampldb')
# カーソルを取得する
cur = conn.cursor()

# トランザクションの開始（検証した感じだとデフォルトFALSE）
conn.autocommit = True

# 接続を閉じる

app = Flask(__name__)
# デバッグを可能とする
app.config.update({'DEBUG': True})
# 秘密鍵
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# 画像ファイルの保存ディレクトリの作成
SAVE_DIR = "./images"
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

SAVE_MODEL = "./model"
LOAD_IMG = "./images/dog.jpg"
imsize = (64, 64)
# データの読み込み


def load_image(path):
    img = Image.open(path)
    img = img.convert('RGB')
    img = img.resize(imsize)
    img = np.asarray(img)
    img = img/255.0
    return img


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return render_template('validate.html')
    elif request.method == 'POST':
        return redirect('/')


@app.route('/predict')
def predict():
    model_path = os.path.join(SAVE_MODEL, "cnn.h5")
    model = load_model(model_path)
    img = load_image(LOAD_IMG)
    pred = model.predict(np.array([img]))
    print(pred)
    prelabel = np.argmax(pred, axis=1)
    if prelabel == 0:
        message = "犬です"
    elif prelabel == 1:
        message = "猫です"
    return render_template('result.html', message=message)


# 画像アップ画面
@app.route('/')
def index():
    # imagesフォルダ配下の画像パスをリストとして取得し、htmlに渡す。
    return render_template('index.html', images=os.listdir(SAVE_DIR)[::-1])


@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory(SAVE_DIR, path)


def random_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i
                    in range(n)])


@app.route('/upload', methods=['POST'])
def upload():
    if request.files['image']:
        # 画像として読み込み
        stream = request.files['image'].stream
        img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, 1)

        # 変換
        img = canny(img)

        # 保存
        dt_now = datetime.now().strftime("%Y_%m") + random_str(5)
        save_path = os.path.join(SAVE_DIR, dt_now + ".png")
        # ファイルを指定して、画像を読み込む
        cv2.imwrite(save_path, img)

        print("save", save_path)

        return redirect('/')


@app.route('/registration', methods=['GET', 'POST'])
def registration():

    form = Form()
    # データ
    message = ""
    if request.method == 'GET':
        return render_template('register.html', form=form, message=message)

    elif request.method == 'POST':
        if not form.validate_on_submit():  # 名前入力欄
            return render_template('register.html', form=form, message=message)
        else:
            count = 0
            '''
            task_dao = dao.Dao()
            task_dao.add(request.form["name"])
            list = task_dao.get()
            return render_template('show_entries.html', entries=list)
            '''
            cur.execute('select * from register')
            docs = cur.fetchall()
            print(docs)

            if not docs == "":
                for doc in docs:
                    count += 1
            print(count)
            name = request.form['name']
            print(name)

            try:

                sql_insert = "INSERT INTO register (id,name) VALUES (%s,%s)"
                print(sql_insert)
                cur.execute(sql_insert, (count+1, name))

                conn.commit()
                message = "登録完了しました"

            except Exception as e:
                print(e)
                conn.rollback()
                message = "登録エラーが生じました"

            conn.close
        return render_template('register.html', form=form, message=message)


@app.route('/select', methods=['GET'])
def select():
    return render_template('select.html')


'''
@app.route('/view', methods=['GET'])
def view():
'''


@app.route('/graph1.png')
def graph1():
    # データからグラフをプロットする
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    fig = plt.figure()
    #ax = fig.add_subplot(111)
    plt.title('サンプル')
    plt.grid(which='both')
    plt.legend()
    plt.plot(x, y)
    # canvasにプロットした画像を出力
    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    data = png_output.getvalue()
    # HTML側に渡すレスポンスを生成する
    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Length'] = len(data)
    return render_template('view.html', response=response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
