from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://merwin:<password>@storage.mazbk2j.mongodb.net/?retryWrites=true&w=majority&appName=Storage"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
DB = client["NETMIKO"]
myCol = DB["Storage"]
myCol1 = DB["Configs"]

data = {
    "hostname": "csr1",
    "ip": "10.10.20.48",
    "vendor": "cisco_ios",
    "username": "developer",
    "password": "C1sco12345"
}

config_data = {
  "hostname": "csr1",
  "timestamp": "2025-08-27T19:20:00Z",
  "config_text": "This is a placeholder config until we fetch the real one."
}

query = {
    "vendor": "cisco_ios"
}

update_data = {
    "$set":{
        "vendor": "cisco_xe",
    }
}
myCol.update_one(query,update_data)
# myCol1.insert_one(config_data)


