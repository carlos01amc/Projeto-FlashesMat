from flask import Flask, redirect, request, url_for, render_template, session, flash, send_file, g
import os
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
import hashlib
from werkzeug.utils import secure_filename
import sqlite3
from flask_mail import Message, Mail
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = r'/home/carlos/projects/projeto-final/static/upload2'

# Configuração do Flask-Mail

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'portal.app.uminho@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'portal.app.uminho@gmail.com'

# Inicializar o objeto Mail
mail = Mail()

# Inicializar a extensão Flask-Mail
mail.init_app(app)


class LogForm(FlaskForm):
    mail = EmailField("Email: ", validators=[Email(), DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("login")


DATABASE = '/home/carlos/projects/projeto-final/database.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()

    if request.method == 'POST':
        email = request.form.get('email')

        # Verificar se o email existe na base de dados

        c.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        user = c.fetchone()
        
        if not user:
            flash('Mail não registrado no site', category="error" )
            return redirect(url_for('login'))

        if user:
            # Gerar token de redefinição de senha
            token = ''.join(random.choice(string.ascii_uppercase +
                            string.ascii_lowercase + string.digits) for _ in range(32))

            # Atualizar o token de redefinição de senha na base de dados

            c.execute(
                "UPDATE usuarios SET reset_password_token=? WHERE email=?", (token, email))
            db.commit()
            db.close()

            # Enviar e-mail de redefinição de senha
            msg = Message('Redefinição de senha', recipients=[email])
            msg.html = render_template(
                'reset_password_email.html', user=user, token=token)
            mail.send(msg)

        flash('Foi enviado um e-mail com instruções para redefinir a senha.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', posts=posts)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    # Verificar se o token existe na base de dados
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM usuarios WHERE reset_password_token=?", (token,))
    user = c.fetchone()

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()

    if not user:
        flash('Token inválido ou expirado.', category='error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('As senhas não coincidem. Tente novamente.', category='error')
            return redirect(url_for('reset_password_confirm', token=token))

        # Hash da nova senha
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Atualizar a senha e o token de redefinição de senha na base de dados

        c.execute("UPDATE usuarios SET senha=?, reset_password_token=? WHERE id=?",
                  (password_hash, None, user[0]))
        db.commit()
        db.close()

        flash('A senha foi redefinida com sucesso.')
        return redirect(url_for('login'))

    return render_template('reset_password_confirm.html', token=token, posts=posts)


@app.route("/login/", methods=['GET', 'POST'])
def login():

    db = get_db()
    c = db.cursor()

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        c.execute('SELECT * FROM usuarios WHERE email=?', (email,))
        user = c.fetchone()

        c.execute("SELECT * FROM posts")
        posts = c.fetchall()

        if user:
            hash_senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            if hash_senha == user[3]:
                session['email'] = user[2]
                session['tipo'] = user[4]
                session['id_user'] = user[0]
                return redirect(url_for('home'))
            else:
                flash('Senha incorreta', category='error')
                return render_template('login.html', can_edit=False, posts=posts)
        else:
            flash('E-mail não encontrado!', category='error')
            return render_template('login.html', can_edit=False, posts=posts)
    else:

        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        db.close()
        return render_template('login.html', can_edit=False, posts=posts)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('tipo', None)
    return redirect(url_for('home', can_edit=False))


@app.route("/")
def home():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM forms")
    forms = c.fetchall()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()
    return render_template("index.html", can_edit=False, forms=forms, posts=posts)


@app.route("/menu")
def menu():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    c.execute("SELECT * FROM forms")
    forms = c.fetchall()
    db.close()
    return render_template("menu.html", can_edit=False, posts=posts, forms=forms)


@app.route("/sabermais/")
def sabe():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()
    return render_template("sabermais.html", can_edit=False, forms=forms, posts=posts)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!", category='error')
        return redirect("/")

    # Conectar à base de dados
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.files['download']
        file = request.files["file"]
        subject = request.form['subject']

        if download:
            filename = secure_filename(download.filename)
            download_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            download.save(download_path)
            download_url = download_path
        else:
            download_url = None

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

        # Inserir dados na tabela de postagens
        c.execute("INSERT INTO posts (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download,subject) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, content, thumbnail_url, file_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, links, download_url, subject))

        db.commit()

        flash("Post criado com sucesso", category='success')
        return redirect("menu")

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()
    return render_template("new_post.html", can_edit=False, forms=forms, posts=posts)


@app.route("/post/<int:post_id>")
def post(post_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()

    can_edit = False
    if 'email' in session and session['tipo'] == 'admin':
        can_edit = True

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()

    return render_template("post.html", post=post, can_edit=can_edit, forms=forms, posts=posts)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!", category='error')
        return redirect("/")

    can_edit = False
    if 'email' in session and session['tipo'] == 'admin':
        can_edit = True

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()

    # Colocar as variáveis a None caso não haja valores

    thumbnail_url = post[3] if post[3] else None
    file_url = post[4] if post[4] else None
    links = post[9] if post[9] else None

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.files['download']
        file = request.files["file"]
        subject = request.form['subject']

        if download:
            filename = secure_filename(download.filename)
            download_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            download.save(download_path)
            download_url = download_path
        else:
            download_url = None

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

        if links:
            # Atualizar links
            c.execute("UPDATE posts SET links=? WHERE id=?", (links, post_id))

         # Atualizar demais informações do post
        c.execute("UPDATE posts SET title=?, content=?, thumbnail_url=?, author=?, snapshots_1=?, snapshots_2=?, snapshots_3=?, file_url=?,download=?,subject=? WHERE id=?",
                  (title, content, thumbnail_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, file_url, download_url, subject, post_id))
        db.commit()
        flash("Post editado com sucesso", category='success')
        return redirect(url_for("menu", post_id=post_id))

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()
    return render_template("edit_post.html", post=post, can_edit=can_edit, forms=forms, posts=posts)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    db = get_db()
    c = db.cursor()

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']
        nome = request.form['nome']

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
        db.commit()

        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        flash('Conta criada com sucesso', category='success')
        return render_template('index.html', posts=posts)
    else:

        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        db.close()
        return render_template('register.html', posts=posts)


@app.route('/new-form', methods=['GET', 'POST'])
def form():
    if 'email' not in session:
        flash("Acesso negado!", category='error')
        return redirect("/")
    
    # Conectar à base de dados
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        thumbnail = request.files['thumbnail']
        author = request.form['author']
        snapshots_1 = request.files['snapshots_1']
        snapshots_2 = request.files['snapshots_2']
        snapshots_3 = request.files['snapshots_3']
        links = request.form['links']
        download = request.files['download']
        file = request.files["file"]
        subject = request.form['subject']

        if download:
            filename = secure_filename(download.filename)
            download_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            download.save(download_path)
            download_url = download_path
        else:
            download_url = None

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

        # Inserir dados na tabela de postagens
        c.execute("INSERT INTO forms (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download,subject) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?)",
                  (title, content, thumbnail_url, file_url, author, snapshots_1_url, snapshots_2_url, snapshots_3_url, links, download_url, subject))

        db.commit()

        flash("Post submetido com sucesso", category='success')
        return redirect("/")

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()

    return render_template('formulario.html', forms=forms, posts=posts)


@app.route('/admin_page/<int:admin_id>', methods=['GET', 'POST'])
def admin(admin_id):
    if 'email' not in session or session['tipo'] != 'admin' or session['id_user'] != admin_id:
        flash("Acesso negado!", category='error')
        return redirect("/")

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM usuarios WHERE id=?", (admin_id,))
    usuario = c.fetchone()

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()

    return render_template('admin_page.html', usuario=usuario, forms=forms, posts=posts)


@app.route("/form/<int:form_id>")
def forms(form_id):

    if 'email' not in session or session['tipo'] != 'admin':
        flash("Acesso negado!", category='error')
        return redirect("/")

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM forms WHERE id=?", (form_id,))
    post = c.fetchone()

    c.execute("SELECT * FROM forms")
    forms = c.fetchall()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()

    return render_template("form.html", post=post, can_edit=False, forms=forms, posts=posts)


@app.route("/delete", methods=["POST"])
def delete():
    form_id = request.form.get('form_id')
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM forms WHERE id=?", (form_id,))
    db.commit()

    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    db.close()
    return redirect(url_for('home', can_edit=False, posts=posts))


@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    db.commit()
    db.close()
    flash('Post apagado com sucesso', category='success')
    return redirect(url_for('menu', can_edit=False))


@app.route('/approved', methods=['POST'])
def approved():
    if request.method == "POST":
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
        subject = request.form['subject']

        # Conectar à base de dados
        db = get_db()
        c = db.cursor()

    # Inserir os valores do formulário na base de dados "posts"
    c.execute('''INSERT INTO posts(title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download, created_at, subject) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (title, content, thumbnail_url, file_url, author, snapshots_1, snapshots_2, snapshots_3, links, download, created_at, subject))

    # Remover os valores do formulário da base de dados "forms"
    c.execute('''DELETE FROM forms WHERE id = ?''', (post_id,))

    # Salvar as mudanças e fechar a conexão com a base de dados
    db.commit()
    db.close()

    return redirect('/')


@app.route('/download', methods=['POST'])
def download():
    if request.method == "POST":
        download = request.form['download']

    file = os.path.basename(download)
    caminho_arquivo = os.path.join(app.config["UPLOAD_FOLDER"], download)
    return send_file(caminho_arquivo, as_attachment=True, download_name=file)


if __name__ == "__main__":
    app.run(debug=True)
