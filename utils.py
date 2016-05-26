from passlib.hash import sha512_crypt
import mongo, smtplib, datetime, logging, atexit, email
from email.mime.application import MIMEApplication #for some reason, MIMEApplication can't be accessed from email
from apscheduler.scheduler import Scheduler

##creates new user account
def createUser(uname, pword, atype):
    user = mongo.getEntry("modelun","users",{"username":uname})
    if user is None:
        mongo.addEntry("modelun","users",{"username":uname,
                                          "password":sha512_crypt.encrypt(pword),
                                          "type":atype})

## checks if the username/password/accounttype combination is correct
def pwordAuth(uname, pword, atype):
    user = mongo.getEntry("modelun","users",{"username":uname,"type":atype})
    return user is not None and sha512_crypt.verify(pword,user["password"])

## sign up to attend a conference
def attendConference(conferenceid):
    pass

## email blasts
## requires gmail account, as well as the user to allow less secure apps
## on the account settings
def emailUser(username, password, receiver, subject, message, attachments):
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(username, password)
    msg = email.MIMEMultipart.MIMEMultipart()
    msg["From"]=username
    msg["To"]=",".join(receiver)
    msg["Subject"]=subject
    msg.attach(email.MIMEText.MIMEText(message,"plain"))
    if attachments:
        msg.attach(MIMEApplication(attachments))
    smtpserver.sendmail(username, receiver, msg.as_string())
    smtpserver.quit()

## allows the admin to specify a time for a notification
## email gets sent out to all members of a specified collection
def scheduleNotification(username, password, receivers, subject, message, attachments, timestring):
    logging.basicConfig() #for some reason necessary for apscheduler
    scheduler = Scheduler()
    scheduler.start()
    sentOn = datetime.datetime.strptime(timestring,"%Y-%m-%dT%H:%M")
    print attachments
    scheduler.add_date_job(emailUser,sentOn,[username,password,receivers.split(","),subject,message,attachments])
    atexit.register(lambda:scheduler.shutdown(wait=False))
    #sean vieira, stackoverflow, shuts down scheduler when app is closed
