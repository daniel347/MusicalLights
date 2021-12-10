import socket

class TCPClient:

    def __init__(self, addr, port, timeout=0.0):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr  # ip of the host conputer which the pi is connected to
        self.port = port

        self.is_connected = False

        try:
            self.client_sock.connect((self.addr, self.port))
            self.is_connected = True
        except (socket.error, socket.herror) as e:
            print("Error connecting to server")
            raise e
        except (socket.timeout) as e:
            print("Connection timeout")
            raise e

        # if no timeout argument is passed to init then the socket is made non-blocking
        self.client_sock.settimeout(timeout)

    def receive(self, recv_size):

        data = self.client_sock.recv(recv_size)
        return data

    def send(self, send_data):

        self.client_sock.send(send_data)

    def close(self):
        self.client_sock.close()
