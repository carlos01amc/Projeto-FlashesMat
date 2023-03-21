from flask import Flask, redirect,request, url_for, render_template, send_file,flash
import sympy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import plotly.graph_objs as go
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import io
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
import sqlite3
conn = sqlite3.connect('blog.db')

#shift+alt+f -> format code

app = Flask(__name__)
app.secret_key = "hello"

class NameForm(FlaskForm):
    user = EmailField("Username: ", validators = [Email(), DataRequired()])
    password = PasswordField("Password: ", validators = [DataRequired()])
    submit = SubmitField("login")

@app.route("/login/", methods = ['GET', 'POST'])
def home():
    user = None
    password = None
    form = NameForm()
    if form.validate_on_submit():
        user = form.user.data
        form.user.data = ''
        password = form.password.data
        form.password.data = ''
        
    return render_template("login.html", user = user, form = form, password = password)

@app.route("/")
def login():
    return render_template("index.html")

@app.route("/menu")
def menu():
    conn = sqlite3.connect("blog.db")
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
        conn = sqlite3.connect("blog.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("new_post.html")

@app.route("/post/<int:post_id>")
def post(post_id):
    conn = sqlite3.connect("blog.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()
    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(debug=True)