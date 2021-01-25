import sqlite3
from flask import Flask, render_template, request, redirect, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import random
import time
import logging
import json


app = Flask(__name__)


logging.basicConfig(filename=time.strftime('%Y-%m-%d', time.localtime(time.time())) + "_log.log",
                    level=logging.DEBUG)


string_pool = list("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def get_id(file):
    conn = sqlite3.connect("employee.db")
    cur = conn.cursor()
    print("get")
    while True:
        _id = random.choice(string_pool) + random.choice(string_pool)

        cur.execute('SELECT * FROM file WHERE (file=?)', (file,))
        if not cur.fetchall():
            cur.execute('SELECT * FROM file WHERE (id=?)', (_id, ))
            if not cur.fetchall():
                conn.commit()
                conn.close()
                return _id
        else:
            return "__fail__"


def write_data(a, b, c, d):
    conn = sqlite3.connect("employee.db")
    cur = conn.cursor()
    cur.execute('INSERT INTO file(id, file, time, cnt) VALUES (?, ?, ?, ?)', (a, b, c, d))
    conn.commit()
    conn.close()


def read_data(_id):
    conn = sqlite3.connect("employee.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM file WHERE id='%s'" % _id)
    _return = cur.fetchall()
    conn.close()
    try:
        return _return[0][1]

    except KeyError:
        return True


@app.route("/", methods=['GET'])
def index():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    err_ = request.args.get('err')
    if err_ == "404":
        return render_template("index.html", err=True)

    return render_template("index.html")


# 파일
@app.route("/file")
def file_index():
    return render_template("file/index.html")


@app.route("/upload")
def upload():
    return render_template("file/upload.html")


@app.route("/complete", methods=['GET', 'POST'])
def file_upload():
    # ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)

        _id = get_id(filename)
        if _id == "__fail__":
            return render_template("file/result.html", fail=True)
        t = time.time()
        write_data(_id, secure_filename(filename), t, 0)
        file.save(os.path.join("upload", filename))
        return render_template("file/result.html", _files=filename, _id=_id)

    return redirect("/")


@app.route("/d")
def download():
    return render_template("file/download.html")


@app.route("/d/<file_id>")
def get_profile(file_id):
    file = read_data(file_id)
    if file:
        file = "잘못된 아이디입니다."
    return render_template("file/do.html", file=file)


@app.route("/do/<file>")
def do(file):
    return send_file("upload/" + file, attachment_filename=file, as_attachment=True)


@app.route("/redirect", methods=["POST", "GET"])
def gogo():
    if request.method == 'POST':
        id_ = request.form.get('id')
        return redirect("/d/"+id_)


# ai
@app.route("/ai")
def ai():
    return redirect("https://web-chat.global.assistant.watson.cloud.ibm.com/"
                    + "preview.html?region=kr-seo&integrationID=73dbc727-82aa-41"
                    + "86-bb30-8f3acd19fb76&serviceInstanceID=4d5d9ef3-d64c-48e9-bd97-f14756c46928")


@app.route("/bot", methods=['POST', 'GET'])
def bot():
    params = json.loads(request.get_data(), encoding='utf-8')
    print(params)
    return jsonify({"doing": "asdf"})


# 404
@app.errorhandler(404)
def page_not_found(e):
    type(e)
    return redirect("/?err=404")


app.run(host="0.0.0.0", port=4999, debug=True)
