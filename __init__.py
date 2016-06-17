import utils, mongo, os, settings, datetime
from werkzeug.utils import secure_filename
from flask import Flask, session, render_template, url_for, request, redirect, send_from_directory
from flask.ext.session import Session, MongoDBSessionInterface

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.config['SESSION_TYPE'] = settings.SESSION_TYPE
email_receiver=[]

def setup(app):
    utils.createUser("admin@stuymunc.com","proscientia","admin")
    Session(app)
    
setup(app)
    
@app.route("/")
@app.route("/home")
def home():
    start=mongo.getEntry("fields","start-time",{})
    countto= "2000-1-1T0:0"
    if start.count() > 0:
        countto=start[0]["time"]
    countto = datetime.datetime.strptime(countto,"%Y-%m-%dT%H:%M")
    return render_template("home.html",user=session.get("loggedin"),year=countto.year,month=countto.month,day=countto.day,hour=countto.hour,minute=countto.minute,schedule=utils.getEvents())

if __name__=="__main__":
    app.debug = True
    app.secret_key="Don't upload to github"
    app.run(host='0.0.0.0', port=8000, use_reloader=False)
