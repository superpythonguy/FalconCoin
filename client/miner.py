import socket, threading, time, hashlib, configparser, sys, platform, signal, statistics, random, datetime
from pathlib import Path

Time1 = time.time()

def hush(): # Hashes/sec calculation
	global last_hash_count, hash_count, khash_count, hash_mean
	
	last_hash_count = hash_count
	khash_count = last_hash_count / 1000
	if khash_count == 0:
		khash_count = random.uniform(0, 2)
		
	hash_mean.append(khash_count) # Calculate average hashrate
	khash_count = statistics.mean(hash_mean)
	khash_count = round(khash_count, 2)
	
	hash_count = 0 # Reset counter
	
	threading.Timer(1.0, hush).start() # Run this def every 1s

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
  now = datetime.datetime.now()
  print(now.strftime("\n%H:%M:%S ") + "SIGINT detected - Exiting gracefully. See you soon!")
  soc.send(bytes("CLOSE", encoding="utf8"))
  time.sleep(1)
  sys.exit()
    
shares = [0, 0]
last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []

config = configparser.ConfigParser()
os=platform.platform()
hush()

if not Path("config.ini").is_file():
    print("Initial configuration, you can edit 'config.ini' later\n")
    pool_address = input("Enter pool adddress (official: 92.5.61.219): ")
    pool_port = input("Enter pool port (official: 5454): ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    config['pool'] = {"address": pool_address,
    "port": pool_port,
    "username": username,
    "password": password}
    with open("config.ini", "w") as configfile:
        config.write(configfile)
else:
    config.read("config.ini")
    pool_address = config["pool"]["address"]
    pool_port = config["pool"]["port"]
    username = config["pool"]["username"]
    password = config["pool"]["password"]

while True:
    print("Connecting to pool...")
    soc = socket.socket()
    try:
        soc.connect((pool_address, int(pool_port)))
        print("Connected!")
        break
    except:
        print("Cannot connect to pool server. Retrying in 30 seconds...")
        time.sleep(30)
    time.sleep(0.025)
print("Logging in...")
soc.send(bytes("LOGI," + username + "," + password, encoding="utf8"))
while True:
    resp = soc.recv(1024).decode()
    if resp == "OK":
        print("Logged in!")
        break
    if resp == "NO":
        print("Error, closing in 5 seconds...")
        soc.close()
        time.sleep(5)
        sys.exit()
    time.sleep(0.025)

print("Start mining...")
signal.signal(signal.SIGINT, handler)
while True:
    soc.send(bytes("JOB", encoding="utf8"))
    while True:
        job = soc.recv(1024).decode()
        if job:
            break
        time.sleep(0.025)
    Timeelapsed = (time.time()-Time1)
    #print(Timeelapsed) Debug purposes only
    print("Recived new job from pool.")
    job = job.split(",")
    print("Recived new job from pool. Diff: " + job[2])
    for iJob in range(10000 * int(job[2]) + 1):
        hash = hashlib.sha3_512(str(job[0] + str(iJob)).encode("utf-8")).hexdigest()
        hash_count = hash_count + 1
        if job[1] == hash:
            soc.send(bytes(str(iJob)+","+str(last_hash_count)+","+str(round(Timeelapsed)), encoding="utf8"))
            while True:
                good = soc.recv(1024).decode()
                if good == "GOOD":
                    shares[0] = shares[0] + 1 # Share accepted
                    print("Share accepted " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), " + str(last_hash_count) + " H/s (Wrong Hashrate)")
                    break
                elif good == "BAD":
                    shares[1] = shares[1] + 1 # SHare rejected
                    print("Share rejected " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), " + str(last_hash_count) + " H/s (Wrong Hashrate)")
                    break
                time.sleep(0.025)
            break

