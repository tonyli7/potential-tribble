from passlib.hash import sha512_crypt
import mongo
import smtplib

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

##email blasts
##requires gmail account, as well as the user to allow less secure apps
##on the account settings
def emailUser(username, password, receiver, subject, message):
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(username, password)
    message = "To: {}\nFrom: {}\nSubject: {}\n".format(receiver,username,subject)
    message += '\n this is test msg  \n\n'
    smtpserver.sendmail(username, receiver, message)
    smtpserver.close()

