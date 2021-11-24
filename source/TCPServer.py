import socket


class TCPServer:

    def __init__(self, port, timeout=0.0):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = "10.9.39.193" # socket.gethostbyname(socket.gethostname())
        self.port = port
        self.timeout = timeout
        self.is_bound = False

        try:
            self.server.bind((self.ip, port))
            self.is_bound = True
        except (socket.error, socket.herror) as e:
            print("Error binding socket to given port and address")
            self.is_bound = False
            raise e

    def listen_for_client(self):

        assert self.is_bound

        try:
            self.server.listen(1)
            self.client, self.addr = self.server.accept()

        except (socket.error, socket.herror) as e:
            print("Error accepting connection")
            raise e
        except (socket.timeout) as e:
            print("Connection timeout")
            raise e

        # if no timeout argument is passed to init then the socket is made non-blocking
        self.client.settimeout(self.timeout)

    def receive(self, recv_size):
        try:
            data = self.client.recv(recv_size)
            return data
        except BlockingIOError:
            return


    def send(self, send_data):

        self.client.send(send_data)
