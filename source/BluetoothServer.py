import bluetooth

class BluetoothServerSDP:

	def __init__(self, uuid, service_name):
		self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		self.port = bluetooth.PORT_ANY

		try:
			self.socket.bind(("", self.port))
		except bluetooth.BluetoothException:
			print("ERROR: server bind failed")
			return

		self.socket.listen(1)
	

		self.uuid = uuid  # arbitrary means of identifying the service
		bluetooth.advertise_service(self.socket, service_name,
										service_id = self.uuid,
										service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
										profiles=[bluetooth.SERIAL_PORT_PROFILE])
		
		print("port : {}".format(self.socket.getsockname()[1]))

		self.client_socket, self.address = self.socket.accept()
			
	def send_data(self, data):
			
		try:
			self.client_socket.send(data)
		except bluetooth.BluetoothError:
			print("ERROR: send failed")
			return -1

		return 1
				
	def recieve_data(self, recv_size):

		data=''
		while len(data) < recv_size:
			try:
				data += self.client_socket.recv(recv_size - len(data))
			except bluetooth.BluetoothError:
				print("ERROR: recieve failed")

		return data

	def close_socket(self):
		self.client_socket.close()
		self.socket.close()
