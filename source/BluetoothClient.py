import bluetooth

class BluetoothClientSDP():
	
	def __init__(self, uuid):

		self.uuid = uuid
		self.connected = False

		matches = bluetooth.find_service(uuid=self.uuid)
		for match in matches :
			print(match)

		if len(matches) == 0:
			print("No services found")
			return

		# take the first match found - should be the only one!
		self.port = matches[0]["port"]
		self.name = matches[0]["name"]
		self.host = matches[0]["host"]

		try:
			self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			self.socket.connect((self.host, self.port))
		except bluetooth.BluetoothError:
			print("ERROR: could not connect to server")
			return

		self.connected = True

	def connect(self):
		"""attempts to connect the client to the address and port provided in init"""
		try:
			self.socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
			self.socket.connect((self.addr, self.port))
			self.connected = True
		except BluetoothError:
			print "bluetooth error!"
			self.connected = False

	def send_data(self, data):
		
		try:
			self.socket.send(data)
		except BluetoothError:
			print "bluetooth error while sending"
			return -1
			
		return 1
		
	def recieve_data(self):
		
		try:
			self.socket.recv(1024)
		except BluetoothError:
			print "bluetooth error while recieving"
			return -1
		
		return 1
