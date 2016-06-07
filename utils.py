import mongo, smtplib, datetime, logging, atexit, email, imaplib
from passlib.hash import sha512_crypt
from email.mime.application import MIMEApplication 
from email.parser import HeaderParser
from apscheduler.scheduler import Scheduler
from bs4 import BeautifulSoup
from bson.objectid import ObjectId

## creates new user account
def createUser(uname, pword, atype):
    user = mongo.getEntry("modelun","users",{"email":uname})
    if user.count() == 0:
        mongo.addEntry("modelun","users",{"email":uname,"password":sha512_crypt.encrypt(pword),"atype":atype})

## checks if the username/password/accounttype combination is correct
def pwordAuth(uname, pword, atype):
    user = mongo.getEntry("modelun","users",{"email":uname,"type":atype})
    return user is not None and sha512_crypt.verify(pword,user["password"])

## sign up to attend a conference as advisor or delegate
def attendConference(role,required_fields):
    print role
    print required_fields
    user = mongo.addEntry("modelun",role,required_fields)

## sign up as an interested party
def mailinglist(email):
    interested = {"email":email}
    if mongo.getEntry("modelun","interested",interested).count() == 0:
        mongo.addEntry("modelun","interested",interested)

## get database collection
def getCollection(collection):
    return mongo.getEntry("modelun",collection,{})

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
    msg["Subject"]=subject
    msg.attach(email.MIMEText.MIMEText(message,"plain"))
    for attachment in attachments:
        att = MIMEApplication(attachment[1])
        att.add_header("Content-Disposition","attachment",filename=attachment[0])
        msg.attach(att)
    smtpserver.sendmail(username, receiver, msg.as_string())
    smtpserver.quit()

## allows the admin to specify a time for a notification
## email gets sent out to all members of a specified collection
def scheduleNotification(username, password, receivers, subject, message, attachments, timestring):
    logging.basicConfig()
    scheduler = Scheduler()
    scheduler.start()
    sentOn = datetime.datetime.strptime(timestring,"%Y-%m-%dT%H:%M")
    scheduler.add_date_job(emailUser,sentOn,[username,password,receivers.split(","),subject,message,attachments])
    atexit.register(lambda:scheduler.shutdown(wait=False))
    #sean vieira, stackoverflow, shuts down scheduler when app is closed

#checks for unseen emails and sends an automated response
def respondToEmails(username,password,response_subject,automated_response):
    conn = imaplib.IMAP4_SSL("imap.gmail.com")
    status,user = conn.login(username,password)
    if status == 'OK':
        status,numMessages = conn.select("INBOX")
        if status == 'OK':
            status,messages = conn.search(None,"(UNSEEN)")
            messages = messages[0].split()
            if len(messages) > 0:
                recipients=[]
                parser = HeaderParser()
                for msg_id in messages:
                    status,data = conn.fetch(msg_id,'(BODY[HEADER.FIELDS (FROM)])')
                    response = parser.parsestr(data[0][1])
                    recipients.append(response["From"])
                    conn.store(msg_id,'+FLAGS','\Seen')
                smtpserver = smtplib.SMTP("smtp.gmail.com",587)
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo()
                smtpserver.login(username, password)
                response = email.MIMEMultipart.MIMEMultipart()
                response["From"]=username
                response["Subject"]=response_subject
                response.attach(email.MIMEText.MIMEText(automated_response,"plain"))
                smtpserver.sendmail(username,recipients,response.as_string())
                smtpserver.quit()
    conn.close()

#sets up a listener to connect to the specified email every five minutes and respond to any unread mail with the automated response
def scheduleEmailListener(username,password,response_subject,automated_response):
    logging.basicConfig()
    scheduler=Scheduler()
    scheduler.start()
    scheduler.add_interval_job(respondToEmails,minutes=5,args=[username,password,response_subject,automated_response])
    atexit.register(lambda:scheduler.shutdown(wait=False))

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
    
#add event to schedule
def addEvent(event,description,start,end):
    startDate = datetime.datetime.strptime(start,"%Y-%m-%dT%H:%M")
    endDate = datetime.datetime.strptime(end,"%Y-%m-%dT%H:%M")
    mongo.addEntry("conference","schedule",{"event":event,"description":description,"start":startDate,"end":endDate})

#get schedule
def getEvents():
    return mongo.getEntry("conference","schedule",{}).sort("start")

#delete events
def deleteEvents(item_ids):
    object_ids = [ObjectId(item_id) for item_id in item_ids]    
    mongo.deleteEntry("conference","schedule",{"_id": {"$in": object_ids}})

#delete specified users
def deleteEntries(item_ids):
    object_ids = [ObjectId(item_id) for item_id in item_ids]    
    mongo.deleteEntry("modelun","users",{"_id": {"$in": object_ids}})
    mongo.deleteEntry("modelun","advisor",{"_id": {"$in": object_ids}})
    mongo.deleteEntry("modelun","delegate",{"_id": {"$in": object_ids}})

#delete fields
def deleteFields(item_ids):
    object_ids = [ObjectId(item_id) for item_id in item_ids]
    mongo.deleteEntry("fields","delegate",{"_id": {"$in": object_ids}})
    mongo.deleteEntry("fields","advisor",{"_id": {"$in": object_ids}})

#add fields
def addField(usertype,fieldname):
    query = {"field":fieldname}
    if mongo.getEntry("fields",usertype,query).count() == 0:
        mongo.addEntry("fields",usertype,query)
    
