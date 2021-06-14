# minidiscord api

# imports
from pickle import loads, dump
from random import choice
from time import time

# log
def log(text):
    logmsg = f"[/] {text}"
    print(logmsg)
    with open("apilogs.txt", "a+") as file:
        file.write(logmsg+"\n")

# server management
class MiniDiscordServerManager:

    # global vars
    ALPHANUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    # ^^^ around 916 million combonations for 5 digit IDs

    # Establish Database Location
    def __init__(self):
        self.__opendb__()

    # open databse
    def __opendb__(self):
        # If exists, read and return
        try:
            with open(".minicorddb", "rb") as file:
                content = file.read()
            # Log and return
            return loads(content)          
        # Otherwise, make it and return empty
        except FileNotFoundError:
            with open(".minicorddb", "wb") as file:
                dump({}, file)
            # Log and return
            log("Created .minicorddb")
            return {}

    # write to database
    def __writedb__(self, data):
        # write this
        with open(".minicorddb", "wb+") as file:
            dump(data, file)

    # generate id
    def __generate_id__(self, compare_set):
        # generate id
        id_exists = True
        while id_exists:
            id = ""
            for x in range(0, 5):
                id += choice(MiniDiscordServerManager.ALPHANUMERIC)
            # check to see if ID exists
            try:
                compare_set[id]
            except KeyError:
                id_exists = False
        # when id is unique
        return id

    # create Server
    def __create_server__(self, creator_id, name):
        # Grab current servers
        db = self.__opendb__()
        # gen id
        id = self.__generate_id__(db)
        # create info abt server
        data = {
            "name":name,
            "created_at":str(time()),
            "owner":str(creator_id),
            "members":[creator_id],
            "verified":False,
            "messages":[{
                "id":self.__generate_id__({}),
                "text":"Welcome to your new server!",
                "sender":str(creator_id),
            }]
        }
        # update db
        db[id]=data
        # dump to file
        self.__writedb__(db)
        # log
        log(f"Added {name} ({id}) to database")
        # return id
        return id
    
    # delete server
    def __delete_server__(self, requester_id, server_id):
        # grab current servers
        db = self.__opendb__()
        # grab server by id and delete
        if server_id in list(db.keys()):
            if db[server_id]["owner"]==str(requester_id):
                log(f'Deleted {db[server_id]["name"]} ({server_id}) from the database.') # log
                del db[server_id] # delete
                self.__writedb__(db) # commit to database
                return True # return
            else:
                return False
        else:
            # if there was no servers
            return None
    
    # present server info
    def __server_info__(self, owner_id):
        # Grab current servers
        db = self.__opendb__()
        # grab every server by the owner
        owned = {}
        for id,data in db.items():
            # If is it owned
            if data["owner"] == str(owner_id):
                owned[id] = data
        # Else return data
        return owned

    # join/leave server
    def __server_attatchment__(self, member_id, server_id, join):
        # grab db
        db = self.__opendb__()
        # does server exist?
        try:
            db[server_id]
        except KeyError:
            return False
        # grab server and add / remove
        for id,data in db.items():
            # just to make sure that there will be no duplicates
            if join and (id==server_id) and (not str(member_id) in data["members"]):
                db[server_id]["members"].append(str(member_id))
                # log
                log(f"Added {member_id} to ({server_id})")
            # to remove
            elif (not join) and (id==server_id) and (str(member_id) in data["members"]):
                db[server_id]["members"].remove(str(member_id))
                # log
                log(f"Removed {member_id} from ({server_id})")
        # commit and close
        self.__writedb__(db)
        return True

    # servers
    def __servers__(self):
        # grab db
        db = self.__opendb__()
        return db

    # send message
    def __send_message__(self, member_id, server_id, message):
        # grab db
        db = self.__opendb__()
        # grab used ids
        previous_ids = {}
        for msg in db[server_id]["messages"]:
            previous_ids[msg['id']] = True
        # generate new id
        new_id = self.__generate_id__(previous_ids)
        db[server_id]["messages"].append({
                "id":new_id,
                "text":message,
                "sender":str(member_id),
        })
        # update db
        self.__writedb__(db)
        # return list of members to ping
        to_ping = []
        for member in db[server_id]['members']:
            # don't include self
            if member != member_id:
                to_ping.append(member)
        # log
            log(f"Sent \'{message}\' to ({server_id})")
        # return
        return to_ping