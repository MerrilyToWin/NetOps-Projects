from netmiko import ConnectHandler
import pymongo
import datetime

# --- Device details ---
device = {
    "device_type": "cisco_ios",
    "host": "10.10.20.40",  # LAN switch IP
    "username": "admin",
    "password": "RG!_Yw200",
    "port": 22
}

# --- MongoDB setup ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ztp_project"]
collection = db["compliance_results"]

# --- Connect to switch ---
net_connect = ConnectHandler(**device)
output = net_connect.send_command("show running-config")

# --- Compliance checks ---
compliance = {
    "hostname": "LAN-SWITCH" in output,
    "snmp": "snmp-server community NETOPS RO" in output,
    "ntp": "ntp server 10.10.20.100" in output,
    "syslog": "logging host 10.10.20.101" in output,
    "vlans": "vlan 10" in output and "vlan 20" in output
}

# --- Record results ---
record = {
    "device": device["host"],
    "timestamp": datetime.datetime.now(),
    "compliance": compliance
}
collection.insert_one(record)

print("✅ Compliance check done and stored in MongoDB")
print(record)

# --- Optional: Email alert for non-compliance ---
issues = [k for k, v in compliance.items() if not v]
if issues:
    print(f"⚠️ Non-compliant settings found: {issues}")
    # Here you can call a send_alert() function
