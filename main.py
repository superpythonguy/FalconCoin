VER = "0.1"

import socket, threading, time, random, hashlib, math, datetime, sys, os, json
from minereg import LMTB
from pathlib import Path

Randrop_amount = 1.5 # FLC

def ServerLog(whattolog):
    now = datetime.datetime.now()
    now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
    print(now + whattolog)
    
def randdrop():
    winner =  random.choice(os.listdir("balance"))
    ServerLog(winner+" Has Won AirDrop!")
    with open("balance/"+winner,"r+") as fe:
        currentbal = fe.readline()
        newbal = float(currentbal) + float(Randrop_amount)
        fe.seek(0)
        fe.write(str(newbal))
        fe.truncate()
        fe.close() 
    threading.Timer(600,randdrop).start()

def UpdateServerInfo():
    global server_info, hashrates
    #Nulling pool hashrate stat
    server_info['pool_hashrate'] = 0
    #Counting registered users
    server_info['users'] = len(os.listdir('users'))
    #Addition miners hashrate and update pool's hashrate
    for hashrate in hashrates:
        server_info['pool_hashrate'] += hashrates[hashrate]["hashrate"]
    #Preparing json data for API
    data = {"pool_miners" : server_info["miners"], "pool_hashrate" : server_info["pool_hashrate"], "users" : server_info["users"], "miners" : {}}
    #Adding mining users to API's json
    for hashrate in hashrates:
        data["miners"][hashrate] = hashrates[hashrate]
    #Writing json data to API
    with open("info/api.json", "w") as fJson:
        json.dump(data, fJson, indent=4)
    #Wait 5 seconds and repeat
    threading.Timer(5, UpdateServerInfo).start()    

class ClientThread(threading.Thread): #separate thread for every user
    def __init__(self, ip, port, clientsock):
        self.thread_id = str(threading.get_ident())
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsock = clientsock
        ServerLog("New thread started (" + self.thread_id + ")")

    def run(self):
        global server_info, hashrates
        ServerLog("Connection from : " + self.ip + ":" + str(self.port))
        
        #### API stuff
        thread_id = str(threading.current_thread().ident)
        server_info['miners'] += 1
        
        while True:
            data = self.clientsock.recv(1024).decode()
            data = data.split(",")
            if data[0] == "REGI": #registration
                username = data[1]
                password = data[2]
                ServerLog("Client request account registration.")
                if not Path("users/"+username + ".txt").is_file(): #checking if user already exists
                    file = open("users/"+username + ".txt", "w")
                    file.write(password)
                    file.close()
                    file = open("balance/"+username + "balance.txt", "w")
                    file.write(str(new_users_balance))
                    file.close
                    self.clientsock.send(bytes("OK", encoding='utf8'))
                    ServerLog("New user (" + username + ") registered")
                else:
                    ServerLog("Account already exists!")
                    self.clientsock.send(bytes("NO", encoding='utf8'))
                    break
            elif data[0] == "LOGI": #login
                username = data[1]
                password = data[2]
                ServerLog("Client request logging in to account " + username)
                if Path("users/"+username + ".txt").is_file():
                    file = open("users/"+username + ".txt", "r")
                    data = file.readline()
                    file.close()
                    if password == data:
                        self.clientsock.send(bytes("OK", encoding='utf8'))
                        ServerLog("Password matches, user logged")
                    else:
                        ServerLog("Incorrect password")
                        self.clientsock.send(bytes("NO", encoding='utf8'))
                else:
                    ServerLog("User doesn't exist!")
                    self.clientsock.send(bytes("NO", encoding='utf8'))
                    
            elif username != "" and data[0] == "JOB": #main, mining section
                
                #ServerLog("New job for user: " + username)
                with locker:
                    file = open("info/blocks.txt", "r")
                    blocks = int(file.readline())
                    file.close()
                    file = open("info/lastblock.txt", "r+")
                    lastblock = file.readline()
                    diff = math.ceil(blocks / (diff_incrase_per*len(os.listdir("users"))))
                    rand = random.randint(0, 10000 * (diff))
                    hashing = hashlib.sha3_512(str(lastblock + str(rand)).encode("utf-8"))
                    #ServerLog("Sending target hash: " + hashing.hexdigest())
                    self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
                    file.seek(0)
                    file.write(hashing.hexdigest())
                    file.truncate()
                    file.close()
                response = self.clientsock.recv(1024).decode()
                if response.find(",") != -1:
                    try:
                        response = response.split(",")
                        result = response[0]
                        timeelapsed = response[2]
                        hashrates[thread_id] = {"username" : username, "hashrate" : 0}
                        hashrates[thread_id]["hashrate"] = int(response[1])
                        hashrates[thread_id]["timeelapsed"] = int(response[2])
                    except:
                        pass
                else:
                    try:
                        result = response
                        hashrates[thread_id]["hashrate"] = 1000 #1kH/s if none submitted
                    except:
                         pass
                if result == str(rand):
                    #ServerLog("Recived good result (" + str(result) + ")")
                    with locker:
                        global balance,reward
                        file = open("balance/"+username + "balance.txt", "r+")
                        balance = float(file.readline())
                        # Basic help for new users
                        # And current reward system
                        # Will change in future to incorperate hashrates into aswell
                        # TODO: Add a 'miner bonus' like if you have multiple devices or have mined for a while(1 day?)
                        bonus=LMTB(hashrates[thread_id]["timeelapsed"],username)
                        if balance < 50:
                            reward = (0.0009 + bonus)
                        else:
                            if balance < 100:
                                reward = (0.00009 + bonus)
                            else:
                                if balance < 200:
                                    reward = (0.000009 + bonus)
                                else:
                                    reward = (0.0000009 + bonus)
                        bal = float(balance) + float(reward)
                        file.seek(0)
                        file.write(str(bal))
                        file.truncate()
                        file.close()
                    self.clientsock.send(bytes("GOOD", encoding="utf8"))
                    with locker:
                        blocks+= 1
                        file = open("info/blocks.txt", "w")
                        file.seek(0)
                        file.write(str(blocks))
                        file.truncate()
                        file.close()
                else:
                    ServerLog("Recived bad result (" + str(result) + ")")
                    self.clientsock.send(bytes("BAD", encoding="utf8"))
                    
            elif username != "" and data[0] == "BALA": #check balance section
                ServerLog("Client request balance check")
                file = open("balance/"+username + "balance.txt", "r")
                balance = file.readline()
                file.close()
                self.clientsock.send(bytes(balance, encoding='utf8'))

            elif username != "" and data[0] == "SEND": #sending funds section
                sender = data[1]
                reciver = data[2]
                amount = float(data[3])
                ServerLog("Client request transfer funds")
                #now we have all data needed to transfer money
                #firstly, get current amount of funds in bank
                try:
                    file = open("balance/"+sender + "balance.txt", "r+")
                    balance = float(file.readline())
                except:
                    ServerLog("Can't checks sender's (" + sender + ") balance")
                #verify that the balance is higher or equal to transfered amount
                if amount > balance:
                    self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
                else: #if ok, check if recipient address exists
                    if Path("balance/"+reciver + "balance.txt").is_file():
                        #it exists, now -amount from sender and +amount to reciver
                        try:
                            #remove amount from senders' balance
                            balance -= amount
                            file.seek(0)
                            file.write(str(balance))
                            file.truncate()
                            file.close
                            #get recipients' balance and add amount
                            file = open("balance/"+reciver+"balance.txt", "r+")
                            reciverbal = float(file.readline())
                            reciverbal += amount
                            file.seek(0)
                            file.write(str(reciverbal))
                            file.truncate()
                            file.close()
                            self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
                            ServerLog("Transferred " + str(amount) + " FLC from " + sender + " to " + reciver)
                        except:
                            self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
                    else: #message if recipient doesn't exist
                        ServerLog("The recepient", reciver, "doesn't exist!")
                        self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
                        
            elif username != "" and data[0] == "NEWS":
                    self.clientsock.send(bytes(News,encoding='utf8'))
            
            elif username != "" and data[0] == "SERINFO":
                self.clientsock.send(bytes("Miners: "+str(server_info["miners"])+"\n"+"Users: "+str(server_info["users"]),encoding='utf8'))

            elif username != "" and data[0] == "CLOSE":
                ServerLog("Client requested thread (" + thread_id + ") closing")
                time.sleep(0.5)
                try:
                    del hashrates[thread_id]
                    server_info["miners"] -= 1
                    self.clientsock.close()
                except:
                    print("Deleting thread did not work")

            
ServerLog("Falcon Coin v" + VER)
host = "10.9.80.42"
port = 5454
new_users_balance = 0
#reward = 0.00005
News = "Server and wallet has been deployed "

diff_incrase_per = 1000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    tcpsock.bind((host,port))
    ServerLog("Server started...")
except:
    ServerLog("Error during TCP socket...")
    time.sleep(5)
    sys.exit()

threads = []
server_info = {'miners' : 0, 'pool_hashrate' : 0, 'users' : 0}
hashrates = {}
locker = threading.Lock()

# Check files

if not Path("info/lastblock.txt").is_file():
    file = open("info/lastblock.txt", "w")
    file.write(hashlib.sha1(str("Falcon.COIN2022").encode("utf-8")).hexdigest())
    file.close()
if not Path("info/blocks.txt").is_file():
    file = open("info/blocks.txt", "w")
    file.write("0")
    file.close()
    
ServerLog("Listening for incoming connections...")
 

while True:
    try:
        tcpsock.listen(16)
        (conn, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port, conn)
        newthread.start()
        threads.append(newthread)
        UpdateServerInfo()
        #randdrop()
    except:
        print("Error in MainLoop!")

for t in threads:
    t.join()