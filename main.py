from flask import Flask, redirect,request, url_for, render_template
import sys
from appc import is_continuous_at, create_function
import sympy
import numpy as np
import plotly.graph_objs as go

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/criadores/")
def criadores():
    return render_template("creatores.html")

@app.route("/continuidade/", methods = ["POST", "GET"])
def continuidade():
    if request.method == "POST":
        func = request.form["fn"]
        ponto = request.form["pt"]
        
        func = sympy.sympify(func)
        func = sympy.lambdify('x',func)
         
        ponto = float(ponto)
        
        if is_continuous_at(func,ponto):
            print("é continua")
        else:
            print("nao é continua")

        x_values = np.linspace(ponto - 10, ponto + 10, 1000)
        y_values = create_function(func, x_values)

        trace = go.Scatter(x=x_values, y=y_values)
        layout = go.Layout(title="Gráfico da função", xaxis=dict(title="x"), yaxis=dict(title="y"))
        fig = go.Figure(data=[trace], layout=layout)
        fig.show()
        
        return render_template("/continuidade.html")
    else:
        return render_template("/continuidade.html")

@app.route("/<usr>")
def func(usr):
    return f"<h1>{usr}</h1>"


if __name__ == "__main__":
    app.run(debug=True)
