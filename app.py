import utils, os
from flask import Flask, render_template, request, send_from_directory
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'POST':

        if request.form['email'] and request.form['pwd']:

            email = request.form['email']
            pwd = request.form['pwd']

            if utils.pwordAuth(email,pwd,"admin"):
                return render_template("home.html")
            else:
                return render_template("login.html", failure="email/password combination does not exist.")
    else:
        return render_template("login.html")


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':

        if request.form['email'] and request.form['f_name'] and request.form['l_name'] and request.form['pwd']:
            email = request.form['email']
            f_name = request.form['f_name']
            l_name = request.form['l_name']
            pwd = request.form['pwd']

            utils.createUser(email, pwd, "admin")

            return render_template("register.html", success="You've successfully registered!")
        else:
            return render_template("register.html", success="You've left some fields empty")
    else:
        return render_template("register.html")

@app.route("/admin", methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        utils.scheduleNotification(request.form['email'],request.form['password'],request.form['recipients'],request.form['subject'],request.form['message'],request.files["attachment"],request.form['time'])
        return "SENT"
    else:
        return render_template("admin.html")

if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000)
