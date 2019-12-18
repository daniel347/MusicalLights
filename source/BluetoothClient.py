import bluetooth

class BluetoothClientSDP():
	
	def __init__(self, uuid):

		self.uuid = uuid
		self.found_service = True
		self.connected = False

		if (self.find_services() == -1):
			return
		else
			self.connect()

	def find_services(self):
		try:
			matches = bluetooth.find_service(uuid=self.uuid)
		except bluetooth.BluetoothError:
			print("ERROR: could not search services")
			self.found_service = False
			return -1

		for match in matches:
			print(match)

		if len(matches) == 0:
			self.found_service = False
			print("No services found")
			return -1

		# take the first match found - should be the only one!
		self.port = matches[0]["port"]
		self.name = matches[0]["name"]
		self.host = matches[0]["host"

		self.found_service = True

		return 0

	def connect(self):
		"""attempts to connect the client to the address and port setup in init"""
		try:
			self.socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
			self.socket.connect((self.addr, self.port))
			self.connected = True
		except BluetoothError:
			print("ERROR: Failed to connect socket")
			self.connected = False
			return -1

		return 0

	def send_data(self, data):
		
		try:
			self.socket.send(data)
		except BluetoothError:
			print("ERROR: could not send data")
			return -1
			
		return 1
		
	def recieve_data(self):
		
		try:
			self.socket.recv(1024)
		except BluetoothError:
			print("ERROR: could not recieve")
			return -1
		
		return 1
