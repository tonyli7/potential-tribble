import utils
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")



if __name__ == "__main__":
    app.debug = True
    app.run()
