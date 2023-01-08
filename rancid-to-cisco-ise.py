import requests
import json

# Set the base URL for the RANCID server
rancid_server_url = "http://rancid.example.com"

# Set the credentials for the RANCID server
rancid_username = "rancid"
rancid_password = "password"

# Set the base URL for the Cisco ISE server
ise_server_url = "https://ise.example.com:9060"

# Set the credentials for the Cisco ISE server
ise_username = "ise-admin"
ise_password = "password"

# Function to retrieve the list of devices from RANCID
def get_rancid_devices():
    # Send a request to the RANCID server to get the list of devices
    response = requests.get(f"{rancid_server_url}/api/devices", auth=(rancid_username, rancid_password))

    # If the request was successful, return the list of devices
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Function to add a device to Cisco ISE
def add_ise_device(name, ip_address, device_type, tacacs_password):
    # Set the request headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Set the request payload
    payload = {
        "name": name,
        "description": "Added by RANCID sync script",
        "ipAddress": ip_address,
        "networkDeviceType": device_type,
        "tacacsProperties": {
            "password": tacacs_password
        }
    }

    # Send a request to the Cisco ISE server to add the device
    response = requests.post(f"{ise_server_url}/ers/config/networkdevice", auth=(ise_username, ise_password), headers=headers, json=payload)

    # Return the response status code
    return response.status_code

# Function to delete a device from Cisco ISE
def delete_ise_device(name):
    # Send a request to the Cisco ISE server to delete the device
    response = requests.delete(f"{ise_server_url}/ers/config/networkdevice/name/{name}", auth=(ise_username, ise_password))

    # Return the response status code
    return response.status_code

# Get the list of devices from RANCID
rancid_devices = get_rancid_devices()

# Get the list of devices from Cisco ISE
headers = {
    "Accept": "application/json"
}
response = requests.get(f"{ise_server_url}/ers/config/networkdevice", auth=(ise_username, ise_password), headers=headers)

if response.status_code == 200:
    ise_devices = response.json()
else:
    ise_devices = []

# Iterate through the list of devices in Cisco ISE
for ise_device in ise_devices:
    # Check if the device is in the list of devices from RANCID
    found = False
    for rancid_device in rancid_devices:
        if rancid_device["name"] == ise_device["name"]:
            found = True
            break
    if not found:
        # Device was not found in RANCID, so delete it from Cisco ISE
        status_code = delete_ise_device(ise_device["name"])
        if status_code == 200:
            print(f"Successfully deleted device {ise_device['name']} from Cisco ISE")
        else:
            print(f"Error deleting device {ise_device['name']} from Cisco ISE")

# Iterate through the list of devices from RANCID
for rancid_device in rancid_devices:
    # Check if the device is in the list of devices from Cisco ISE
    found = False
    for ise_device in ise_devices:
        if rancid_device["name"] == ise_device["name"]:
            found = True
            break
    if not found:
        # Device was not found in Cisco ISE, so add it
        status_code = add_ise_device(rancid_device["name"], rancid_device["ipAddress"], rancid_device["type"], rancid_device["tacacsPassword"])
        if status_code == 201:
            print(f"Successfully added device {rancid_device['name']} to Cisco ISE")
        else:
            print(f"Error adding device {rancid_device['name']} to Cisco ISE")
