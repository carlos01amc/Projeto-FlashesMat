from flask import Flask, redirect, request, url_for, render_template, session, abort
import os
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
import hashlib
from werkzeug.utils import secure_filename
import sqlite3

conn = sqlite3.connect('database.db')

# shift+alt+f -> format code

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = r'C:\Users\carlo\OneDrive\Ambiente de Trabalho\UM\3ano2s\Projeto\static'


class LogForm(FlaskForm):
    mail = EmailField("Email: ", validators=[Email(), DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("login")


@app.route("/login/", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email=?', (email,))
        user = c.fetchone()
        conn.close()

        if user:
            hash_senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            if hash_senha == user[3]:
                session['email'] = user[2]
                session['tipo'] = user[4]
                return redirect(url_for('home'))
            else:
                return 'Senha incorreta!'
        else:
            return 'E-mail não encontrado!'
    else:
        return render_template('login.html')

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('tipo', None)
    return redirect(url_for('home'))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    conn.close()
    return render_template("menu.html", posts=posts)


@app.route("/criadores/")
def criadores():
    return render_template("creatores.html")


@app.route("/sabermais/")
def sabe():
    return render_template("sabermais.html")


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, content,file_url) VALUES (?, ?, ?)",
                  (title, content, file_path))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("new_post.html")


@app.route("/post/<int:post_id>")
def post(post_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()
    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(debug=True)
