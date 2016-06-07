import utils, mongo, os, settings
from werkzeug.utils import secure_filename
from flask import Flask, session, render_template, url_for, request, redirect, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods = ['GET','POST'])
def login():
    if session.keys().count("loggedin") == 0:
        if request.method == 'POST':

            if request.form['email'] and request.form['pwd']:

                email = request.form['email']
                pwd = request.form['pwd']

                if utils.pwordAuth(email,pwd,"admin"):
                    session["loggedin"] = email
                    return render_template("home.html")
                else:
                    return render_template("login.html", failure="email/password combination does not exist.")
        else:
            return render_template("login.html")
    else:
        return redirect(url_for("home"))


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
        #schedule the email
        if 'schedule-email' in request.form:
            rcpts=""
            if request.form["recipient-category"]:
                entries = mongo.getEntry("modelun",request.form["recipient-category"],{})
                for entry in entries:
                    if "email" in entry:
                        rcpts+=entry["email"]+","
            file_bins=[]
            if request.files['attachment']:
                files = request.files.getlist('attachment')
                file_bins = [(attachment.filename,attachment.read()) for attachment in files]
            utils.scheduleNotification(request.form['email'],request.form['password'],rcpts+request.form['recipients'],request.form['subject'],request.form['message'],file_bins,request.form['time'])

        #set the automatic reply
        if 'set-reply' in request.form:
            utils.scheduleEmailListener(request.form['email'],request.form['password'],request.form['subject'],request.form['response'])
            
        #upload a file to gallery
        if 'upload-file' in request.form:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save("."+os.path.join(app.config['UPLOAD_FOLDER'],filename))
                return redirect(url_for('uploaded_file',filename=filename))

        #edit schedule
        if 'edit-schedule' in request.form:
            utils.addEvent(request.form['event'],request.form['description'],request.form['start'],request.form['end'])
            
    return render_template("admin.html",entries=utils.getCollection("users"),collections=mongo.getCollections("modelun"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        text = request.form['about']       
        utils.updateAbout(text)
        return render_template("edit.html")
    else:
        return render_template("edit.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS
    
@app.route(app.config['UPLOAD_FOLDER']+'/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route("/schedule",methods=["GET","POST"])
def schedule():
    if request.method == "POST":
         delete = request.form.getlist('delete-event')
         utils.deleteEvents(delete)
    return render_template("schedule.html",schedule=utils.getEvents())

if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000, use_reloader=False)
