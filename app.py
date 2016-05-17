import utils
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods = ["POST"])
def login():
    ## Login template will have a link to register
    if str(request.form["button"]) == "Log in":
        username = str(request.form["username"])
        ## User logs in by checking off account type (student or advisor), inputing uname and pword
        if utils.pwordAuth(username, str(request.form["password"]), request.form["accounttype"]):
            return render_template("/home.html")
        else:
            return render_template("/login.html", text = "Username and password do not match")


if __name__ == "__main__":
    app.debug = True
    app.run()
