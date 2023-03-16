from flask import Flask, redirect,request, url_for, render_template, send_file,flash
import sys
from appc import is_continuous_at, create_function
import sympy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import plotly.graph_objs as go
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import io
import base64
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

@app.route("/continuidade/", methods = ["POST", "GET"])
def continuidade():
    if request.method == "POST":
        func = request.form["fn"]
        ponto = request.form["pt"]
        
        func = sympy.sympify(func)
        func = sympy.lambdify('x',func)
         
        ponto = float(ponto)
        
        if is_continuous_at(func,ponto):
            flash("é continua", "info")
        else:
            flash("nao é continua", "info")

        x_values = np.linspace(ponto - 10, ponto + 10, 1000)
        y_values = create_function(func, x_values)

        trace = go.Scatter(x=x_values, y=y_values)
        layout = go.Layout(title="Gráfico da função", xaxis=dict(title="x"), yaxis=dict(title="y"))
        fig = go.Figure(data=[trace], layout=layout)
        fig.show()
        
        
        return render_template("/continuidade.html")
    else:
        return render_template("/continuidade.html")

@app.route('/interactive-graphic')
def interactive_graphic():
    # Define the data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Get the slider value from the request object
    freq = float(request.args.get('freq', 1.0))

    # Create the plot
    fig, ax = plt.subplots()
    line, = ax.plot(x, np.sin(freq * x))

    # Add interactivity
    def update(val):
        print('update called')
        # Get the slider value
        freq = s_freq.val
        
        # Update the plot
        line.set_ydata(np.sin(freq * x))
        fig.canvas.draw_idle()

    # Create a slider
    ax_freq = plt.axes([0.1, 0.1, 0.8, 0.05])
    s_freq = Slider(ax_freq, 'Frequency', 0.1, 10.0, valinit=freq)
    s_freq.on_changed(update)


    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # Convert the plot to an image
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    
    # Generate the HTML code for the plot
    html = f'<img id="plot" src="send_file(buffer, mimetype=''image/png'')" />'

    # Render the template with the HTML code for the plot
    return render_template('interactive-graphic.html', html=html)

@app.route('/plot/<float:freq>')
def plot_im(freq):
    # Define the data
    x = np.linspace(0, 10, 100)
    y = np.sin(freq * x)

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # Convert the plot to an image
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Return the image as a response
    return send_file(buffer, mimetype='image/png')

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