from django.shortcuts import render
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def get_results(request):
    uri = "mongodb+srv://merwin:AmmaMerwin@storage.mazbk2j.mongodb.net/?retryWrites=true&w=majority&appName=Storage"
    client = MongoClient(uri, server_api=ServerApi('1'))
    DB = client["NETMIKO"]
    myCol = DB["Results"]
    
    results = list(myCol.find({}))
    
    return render(request, "tables.html",{"results":results})
