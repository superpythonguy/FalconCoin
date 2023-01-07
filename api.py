from flask import Flask
import json, os
import requests

app = Flask(__name__)
    
with open("info/api.json","r") as f:
    data=json.load(f)    

@app.route("/")
def index():
    return("Welcome to Falcon Coin's Own API")
    
@app.route("/num/users")
def numofusers():
    with open("info/api.json","r") as f:
            data = json.load(f)
            return str(data["users"])
    
@app.route("/FLC_in_Circulation")
def in_circulation():
    return  GetcirculatingFLC()

@app.route("/user/<username>")
def search(username):
    try:
        with open("balance/"+username+"balance"+".txt","r") as f:
            bal=f.readline()
            f.close()
        return username +" has "+bal+" FLC"
    except:
        return "User not found pleae retype Username!"

@app.route("/user/raw/<username>")
def searchraw(username):
    try:
        with open("balance/"+username+"balance"+".txt","r") as f:
            bal=f.readline()
            f.close()
        return bal
    except:
        return "User not found pleae retype Username!"
    
@app.route("/miners")
def miners():
    with open("info/api.json","r") as fe:
        dataa=json.load(fe)
    return dataa["miners"]

@app.route("/num/allusers")
def usersnum():
    return str(data["users"])

@app.route("/allusers")
def userslist():
    for files in os.listdir("users/"):
        filesstriped=files.rsplit(".txt")
    return str(filesstriped)

######################################################

def GetcirculatingFLC():
    global FLC_Mined
    for filename in os.listdir("balance/"): # All-time mined FLC
        if filename.endswith(".txt"):
            try:
                with open("balance/"+filename) as f:
                    
                    FLC_Mined = float(f.read())
                    continue
            except:
                continue
            else:
                continue
    return str(FLC_Mined)

app.run(port=5354)