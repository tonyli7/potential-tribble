import utils
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

"""
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

"""
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
        return render_template("/register.html")
    """
    if str(request.form["button"]) == "Register":
        # Look for and check for completeness of information
        if True ""info is complete"":
            return render_template("/home.html")
        else:
            return render_template("/register.html", text = "Missing required fields")
    """
    
if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000)
