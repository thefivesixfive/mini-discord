# minidiscord api

# imports
from pickle import loads, dump
from random import choice
from time import time

# log
def log(text):
    logmsg = f"[/] {text}"
    print(logmsg)
    with open("logs.txt", "a+") as file:
        file.write(logmsg+"\n")

# server management
class MiniDiscordServerManager:

    # global vars
    ALPHANUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_"

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
            for x in range(0, 20):
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
            "messages":{
                "id":self.__generate_id__({}),
                "text":"Welcome to your new server!"
            }
        }
        # update db
        db[id]=data
        # dump to file
        self.__writedb__(db)
        # log
        log(f"Added {name} ({id}) to database")
    
    # delete server
    def __delete_server__(self, requester_id, server_id):
        # grab current servers
        db = self.__opendb__()
        # grab server by id and delete
        if (db[id]==server_id) and (db[id]["owner"]==str(server_id)):
            del db[id] # delete
            self.__writedb__(db) # commit to database
            log(f'Deleted {data["name"]} ({id}) from the database.') # log
            return True # return
        # if there was no servers
        return False
    
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

    # join server
    def __server_attatchment__(self, member_id, server_id, join):
        # grab db
        db = self.__opendb__()
        # grab server and add / remove
        for id,data in db.items():
            # just to make sure that there will be no duplicates
            if join and (id==server_id) and (not str(member_id) in data["members"]):
                db[server_id]["members"].append(str(member_id))
            # to remove
            elif (not join) and (id==server_id) and (str(member_id) in data["members"]):
                db[server_id]["members"].remove(str(member_id))
        # commit and close
        self.__writedb__(db)
        return True