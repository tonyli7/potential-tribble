import hashlib, mongo

## checks if the username/password/accounttype combination is correct
def pwordAuth(uname, pword, atype):
    user = mongo.getEntry("modelun","users",{"username":uname,
                                             "password":pword,
                                             "type":atype})
    return user.count() == 1
