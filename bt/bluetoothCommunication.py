################################################################################
# Program Description
################################################################################
#
#   Purpose: Blutooth wrapper for team grapefruit project
#   Written By: Niklas Wilson
#   NOTE:
#         Core communication line is done, this is more a proof of concept
#         Code will need to be revised for final question/answer stuff
#         This Simple Demonstrates the ability to
#         - Connect to other PI
#         - Verify Connection, to prevent communication hijacking
#         - CLIENT: Ask for a question, or provide answer to question
#         - HOST: Send a question or receive an answer to a question
#
#   Installation:
#   1) sudo apt-get install bluetooth libbluetooth-dev python-dev python-pip
#   2) sudo pip install pybluez
#
#   Extended Installation for Server:
#   3) sudo nano /etc/systemd/system/dbus-org.bluez.service
#   4) Add ' --compat' to 'ExecStart=/usr/lib/bluetooth/bluetoothd'
#   5) sudo systemctl daemon-reload
#   6) sudo systemctl restart bluetooth
#   7) sudo chmod 777 /var/run/sdp
#   8) sudo hciconfig hci0 piscan

################################################################################
# Library Imports
################################################################################
# General libraries 
from sys import exit

# Logging Control
import logging

# Blutooth library
try: import bluetooth
#except Exception,e: #syntax not supported by python 3
except:
    logging.critical("Read Installation Instructions!"); exit(1)
	
################################################################################
# SETTINGS
################################################################################
host_uuid="1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
host_name="MainBoard"
host_verification="grapefruit_host"
client_verification="grapefruit_client"

################################################################################
# Bluetooth Utility Functions
################################################################################
# returns array of devices [{name,address}]
def getNearbyBlutoothDevices():
	devices=[]; nearby_devices=bluetooth.discover_devices()
	for bdaddr in nearby_devices:
		devices.append({
			"name":bluetooth.lookup_name( bdaddr ),
			"address":bdaddr
		})
	return devices

################################################################################
# Bluetooth Server/Host Functions
################################################################################
def hostCommunicate(openSocket):
	# Validate Client
	recvData = openSocket.recv(1024).strip()
	logging.debug(recvData)
	if client_verification not in recvData: 
		logging.critical("Client Failed validation")
		openSocket.send("Invalid Client"); return
	# Send back server validation
	openSocket.send(host_verification)
	# Wait for command
	recvData = openSocket.recv(1024).strip()
	logging.debug(recvData)
	if "getQuestion" in recvData: 
		# TODO: Get a question from a function and send it here
		openSocket.send("What is a cow?, mammal, reptile, planet, fish")
	elif "haveAnswer" in recvData:
		openSocket.send("ok")
		recvData = openSocket.recv(1024).strip()
		logging.debug(recvData)
		# TODO: Do something with the resulting answer
	
def host():
	# Server Setup
	server_sock=bluetooth.BluetoothSocket( bluetooth.L2CAP )
	server_sock.bind(("",0)); server_sock.listen(1)
	bluetooth.advertise_service( server_sock, host_name, host_uuid )
	
	# Listen for connections
	while True:
		logging.debug("Waiting For Connection")
		client_sock,address = server_sock.accept()
		
		# Communicate with client
		hostCommunicate(client_sock)
		client_sock.close()
		
	# Stop Listening
	server_sock.close()

################################################################################
# Bluetooth Client Functions
################################################################################
def clientCommunicate(openSocket):
	# Send Client Validation
	openSocket.send(client_verification)
	
	# Validate Server
	recvData = openSocket.recv(1024).strip()
	logging.debug(recvData)
	if host_verification not in recvData: 
		logging.critical("Host Failed validation")
		openSocket.send("Invalid Host"); return
		
	# Ask For Question
	openSocket.send("getQuestion")
	recvData = openSocket.recv(1024).strip()
	logging.debug(recvData)
	
	# TODO: Implement the returned question/answers
	# TODO: Send an answer when provided
	
def client():
	logging.info("Looking for host")
	while True:
		service_matches = bluetooth.find_service( uuid = host_uuid )
		if len(service_matches) == 0: 
			logging.warning("Host not found, retrying"); continue

		# Connection Details
		first_match = service_matches[0]
		port = first_match["port"]
		name = first_match["name"]
		host = first_match["host"]

		# Communicate with host
		sock=bluetooth.BluetoothSocket( bluetooth.L2CAP )
		sock.connect((host, port))
		clientCommunicate(sock)
		sock.close()

################################################################################
# Main Program
################################################################################
if __name__ == "__main__":
	# Logging/Debug Setting
	logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s [%(levelname)-8s]: %(message)s', datefmt='%H:%M:%S')
	logging.info("put client() or server() in main or import this script instead")


