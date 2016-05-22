from passlib.hash import sha512_crypt
import mongo

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
