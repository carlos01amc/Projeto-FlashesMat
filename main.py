from flask import Flask, redirect, request, url_for, render_template, session, abort, flash
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
app.config["UPLOAD_FOLDER"] = r'C:\Users\carlo\Desktop\UM\3ano2s\Projeto\static\upload'


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
                flash('Senha incorreta',category='error')
                return render_template('login.html',can_edit=False)
        else:
            flash('E-mail não encontrado!',category='error')
            return render_template('login.html',can_edit=False)
    else:
        return render_template('login.html', can_edit=False)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('tipo', None)
    return redirect(url_for('home', can_edit=False))


@app.route("/")
def home():
    return render_template("index.html", can_edit=False)


@app.route("/menu")
def menu():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    conn.close()
    return render_template("menu.html", can_edit=False, posts=posts)


@app.route("/criadores/")
def criadores():
    return render_template("creatores.html", can_edit=False)


@app.route("/sabermais/")
def sabe():
    return render_template("sabermais.html", can_edit=False)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!",category='error')
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = file_path
        else:
            file_url = None
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, content,file_url) VALUES (?, ?, ?)",
                  (title, content, file_url))
        conn.commit()
        conn.close()
        flash("Post criado com sucesso",category='success')
        return redirect("/")
    return render_template("new_post.html", can_edit=False)


@app.route("/post/<int:post_id>")
def post(post_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()

    can_edit = False
    if 'email' in session and session['tipo'] == 'admin':
        can_edit = True

    return render_template("post.html", post=post, can_edit=can_edit)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!",category='error')
        return redirect("/")

    can_edit = False
    if 'email' in session and session['tipo'] == 'admin':
        can_edit = True

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = file_path
        else:
            file_url = None
        c.execute("UPDATE posts SET title=?, content=?, file_url=? WHERE id=?",
                  (title, content, file_url, post_id))
        conn.commit()
        conn.close()
        flash("Post editado com sucesso",category='success')
        return redirect(url_for("post", post_id=post_id))

    conn.close()
    
    return render_template("edit_post.html", post=post, can_edit=can_edit)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']            
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email=?', (email,))
        user = c.fetchone()
        if user:
            flash('Este e-mail já foi registrado',category='error')
            return render_template('register.html')
        if len(senha) < 9:
            flash('Palavra-passe tem que ter mais que 8 caracteres', category = 'error')
            return render_template('register.html')
        
        hash_senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        c.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)',
                  (email, hash_senha))
        conn.commit()
        conn.close()
        flash('Conta criada com sucesso', category='success')
        return render_template('index.html')
    else:
        return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
