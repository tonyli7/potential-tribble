import utils,mongo
from flask import Flask, render_template, request, session
from bs4 import BeautifulSoup

app = Flask(__name__)


def updateAbout(text):
    about = open("templates/about.html","r")
    t = about.read()
    soup = BeautifulSoup(t, 'html.parser')
    lines = t.split('\n')[:2]
    
    soup.p.replaceWith("<p>"+text+"</p>")
    #soup.p = "<p>"+text+"</p>"
    new = lines[0]+"\n"+lines[1]+"\n"+soup.get_text()
    about.close()
    
    about = open("templates/about.html","w")
    about.write(new)
    about.close()
    

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


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        
        text = request.form['about']
       
        updateAbout(text)
        return render_template("edit.html")
    else:
        return render_template("edit.html")
        
if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000)
