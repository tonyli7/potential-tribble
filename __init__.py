import utils, mongo, os, settings, datetime
from werkzeug.utils import secure_filename
from flask import Flask, session, render_template, url_for, request, redirect, send_from_directory
from flask.ext.session import Session, MongoDBSessionInterface

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.config['SESSION_TYPE'] = settings.SESSION_TYPE
email_receiver=[]
"""
def setup(app):
    utils.createUser("admin@stuymunc.com","proscientia","admin")
    Session(app)
    
setup(app)
"""
Session(app)
@app.route("/")
@app.route("/home")
def home():
    start=mongo.getEntry("fields","start-time",{})
    countto= "2000-1-1T0:0"
    if start.count() > 0:
        countto=start[0]["time"]
    countto = datetime.datetime.strptime(countto,"%Y-%m-%dT%H:%M")
    return render_template("home.html",user=session.get("loggedin"),year=countto.year,month=countto.month,day=countto.day,hour=countto.hour,minute=countto.minute,schedule=utils.getEvents())


@app.route("/login", methods = ['GET','POST'])
def login(): 
    if session.get("loggedin") == None:
        if request.method == 'POST':
            if request.form['email'] and request.form['pwd']:
                email = request.form['email']
                pwd = request.form['pwd']
                if utils.pwordAuth(email,pwd,"admin"):
                    session["loggedin"]=email
                    session["id"]=utils.newSession(email)
                    return redirect(url_for("home"))
                else:
                    return render_template("login.html", failure="email/password combination does not exist.")
        else:
            return render_template("login.html")
    else:
        return redirect(url_for("home"))

@app.route("/logout", methods=['GET','POST'])
def logout():
    utils.delSession(session["id"])
    session["loggedin"]=None
    session["id"]=None
    return redirect(url_for("home"))

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        attendee={}
        for attribute in request.form:
            if attribute != "submit":
                attendee[attribute]=request.form[attribute]
        utils.attendConference(request.form["submit"],attendee)
        return render_template("register.html", success="You've successfully registered!",advisor_fields=mongo.getEntry("fields","advisor",{}),delegate_fields=mongo.getEntry("fields","delegate",{}))
    else:
        return render_template("register.html",user=session.get("loggedin"),advisor_fields=mongo.getEntry("fields","advisor",{}),delegate_fields=mongo.getEntry("fields","delegate",{}))

    
@app.route("/admin", methods=['GET','POST'])
def admin():
    #if not utils.checkSession(session["loggedin"],session["id"]):
    #    return redirect(url_for("home"))
    if not user["loggedin"]:
        return redirect(url_for("home"))
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
            for receiver in email_receiver:
                receiver.shutdown(wait=False)
            email_receiver.append(utils.scheduleEmailListener(request.form['email'],request.form['password'],request.form['subject'],request.form['response']))
            
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
            
        #delete entry
        if 'delete-entries' in request.form:
            delete = request.form.getlist('delete-entry')
            utils.deleteEntries(delete)
            
        #edit schedule
        if 'delete-events' in request.form:
            delete = request.form.getlist('delete-event')
            utils.deleteEvents(delete)

        #edit fields
        if 'delete-fields' in request.form:
            delete = request.form.getlist('delete-field')
            utils.deleteFields(delete)

        #add fields
        if 'add-field' in request.form:
            utils.addField(request.form['user-type'],request.form['field-name'])

        #add admin
        if 'add-admin' in request.form:
            utils.createUser(request.form["admin-email"],request.form["admin-pass"],"admin")

        #set stumunc
        if 'set-stuymunc' in request.form:
            mongo.deleteEntry("fields","start-time",{})
            mongo.addEntry("fields","start-time",{"time":request.form["start-time"]})
        
    advisor_fields = mongo.getEntry("fields","advisor",{})
    advisor_header = [f['field'] for f in advisor_fields]
    advisor_fields.rewind()
    delegate_fields= mongo.getEntry("fields","delegate",{})
    delegate_header= [f['field'] for f in delegate_fields]
    delegate_fields.rewind()
    return render_template("admin.html",admins=utils.getCollection("users"),
                           delegate_headers=delegate_header,
                           delegates=utils.getCollection("delegate"),
                           advisor_headers=advisor_header,
                           advisors=utils.getCollection("advisor"),
                           interest=utils.getCollection("interest"),
                           collections=mongo.getCollections("modelun"),
                           schedule=utils.getEvents(),
                           advisor_fields=advisor_fields,
                           delegate_fields=delegate_fields,
                           user=session.get("loggedin"))


@app.route("/about")
def about():
    return render_template("about.html",user=session.get("loggedin"))

@app.route("/edit", methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        if request.form['about']:
            about_text = request.form['about']
            utils.updateAbout(about_text)
        
        if request.form['name'] and request.form['email']:

            name = request.form['name']
            email = request.form['email']
            contact_text = [name,email]
            utils.updateContact(contact_text)
              
        return render_template("edit.html",user=session.get("loggedin"))
    else:
        return render_template("edit.html",user=session.get("loggedin"))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS
    
@app.route('/files'+'static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route("/files")
def downloads():
    files = os.listdir("./static/uploads")
    imgs=[]
    docs=[]
    for i in files:
        if 'png' in i or 'jpg' in i or 'jpeg' in i or 'gif' in i:
            imgs.append(i)
        else:
            docs.append(i)

    return render_template("files.html", imgs=imgs,docs=docs,user=session.get("loggedin"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000, use_reloader=False)
