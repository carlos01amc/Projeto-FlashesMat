from flask import Flask, redirect, request, url_for, render_template, session, flash
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
                session['id_user'] = user[0]
                return redirect(url_for('home'))
            else:
                flash('Senha incorreta', category='error')
                return render_template('login.html', can_edit=False)
        else:
            flash('E-mail não encontrado!', category='error')
            return render_template('login.html', can_edit=False)
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
        flash("Acesso negado!", category='error')
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.form['download']
        file = request.files["file"]

        if content:
            content = content
        else:
            content = None

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = file_path
        else:
            file_url = None

        if thumbnail:
            # Salvar arquivo de imagem na pasta de uploads
            filename = secure_filename(thumbnail.filename)
            thumbnail_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            thumbnail.save(thumbnail_path)
            thumbnail_url = thumbnail_path
        else:
            thumbnail_url = None

        if snapshots_1:
            # Salvar arquivo de snapshot 1 na pasta de uploads
            filename = secure_filename(snapshots_1.filename)
            snapshots_1_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_1.save(snapshots_1_path)
            snapshots_1_url = snapshots_1_path
        else:
            snapshots_1_url = None

        if snapshots_2:
            # Salvar arquivo de snapshot 2 na pasta de uploads
            filename = secure_filename(snapshots_2.filename)
            snapshots_2_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_2.save(snapshots_2_path)
            snapshots_2_url = snapshots_2_path
        else:
            snapshots_2_url = None

        if snapshots_3:
            # Salvar arquivo de snapshot 3 na pasta de uploads
            filename = secure_filename(snapshots_3.filename)
            snapshots_3_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_3.save(snapshots_3_path)
            snapshots_3_url = snapshots_3_path
        else:
            snapshots_3_url = None

        # Conectar à base de dados
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Inserir dados na tabela de postagens
        c.execute("INSERT INTO posts (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, content, thumbnail_url, file_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, links, download))

        conn.commit()
        conn.close()
        flash("Post criado com sucesso", category='success')
        return redirect("menu")
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
        flash("Acesso negado!", category='error')
        return redirect("/")

    can_edit = False
    if 'email' in session and session['tipo'] == 'admin':
        can_edit = True

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()

    # Colocar as variáveis a None caso não haja valores

    thumbnail_url = post[3] if post[3] else None
    file_url = post[4] if post[4] else None
    snapshots_1_url = post[6] if post[6] else None
    snapshots_2_url = post[7] if post[7] else None
    snapshots_3_url = post[8] if post[8] else None
    links = post[9] if post[9] else None
    download = post[10] if post[10] else None

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.form['download']
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = file_path

        if thumbnail:
            # Salvar arquivo de imagem na pasta de uploads
            filename = secure_filename(thumbnail.filename)
            thumbnail_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            thumbnail.save(thumbnail_path)
            thumbnail_url = thumbnail_path

        if snapshots_1:
            # Salvar arquivo de snapshot 1 na pasta de uploads
            filename = secure_filename(snapshots_1.filename)
            snapshots_1_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_1.save(snapshots_1_path)
            snapshots_1_url = snapshots_1_path

        if snapshots_2:
            # Salvar arquivo de snapshot 2 na pasta de uploads
            filename = secure_filename(snapshots_2.filename)
            snapshots_2_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_2.save(snapshots_2_path)
            snapshots_2_url = snapshots_2_path

        if snapshots_3:
            # Salvar arquivo de snapshot 3 na pasta de uploads
            filename = secure_filename(snapshots_3.filename)
            snapshots_3_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_3.save(snapshots_3_path)
            snapshots_3_url = snapshots_3_path

        # Conectar à base de dados e atualizar o post
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        if links:
            # Atualizar links
            c.execute("UPDATE posts SET links=? WHERE id=?", (links, post_id))

        if download:
            # Atualizar links de download
            c.execute("UPDATE posts SET download=? WHERE id=?",
                      (download, post_id))

         # Atualizar demais informações do post
        c.execute("UPDATE posts SET title=?, content=?, thumbnail_url=?, author=?, snapshots_1=?, snapshots_2=?, snapshots_3=?, file_url=? WHERE id=?",
                  (title, content, thumbnail_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, file_url, post_id))
        conn.commit()
        conn.close()
        flash("Post editado com sucesso", category='success')
        return redirect(url_for("menu", post_id=post_id))
    return render_template("edit_post.html", post=post, can_edit=can_edit)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']
        nome = request.form['nome']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email=?', (email,))
        user = c.fetchone()
        if user:
            flash('Este e-mail já foi registrado', category='error')
            return render_template('register.html')
        if len(senha) < 9:
            flash('Palavra-passe tem que ter mais que 8 caracteres', category='error')
            return render_template('register.html')

        hash_senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        c.execute('INSERT INTO usuarios (nome,email, senha) VALUES (?,?, ?)',
                  (nome, email, hash_senha))
        conn.commit()
        conn.close()
        flash('Conta criada com sucesso', category='success')
        return render_template('index.html')
    else:
        return render_template('register.html')


@app.route('/new-form', methods=['GET', 'POST'])
def form():
    if 'email' not in session:
        flash("Acesso negado!", category='error')
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.form['download']
        file = request.files["file"]
        if content:
            content = content
        else:
            content = None
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = file_path
        else:
            file_url = None

        if thumbnail:
            # Salvar arquivo de imagem na pasta de uploads
            filename = secure_filename(thumbnail.filename)
            thumbnail_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            thumbnail.save(thumbnail_path)
            thumbnail_url = thumbnail_path
        else:
            thumbnail_url = None

        if snapshots_1:
            # Salvar arquivo de snapshot 1 na pasta de uploads
            filename = secure_filename(snapshots_1.filename)
            snapshots_1_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_1.save(snapshots_1_path)
            snapshots_1_url = snapshots_1_path
        else:
            snapshots_1_url = None

        if snapshots_2:
            # Salvar arquivo de snapshot 2 na pasta de uploads
            filename = secure_filename(snapshots_2.filename)
            snapshots_2_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_2.save(snapshots_2_path)
            snapshots_2_url = snapshots_2_path
        else:
            snapshots_2_url = None

        if snapshots_3:
            # Salvar arquivo de snapshot 3 na pasta de uploads
            filename = secure_filename(snapshots_3.filename)
            snapshots_3_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            snapshots_3.save(snapshots_3_path)
            snapshots_3_url = snapshots_3_path
        else:
            snapshots_3_url = None

        # Conectar à base de dados
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Inserir dados na tabela de postagens
        c.execute("INSERT INTO forms (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, content, thumbnail_url, file_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, links, download))

        conn.commit()
        conn.close()
        flash("Post submetido com sucesso", category='success')
        return redirect("/")

    return render_template('formulario.html')


@app.route('/admin_page/<int:admin_id>', methods=['GET', 'POST'])
def admin(admin_id):
    if 'email' not in session or session['tipo'] != 'admin' or session['id_user'] != admin_id:
        flash("Acesso negado!", category='error')
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE id=?", (admin_id,))
    usuario = c.fetchone()
    conn.close()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM forms")
    forms = c.fetchall()
    conn.close()

    return render_template('admin_page.html', usuario=usuario, forms=forms)


@app.route("/form/<int:form_id>")
def forms(form_id):

    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!", category='error')
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM forms WHERE id=?", (form_id,))
    post = c.fetchone()
    conn.close()

    return render_template("form.html", post=post, can_edit=False)


@app.route("/delete", methods=["POST"])
def delete():
    form_id = request.form.get('form_id')
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM forms WHERE id=?", (form_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home', can_edit=False))

@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    flash('Post apagado com sucesso', category='success')
    return redirect(url_for('menu', can_edit=False))


@app.route('/approved', methods=['POST'])
def approved():
    post_id = request.form['post_id']
    title = request.form['title']
    content = request.form['content']
    thumbnail_url = request.form['thumbnail_url']
    file_url = request.form['file_url']
    author = request.form['author']
    snapshots_1 = request.form['snapshots_1']
    snapshots_2 = request.form['snapshots_2']
    snapshots_3 = request.form['snapshots_3']
    links = request.form['links']
    download = request.form['download']
    created_at = request.form['date']

    # Conectar com a base de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Inserir os valores do formulário na base de dados "nice"
    cursor.execute('''INSERT INTO posts(title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download, created_at) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download, created_at))

    # Remover os valores do formulário da base de dados "forms"
    cursor.execute('''DELETE FROM forms WHERE id = ?''', (post_id,))

    # Salvar as mudanças e fechar a conexão com a base de dados
    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
