from netmiko import ConnectHandler

sandbox = {
    "device_type": "cisco_xe",
    "host": "10.10.20.48",
    "username": "developer",
    "password": "C1sco12345",
    "port": 22,
}

net_connect = ConnectHandler(**sandbox)
output = net_connect.send_command("show ip int brief")
print(output)