from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/criadores/")
def criadores():
    return render_template("creatores.html")

@app.route("/continuidade/")
def continuidade():
    return render_template("continuidade.html")

@app.route("/result_cont/",methods = ['POST'])
def result():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


