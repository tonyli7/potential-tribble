import mongo, smtplib, datetime, logging, atexit, email, imaplib
from passlib.hash import sha512_crypt
from email.mime.application import MIMEApplication 
from email.parser import HeaderParser
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
    user = mongo.getEntry("modelun","attendees",{"email":email})

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
    #when no value is assigned to msg['To'], those named as receivers in sendmail are bcc'ed
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
    logging.basicConfig() #for some reason necessary for apscheduler
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

def scheduleEmailListener(username,password,response_subject,automated_response):
    logging.basicConfig()
    scheduler=Scheduler()
    scheduler.start()
    scheduler.add_interval_job(respondToEmails,minutes=5,args=[username,password,response_subject,automated_response])
    atexit.register(lambda:scheduler.shutdown(wait=False))

class EventNode():
    def __init__(self,event,description,start,end,next_node):
        self.data={"event":event,"description":description,"start":start,"end":end}
        self.next_node=next_node
    def getData(self,data):
        return data
    def getField(self,field):
        return data[field]
    def getNext(self):
        return self.next_node
    def setData(self,data):
        self.data=data
    def setField(self,field,value):
        self.data[field]=value
    def setNext(self,next_node):
        self.next_node=next_node

schedule = None

def addEvent(schedule,event,description,start,end):
    print schedule
    if schedule == None:
        schedule = EventNode(event,description,start,end,schedule)
    else:
        while schedule.getNext() != None and schedule.getNext().getStart()> start:
            schedule=schedule.getNext()
        event = EventNode(event,description,start,end,schedule.getNext())
        schedule.setNext(event)
    print schedule
    
def printSchedule(schedule):
    while schedule != None:
        print schedule.getData()
        schedule = schedule.getNext()

    
